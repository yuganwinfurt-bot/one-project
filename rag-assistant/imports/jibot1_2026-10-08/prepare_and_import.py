"""通过已有 RAG API 导入本次 Jibot1 资料；同名同内容文件跳过，避免重复入库。"""
from pathlib import Path
import hashlib
import json
import shutil
import sqlite3
import time

import httpx

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）")
PICTURES = Path(r"E:\BaiduNetdiskDownload\001-智能机械臂-Jibot1（25年）")
KB = "f75567ffdb404490bda53d8820cedfa8"
API = "http://127.0.0.1:8000"
DB = ROOT.parents[1] / "backend/storage/assistant.sqlite3"
PREPARED = ROOT / "prepared"
ORIGINALS = ROOT / "originals"
PREPARED.mkdir(exist_ok=True)
ORIGINALS.mkdir(exist_ok=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def existing_same(filename, path, knowledge_base_id=KB):
    with sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True) as db:
        rows = db.execute("SELECT id, filename, stored_path, chunk_count FROM documents WHERE knowledge_base_id=? AND filename=?", (knowledge_base_id, filename)).fetchall()
    for row in rows:
        stored = Path(row[2])
        if stored.exists() and digest(stored) == digest(path):
            return {"id": row[0], "filename": row[1], "chunk_count": row[3], "already_present": True}
    if rows:
        raise RuntimeError(f"已有同名但内容不同的文档，需人工核对：{filename}")
    return None


def upload(path, source=None, knowledge_base_id=KB):
    filename = path.name
    result = existing_same(filename, path, knowledge_base_id)
    if not result:
        with httpx.Client(timeout=600, trust_env=False) as client, path.open("rb") as stream:
            response = client.post(f"{API}/api/knowledge-bases/{knowledge_base_id}/documents", files=[("files", (filename, stream, "application/octet-stream"))])
            if not response.is_success:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
            result = response.json()["uploaded"][0]
    result.update(source=str(source or path), prepared_path=str(path), sha256=digest(path), knowledge_base_id=knowledge_base_id)
    with (ROOT / "import_results.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(result, ensure_ascii=False) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


def guide(model, suction):
    source_name = "气泵机械臂-快速入门.jpg" if suction else "六轴机械臂J1-快速入门.jpg"
    src = PICTURES / source_name
    shutil.copy2(src, ORIGINALS / source_name)
    title = f"{model}快速上手指南"
    source = f"来源：{src}（单页原图，文字及按键表转录）。\n"
    def section(name, body):
        return f"## {model}：{name}\n{source}{body.strip()}\n"
    sections = [section("上电及开机成功标志", """
1. 将电源适配器插到电源插座上。
2. 电源适配器连接机械臂控制板上的适配器对接线。
3. 先将机械臂扶至大概直立的状态，然后打开控制板电源开关。
4. 听到嘀嘀嘀响三声代表开机成功。
原图标出了控制板的电源开关和连接电源适配器的接头。本指南没有标明适配器电压、电流，不应据此推断供电参数。
"""), section("PS2 手柄配对、红灯模式及控制模式切换", """
1. 将 2 节 7 号电池装到 PS2 手柄中。
2. 将手柄开关拨到 ON。手柄和接收器上的指示灯闪烁表示等待配对；配对成功后指示灯长亮。
3. 用 MODE 键切换至红灯模式；原图特别说明：红绿灯都亮即为红灯模式。
4. 完成上述步骤后即可用手柄控制机械臂。
5. SELECT 键在手动操作模式和自动夹取模式之间切换。MODE 切换红绿灯模式，SELECT 切换操作模式，二者功能不同。
手柄图标出了方向键上、下、左、右，SELECT、START、MODE、L1、L2、R1、R2、左右摇杆，以及三角形、叉号、方形、圆形按键；本指南没有提供摇杆的动作映射。
""")]
    end = "吸盘" if suction else "爪子"
    release, grip = ("吸盘松开", "吸盘吸取") if suction else ("爪子张开", "爪子闭合")
    sections.append(section("手动操作模式完整按键表", f"""
SELECT 切换模式；手动模式下，按键按下时对应关节动，松开时停止。
| 按键 | 功能 |
| --- | --- |
| SELECT | 模式切换 |
| START | 直立 |
| 上 | 1号舵机前 |
| 下 | 1号舵机后 |
| 左 | 云台左转 |
| 右 | 云台右转 |
| 三角形 △ | 2号舵机前 |
| 叉号 × | 2号舵机后 |
| 方形 □ | 3号舵机前 |
| 圆形 ○ | 3号舵机后 |
| L1 | {end}左转 |
| R1 | {end}右转 |
| L2 | {release} |
| R2 | {grip} |
"""))
    sections.append(section("自动夹取模式完整按键表", """
SELECT 切换至自动夹取模式。原图自动夹取表中：
| 按键 | 功能 |
| --- | --- |
| SELECT | 模式切换 |
| START | 直立 |
| 上 | 前抓 |
| 下 | 蜷缩 |
| 左 | 左抓 |
| 右 | 右抓 |
| 三角形 △ | 前放 |
| 叉号 × | 蜷缩 |
| 方形 □ | 左放 |
| 圆形 ○ | 右放 |
自动夹取模式表没有列出 L1、L2、R1、R2 的功能，不从手动模式表推断。
"""))
    sections.append(section("到货检查、休眠唤醒及资料入口", """
产品拿到手先试上电、配对和上述控制功能，保证硬件到手完好后再继续使用；有问题立即联系客服处理。
手柄开机状态下长时间未操作会自动休眠，可以通过 START 键或 MODE 键激活。
原图底部有产品资料二维码和售后二维码，售后标注为“明明同学（客户经理）”。二维码网址未解码，应查看保存的原始图片扫码。
"""))
    path = PREPARED / f"{title}（图片转录）.md"
    path.write_text("\n".join(sections), encoding="utf-8")
    return path, src


def prepare():
    pairs = [guide("六轴机械臂J1（爪子版）", False), guide("气泵机械臂（吸盘版）", True)]
    src = SOURCE / "资料导读.txt"
    text = src.read_bytes().decode("utf-8-sig")
    path = PREPARED / "Jibot1资料导读（原文及版本说明）.md"
    path.write_text(f"# Jibot1 资料导读\n\n原始文件：{src}\n\n整理说明：该文件所在目录名称为 STM32，但原文的 1.3、1.8、1.9、1.11、1.12、1.13 标题写为 ESP32。以下保留原文；具体平台以对应教程 PDF 标题和正文为准。此文件只是资料目录，不能替代教程正文，也不能证明所列源码或工具已下载。\n\n## 原文\n\n{text}", encoding="utf-8")
    shutil.copy2(src, ORIGINALS / "资料导读.txt")
    pairs.append((path, src))
    for src in sorted(SOURCE.rglob("*.pptx")):
        shutil.copy2(src, ORIGINALS / src.name)
    return pairs


def main():
    prepared = prepare()
    for path in sorted(SOURCE.rglob("*.pdf")):
        upload(path)
    for path, src in prepared:
        upload(path, src)


if __name__ == "__main__":
    main()
