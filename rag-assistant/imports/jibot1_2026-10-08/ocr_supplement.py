"""提取 PDF 内嵌图片文字，保留页码、原图及识别结果，供索引补充。"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import re
import time

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）")
CACHE = ROOT / "ocr_cache"
CACHE.mkdir(exist_ok=True)
ENGINE = None


def init_worker():
    global ENGINE
    from rapidocr import RapidOCR
    ENGINE = RapidOCR(params={
        "Global.font_path": r"C:\Windows\Fonts\msyh.ttc",
        "Global.log_level": "error",
        "Global.max_side_len": 1800,
        "EngineConfig.onnxruntime.intra_op_num_threads": 1,
        "EngineConfig.onnxruntime.inter_op_num_threads": 1,
    })


def process_image(path):
    path = Path(path)
    target = path.with_suffix(".json")
    if target.exists():
        return json.loads(target.read_text(encoding="utf-8"))
    result = ENGINE(str(path))
    rows = []
    if result.txts:
        for text, score, box in zip(result.txts, result.scores, result.boxes):
            rows.append({"text": str(text), "score": float(score), "box": box.tolist()})
    record = {"image": str(path), "rows": rows}
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def main():
    images = {}
    for path in sorted(SOURCE.rglob("*.pdf")):
        for number, page in enumerate(PdfReader(path).pages, 1):
            for item in page.images:
                img = item.image.convert("RGB")
                if img.width < 120 or img.height < 45 or img.width * img.height < 12000:
                    continue
                key = hashlib.sha256(img.tobytes()).hexdigest()
                output = CACHE / f"{key}.png"
                if not output.exists():
                    img.save(output)
                images.setdefault(key, {"path": str(output), "sources": []})["sources"].append({"file": str(path), "page": number, "image_name": item.name})
    (ROOT / "image_manifest.json").write_text(json.dumps(images, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"unique_images": len(images)}, ensure_ascii=False), flush=True)
    done = 0
    failures = []
    with ProcessPoolExecutor(max_workers=3, initializer=init_worker) as pool:
        jobs = {pool.submit(process_image, item["path"]): key for key, item in images.items()}
        for future in as_completed(jobs):
            done += 1
            try:
                record = future.result()
                images[jobs[future]]["ocr"] = record
            except Exception as exc:
                failures.append({"key": jobs[future], "error": str(exc)})
            if done % 10 == 0 or done == len(jobs):
                print(json.dumps({"ocr_done": done, "total": len(jobs), "failed": len(failures)}), flush=True)
    documents = {}
    for key, image in images.items():
        rows = image.get("ocr", {}).get("rows", [])
        lines = [row["text"].strip() for row in rows if row["score"] >= 0.75 and not re.fullmatch(r"[\d\W_]+", row["text"].strip())]
        text = "\n".join(lines)
        if len(text) < 15:
            continue
        for src in image["sources"]:
            body = f"## 原文第 {src['page']} 页，图片 {src['image_name']}\n原始文件：{src['file']}\n识别方式：本机 RapidOCR；以下为图片文字检索辅助，代码符号、数字和接线对应可能存在识别错误，使用时请核对原 PDF 页和截图。\n\n{text}\n"
            documents.setdefault(src["file"], []).append((src["page"], body))
    outputs = []
    for source, sections in documents.items():
        output = ROOT / "prepared" / (Path(source).stem + "（截图OCR补充）.md")
        output.write_text("\n".join(body for _, body in sorted(sections, key=lambda item: item[0])), encoding="utf-8")
        outputs.append({"path": str(output), "source": source, "sections": len(sections)})
    report = {"images": len(images), "failures": failures, "outputs": outputs}
    (ROOT / "ocr_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"outputs": len(outputs), "failures": failures}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
