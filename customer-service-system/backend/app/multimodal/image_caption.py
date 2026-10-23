"""图片描述（lesson-11 多模态）。

链路：评价晒图（本地文件）→ 大模型视觉能力 → 一段中文描述 → 拼进 Chroma 文档。

教学重点：
- 传图用 OpenAI 兼容的 Chat Completions vision 写法：content 里放
  {"type": "text", ...} + {"type": "image_url", "image_url": {"url": data_url}}，
  图片以 base64 data URL 内联，不依赖公网图床 / Docker / 海外服务
- 模型走现有 .env 的 LLM_* 配置（默认 qwen3.7-flash，需确认模型支持视觉；
  不支持时会直接报错，不要静默吞掉）
"""

import base64
from pathlib import Path

from openai import APITimeoutError, APIError

from app.common.exceptions import BusinessException
from app.config import UPLOAD_DIR, settings
from app.utils.llm import get_llm_client

# 视觉接口支持的图片后缀（与 OpenAI vision 文档一致：png / jpeg / webp / 非动画 gif）
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# data URL 的 MIME 映射（jpg 按惯例用 image/jpeg）
_IMAGE_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

CAPTION_SYSTEM_PROMPT = """
你是电商评价分析助手。请用简洁中文描述这张买家晒图，只说画面里能看到的内容，
重点关注：拍的是什么商品、有无可见缺陷（开胶、破损、划痕、裂纹、污渍、变形等）、
颜色外观、包装状态。不要猜测画面之外的信息，不要输出多余解释。
""".strip()


def resolve_image_path(image_path: str) -> Path | None:
    """把评价里存的图片路径解析成磁盘文件；不存在则返回 None。

    支持两种写法：
    - /uploads/xxx.jpg：站内 URL 前缀，对应 backend/uploads/ 下的文件
    - 磁盘绝对路径：主要给单测 / 脚本直接传文件用
    """
    if not image_path or not str(image_path).strip():
        return None
    text = str(image_path).strip()
    if text.startswith("/uploads/"):
        candidate = UPLOAD_DIR / text[len("/uploads/"):]
    else:
        candidate = Path(text)
    if not candidate.is_file():
        return None
    return candidate


def caption_image(image_path: str | Path, max_chars: int = 300) -> str:
    """输入一张本地图片，返回中文内容描述（失败抛业务异常，不静默吞错）。"""
    file = resolve_image_path(str(image_path)) if isinstance(image_path, str) else image_path
    if isinstance(image_path, Path):
        file = image_path if image_path.is_file() else None
    if file is None:
        raise BusinessException(message=f"图片不存在：{image_path}")

    ext = file.suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise BusinessException(message=f"不支持的图片格式：{ext}，仅支持 png/jpg/webp/gif")

    raw = file.read_bytes()
    if not raw:
        raise BusinessException(message=f"图片文件为空：{file.name}")
    data_url = f"data:{_IMAGE_MIME[ext]};base64," + base64.b64encode(raw).decode("ascii")

    client = get_llm_client()
    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": CAPTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请描述这张买家晒图的内容。"},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            temperature=0,
        )
    except APITimeoutError as exc:
        raise BusinessException(message="图片描述调用超时，请稍后重试") from exc
    except APIError as exc:
        raise BusinessException(message=f"图片描述调用失败：{exc.message}") from exc

    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise BusinessException(message="图片描述返回空内容（模型可能不支持视觉输入）")
    return content[:max_chars] if len(content) > max_chars else content
