"""只读资料及压缩包：提取文档与项目源码，生成有来源和行号的 RAG 文本。"""
from pathlib import Path
from collections import defaultdict
import hashlib
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET

from prepare_and_import import ROOT, SOURCE, PREPARED, KB

EXTRACTED = ROOT / "extracted"
EXTRACTED.mkdir(exist_ok=True)
REF_KB = "c0077d246def4753bc5465e919510b52"
CODE_EXT = {".c", ".h", ".cpp", ".cc", ".py", ".ino", ".mix", ".pro", ".ui"}
DOC_EXT = {".pdf", ".docx", ".doc", ".md", ".txt", ".pptx"}
VENDOR = {"cmsis", "libraries", "build", "managed_components", "components", ".git", "node_modules", "obj", "objs", "objects", "output", "outputs", "third_party", "third-party"}
records = []
codes = {}
documents = {}
queue = []


def decode(data):
    encodings = ["utf-16", "utf-8-sig", "gb18030"] if data.startswith((b"\xff\xfe", b"\xfe\xff")) else ["utf-8-sig", "gb18030"]
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeError:
            continue
    raise UnicodeError("文本编码未识别")


def zip_name(info):
    if not info.flag_bits & 0x800:
        try:
            return info.filename.encode("cp437").decode("gbk")
        except UnicodeError:
            pass
    return info.filename


def category(source):
    return REF_KB if "005-拓展资料" in source and "01-技术文档" in source and "舵机知识" not in source else KB


def consume(data, name, source, group):
    suffix = Path(name).suffix.lower()
    key = hashlib.sha256(data).hexdigest()
    entry = {"source": source, "name": name, "group": group, "bytes": len(data), "sha256": key}
    records.append(entry)
    if suffix in CODE_EXT:
        try:
            text = decode(data)
        except UnicodeError:
            entry["status"] = "编码不明，未索引"
            return
        if len(re.findall(r"0x[0-9a-fA-F]+", text)) > 500 and Path(name).name.lower() in {"tb_table.h", "z_codetab.h", "font.h", "font8.h", "font16.h"}:
            entry["status"] = "字模或大数组资源，仅保留目录"
            return
        entry["status"] = "源码（相同内容合并）"
        if key not in codes:
            codes[key] = {"text": text, "group": group, "aliases": [], "name": name}
        codes[key]["aliases"].append(source)
        return
    if suffix not in DOC_EXT:
        entry["status"] = "二进制或媒体文件，仅保留目录"
        return
    if Path(name).name.lower() in {"programlogs.txt", "license.doc", "license.txt", "copying.txt"}:
        entry["status"] = "运行日志或依赖许可，仅保留目录"
        return
    kb = category(source)
    doc_key = (key, suffix, kb)
    if doc_key in documents:
        entry["status"] = "重复文档"
        entry["canonical"] = documents[doc_key]["source"]
        return
    basename = re.sub(r'[<>:"/\\|?*]', '_', Path(name).name)
    path = EXTRACTED / f"{key[:10]}_{basename}"
    path.write_bytes(data)
    entry["extracted_path"] = str(path)
    documents[doc_key] = entry
    if suffix == ".doc":
        entry["status"] = "等待旧版Word文字提取"
        return
    if suffix == ".pptx":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            sections = []
            slides = sorted([n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)], key=lambda n:int(re.search(r"slide(\d+)",n).group(1)))
            for num, slide in enumerate(slides,1):
                root = ET.fromstring(z.read(slide))
                paragraphs = ["".join(t.text or "" for t in p.iter() if t.tag.endswith("}t")) for p in root.iter() if p.tag.endswith("}p")]
                sections.append(f"## {basename} 第{num}页\n原始来源：{source}\n" + "\n".join(paragraphs))
        output = PREPARED / (f"{Path(basename).stem}（PPT文字提取）.md")
        output.write_text("\n\n".join(sections), encoding="utf-8")
        # 两份快速上手与人工核对的图片转录重复，已有文字和表格。
        if "快速上手" in basename:
            entry["status"] = "已由同版图片转录覆盖"
            return
        path = output
    elif suffix in {".txt", ".md"}:
        try:
            body = decode(data)
        except UnicodeError:
            entry["status"] = "编码不明，未索引"
            return
        if not body.strip():
            body = f"原始文件为空，说明仅在文件名中：{basename}"
        path = PREPARED / f"附带说明_{key[:8]}_{Path(basename).stem}.md"
        path.write_text(f"# {basename}\n\n原始来源：{source}\n\n{body}", encoding="utf-8")
    entry["status"] = "待导入文档"
    queue.append({"path":str(path), "source":source, "knowledge_base_id":kb})


def archive(blob, source, group, depth=0):
    with zipfile.ZipFile(blob) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            name = zip_name(item).replace("\\", "/")
            parts = set(name.lower().split("/"))
            full = source + "!/" + name
            ext = Path(name).suffix.lower()
            reason = None
            if parts & VENDOR:
                reason = "第三方依赖或编译产物，仅保留目录"
            elif "ST3.5.0官方标准库" in source and ext in CODE_EXT | {".txt", ".md"}:
                reason = "通用库示例，配套手册已纳入文档队列"
            elif "ZL_AI_ZHIKONG" in source and "/boards/" in name:
                board = name.split("/boards/",1)[1].split("/",1)[0]
                if board not in {"common", "zl-ai-zhikong-wifi", "zl-ai-zhikong-4g"}:
                    reason = "其他硬件板型，当前资料工程配置为 ZL_AI_ZHIKONG_WIFI"
            if reason or ext not in CODE_EXT | DOC_EXT | {".zip"}:
                records.append({"source":full,"bytes":item.file_size,"status":reason or "二进制或媒体文件，仅保留目录"})
                continue
            if item.file_size > 100_000_000:
                records.append({"source":full,"bytes":item.file_size,"status":"超大嵌套成员，未自动展开"})
                continue
            data = z.read(item)
            if ext == ".zip":
                if depth < 2:
                    archive(io.BytesIO(data), full, group, depth+1)
                else:
                    records.append({"source":full,"status":"嵌套超过3层，未展开"})
            else:
                consume(data, name, full, group)


def code_blocks(item):
    lines = item["text"].splitlines()
    source = item["aliases"][0]
    short_source = source.replace(str(SOURCE) + "\\", "")
    function = "文件开头/全局定义"
    start = 1
    current = []
    size = 0
    blocks = []
    pattern = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(|^\s*(?:static\s+|inline\s+|const\s+|unsigned\s+|signed\s+)*(?:[\w:*<>]+\s+)+([\w:~]+)\s*\([^;]*\)\s*(?:\{|$)")
    def flush():
        if current:
            end = start + len(current) - 1
            context = f"## {Path(item['name']).name} | {function} | 原文件第{start}-{end}行\n来源：{short_source}\n以下为原始源码，不是截图OCR。\n"
            blocks.append(context + "```\n" + "\n".join(f"{start+i}: {v}" for i,v in enumerate(current)) + "\n```\n")
    for num, line in enumerate(lines,1):
        match = pattern.match(line)
        if match and current:
            flush(); current=[]; size=0; start=num
        if match:
            function=next(g for g in match.groups() if g)
        if current and size+len(line)+len(str(num))+3 > 440:
            flush(); current=[]; size=0; start=num
        if not current:
            start=num
        current.append(line)
        size += len(line)+len(str(num))+3
    flush()
    return blocks


def main():
    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower()==".zip":
            archive(path, str(path), path.stem)
        elif path.suffix.lower() in CODE_EXT | DOC_EXT:
            # 原始PDF和资料导读已有独立导入；此处避免再生成副本。
            if path.suffix.lower()==".pdf" or path == SOURCE/"资料导读.txt":
                continue
            consume(path.read_bytes(), path.name, str(path), path.parent.name)
        else:
            records.append({"source":str(path),"bytes":path.stat().st_size,"status":"媒体/二进制文件，仅保留目录"})
    groups=defaultdict(list)
    for key,item in codes.items():
        groups[item["group"]].append((key,item))
    for group,items in groups.items():
        output=PREPARED/f"Jibot1源码_{group}.md"
        text=[]
        for key,item in items:
            text.extend(code_blocks(item))
        output.write_text("\n".join(text),encoding="utf-8")
        queue.append({"path":str(output),"source":group,"knowledge_base_id":category(items[0][1]["aliases"][0])})
    code_index=[]
    for key,item in codes.items():
        code_index.append({"sha256":key,"name":item["name"],"group":item["group"],"aliases":item["aliases"],"lines":len(item["text"].splitlines())})
    (ROOT/'code_manifest.json').write_text(json.dumps(code_index,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'archive_members.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'archive_import_queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'unique_code_files':len(codes),'code_groups':len(groups),'document_queue':len(queue),'legacy_docs':[r for r in records if r.get('status')=='等待旧版Word文字提取']},ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
