"""Extract bounded text from a chat attachment without storing the original file."""

from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException

MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024
MAX_ATTACHMENT_TEXT = 16000
TEXT_SUFFIXES = {
    ".txt", ".md", ".csv", ".json", ".log", ".py", ".js", ".jsx",
    ".ts", ".tsx", ".html", ".css", ".xml", ".yaml", ".yml", ".toml", ".sh",
}
DOCUMENT_SUFFIXES = TEXT_SUFFIXES | {".pdf", ".docx"}


def extract_attachment_text(filename: str, data: bytes) -> dict:
    """Return text for one supported document; reject empty or unreadable files."""
    name = filename.replace("\\", "/").split("/")[-1].strip()
    suffix = Path(name).suffix.lower()
    if not name or len(name) > 255 or suffix not in DOCUMENT_SUFFIXES:
        raise HTTPException(415, "仅支持 PDF、DOCX 和常见文本/代码文件")
    if not data:
        raise HTTPException(400, "文件为空")
    if len(data) > MAX_ATTACHMENT_BYTES:
        raise HTTPException(413, "单个文件不能超过 8 MB")

    pages_truncated = False
    try:
        if suffix in TEXT_SUFFIXES:
            try:
                content = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                content = data.decode("gb18030")
        elif suffix == ".docx":
            with ZipFile(BytesIO(data)) as package:
                info = package.getinfo("word/document.xml")
                if info.file_size > 4 * 1024 * 1024:
                    raise HTTPException(413, "DOCX 文本内容过大")
                xml = package.read(info)
            root = ElementTree.fromstring(xml)
            ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paragraphs = []
            for paragraph in root.iter(f"{ns}p"):
                line = "".join(node.text or "" for node in paragraph.iter(f"{ns}t"))
                if line.strip():
                    paragraphs.append(line)
            content = "\n".join(paragraphs)
        else:
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise HTTPException(503, "PDF 解析依赖尚未安装，请更新 Agent 依赖") from exc
            reader = PdfReader(BytesIO(data), strict=False)
            if reader.is_encrypted:
                raise HTTPException(422, "加密 PDF 无法读取，请先解密")
            pages = []
            pages_truncated = len(reader.pages) > 30
            for page_index in range(min(len(reader.pages), 30)):
                pages.append(reader.pages[page_index].extract_text() or "")
                if sum(map(len, pages)) > MAX_ATTACHMENT_TEXT:
                    break
            content = "\n\n".join(pages)
    except HTTPException:
        raise
    except (BadZipFile, KeyError, ValueError, UnicodeError, ElementTree.ParseError, OSError) as exc:
        raise HTTPException(422, "文件无法解析，请检查格式是否正确") from exc
    except Exception as exc:
        # pypdf raises several parser-specific exceptions for malformed PDFs.
        raise HTTPException(422, "文件无法解析，请检查格式是否正确") from exc

    content = content.replace("\x00", "").strip()
    if not content:
        raise HTTPException(422, "未提取到文字；扫描版 PDF 请先进行 OCR")
    truncated = pages_truncated or len(content) > MAX_ATTACHMENT_TEXT
    return {"name": name, "text": content[:MAX_ATTACHMENT_TEXT], "truncated": truncated}
