"""核对本次导入的数据库、向量分片及来源，生成交付清单。"""
from pathlib import Path
from collections import Counter, defaultdict
import json
import sqlite3
import sys

import httpx

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT/'backend'))
from app.rag.pipeline import get_vector_store


def main():
    entries={}
    all_aliases=defaultdict(set)
    for line in (ROOT/'import_results.jsonl').read_text(encoding='utf-8').splitlines():
        record=json.loads(line)
        entries[record['id']]=record
        all_aliases[record['id']].add(record['source'])
    with sqlite3.connect(PROJECT/'backend/storage/assistant.sqlite3') as db:
        db.row_factory=sqlite3.Row
        rows=[dict(x) for x in db.execute('SELECT * FROM documents')]
        names={x['id']:x['name'] for x in db.execute('SELECT * FROM knowledge_bases')}
    existing={x['id']:x for x in rows}
    imported=[x for x in rows if x['id'] in entries]
    groups=defaultdict(list)
    for record in imported:groups[record['knowledge_base_id']].append(record)
    checks=[]
    orphan_candidates=[]
    known_filenames={x['filename'] for x in entries.values()}
    for kb,records in groups.items():
        store=get_vector_store(kb)
        vectors=store.get(include=['metadatas'])
        vectors_by_id=dict(zip(vectors['ids'],vectors['metadatas']))
        for doc in records:
            ids=json.loads(doc['vector_ids'])
            missing=[value for value in ids if value not in vectors_by_id]
            wrong=[value for value in ids if value in vectors_by_id and vectors_by_id[value].get('document_id')!=doc['id']]
            checks.append({'document_id':doc['id'],'filename':doc['filename'],'expected_chunks':doc['chunk_count'],'actual_listed_chunks':len(ids),'missing':missing,'wrong_document':wrong})
        for vector_id,metadata in vectors_by_id.items():
            if metadata.get('document_id') not in existing and metadata.get('filename') in known_filenames:
                orphan_candidates.append({'knowledge_base_id':kb,'vector_id':vector_id,'metadata':metadata})
    (ROOT/'orphan_candidates.json').write_text(json.dumps(orphan_candidates,ensure_ascii=False,indent=2),encoding='utf-8')
    problems=[x for x in checks if x['missing'] or x['wrong_document'] or x['expected_chunks']!=x['actual_listed_chunks']]
    (ROOT/'integrity_check.json').write_text(json.dumps({'checked_documents':len(checks),'problems':problems,'orphan_candidates':len(orphan_candidates)},ensure_ascii=False,indent=2),encoding='utf-8')
    stats=[]
    for kb,records in groups.items():
        stats.append({'knowledge_base':names[kb],'knowledge_base_id':kb,'new_documents':len(records),'new_chunks':sum(x['chunk_count'] for x in records)})
    summary={'source_directory':r'E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）','knowledge_bases':stats,'documents':len(imported),'chunks':sum(x['chunk_count'] for x in imported),'integrity_problems':len(problems),'orphan_candidates':len(orphan_candidates)}
    (ROOT/'final_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    codes=json.loads((ROOT/'code_manifest.json').read_text(encoding='utf-8'))
    members=json.loads((ROOT/'archive_members.json').read_text(encoding='utf-8'))
    lines=['# Jibot1（STM32）资料入库清单','',f"资料根目录：`{summary['source_directory']}`。",'',
        '目标网页：http://127.0.0.1:5173/ 。在“六度机械臂”项目选择自动检索，可使用已关联的“机械臂”和“STM32F103”知识库。','',
        '| 目标知识库 | 本次新增文档 | 本次新增切片 |','| --- | ---: | ---: |']
    lines += [f"| {x['knowledge_base']} | {x['new_documents']} | {x['new_chunks']} |" for x in stats]
    lines += ['',f"合计：{summary['documents']} 份文档，{summary['chunks']} 个切片。计数只包括本次导入后仍在库中的文档，不含原有资料。",'',
        '## 处理方式','',
        '- PDF 按原页提取，并沿用现有 RAG 的 900 字符切片、120 字符重叠；PDF 切片保留页码。',
        f'- 压缩包展开读取后，项目及附带 USB 示例源码按内容去重，共 {len(codes)} 份不重复源码，合并为 18 份源码文档。源码片段保留压缩包成员路径、函数或段落标签、原始行号。重复源码的全部来源保存在 code_manifest.json。',
        '- 两份快速上手图、KPZ32 引脚图及 FlyMcu 下载步骤图已人工核对转录。两份快速上手 PPT 与同版图片合并处理。',
        '- 教程 PDF 内的 287 张不重复图片、Office 文件内的 149 张不重复图片进行了本机 OCR；结果作为带来源标识的截图文字补充。两类计数各自去重，不能理解为跨类别完全无重复。',
        '- 《C和指针》470页、《嵌入式c编程语言入门与深入》378页及《STM32时钟图》1页，共849页补充不可见 OCR 文字层；原页面图保留，抽查渲染与原件一致。',
        '- 5份旧版 DOC 使用本机 Word 只读、禁用宏方式提取；其中的截图另作 OCR 补充。',
        '- 根目录《资料导读》位于 STM32 文件夹，但多处章节名写 ESP32；已保留原文并标注矛盾。',
        '- 中断后恢复了本机 RAG 后端，以本机地址直连 Ollama；原有数据库与知识库记录保留。','',
        '## 已核对','',
        f"- 数据库文档数、向量ID列表及实际向量存在性核对：检查 {len(checks)} 份文档，发现 {len(problems)} 项记录问题。",
        '- 4组检索抽查命中了六轴手柄配对/按键、KPZ32 PWM引脚、kinematics_analysis 逆运动学源码、loop_uart 串口解析相关源码；详细结果保存在 retrieval_checks.json。',
        '- Keil工程编译文件索引从 .uvproj 的实际 FilePath/Device 配置提取，可用于区分工程引用文件与包内其他历史代码。','',
        '## 内容边界','',
        '- 视频只保留文件清单，未进行语音转写；软件安装器、固件 HEX/BIN、3D STEP 模型及 CHM/RAR 等未转为正文索引。',
        '- 通用第三方依赖、编译产物、字体数组、无关板型的代码被过滤，详见 archive_members.json 的逐项处理状态。',
        '- OCR 可检索文字；截图中的代码符号、数字、公式、图纸连接关系仍须核对原图，不能把 OCR 结果当作已编译验证的代码或完整电路模型。',
        '- 《资料导读》及附带的软件下载网址只保存原文，未自动下载外链资源。','',
        '## 文档及来源明细','',
        '| 知识库 | 文档 | 切片数 | 原始来源 |','| --- | --- | ---: | --- |']
    for doc in sorted(imported,key=lambda x:(names[x['knowledge_base_id']],x['filename'])):
        source='；'.join(sorted(all_aliases[doc['id']])).replace('|','\\|')
        lines.append(f"| {names[doc['knowledge_base_id']]} | {doc['filename']} | {doc['chunk_count']} | {source} |")
    (ROOT/'入库报告.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    if problems:raise RuntimeError('向量完整性检查未通过')


if __name__=='__main__':main()
