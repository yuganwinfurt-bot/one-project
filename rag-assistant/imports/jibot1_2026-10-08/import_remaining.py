from pathlib import Path
import json
import shutil
import time

from prepare_and_import import ROOT, SOURCE, PREPARED, ORIGINALS, upload, KB


def main():
    queue=json.loads((ROOT/'archive_import_queue.json').read_text(encoding='utf-8'))
    queue=[x for x in queue if not any(n in Path(x['path']).name for n in ('01cdc9e433_C和指针.pdf','b20291b54d_嵌入式c编程语言入门与深入.pdf','659fc9575f_STM32时钟图.pdf'))]
    # 核心机械臂材料优先，然后处理通用参考手册。
    queue.sort(key=lambda x:x['knowledge_base_id'] != KB)
    png=SOURCE/'001-文档教程/KPZ32引脚分布图.png'
    shutil.copy2(png, ORIGINALS/png.name)
    queue.insert(0,{'path':str(PREPARED/'KPZ32引脚分布图（图片转录）.md'),'source':str(png),'knowledge_base_id':KB})
    for item in json.loads((ROOT/'ocr_report.json').read_text(encoding='utf-8'))['outputs']:
        queue.append({'path':item['path'],'source':item['source'],'knowledge_base_id':KB})
    extra=ROOT/'legacy_doc_queue.json'
    if extra.exists():
        queue.extend(json.loads(extra.read_text(encoding='utf-8')))
    office=ROOT/'office_ocr_queue.json'
    if office.exists():queue.extend(json.loads(office.read_text(encoding='utf-8')))
    for filename in ['STM32程序下载步骤（FlyMcu图片转录）.md','Jibot1_Keil工程编译文件索引.md']:
        queue.append({'path':str(PREPARED/filename),'source':str(SOURCE),'knowledge_base_id':KB})
    failures=[]
    for num,item in enumerate(queue,1):
        path=Path(item['path'])
        start=time.monotonic()
        print(json.dumps({'position':num,'total':len(queue),'starting':path.name},ensure_ascii=False),flush=True)
        try:
            upload(path,item['source'],item['knowledge_base_id'])
        except Exception as exc:
            failures.append({**item,'error':str(exc)})
            print(json.dumps({'failed':path.name,'error':str(exc)},ensure_ascii=False),flush=True)
        (ROOT/'bulk_failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'completed_position':num,'seconds':round(time.monotonic()-start,1)}),flush=True)
    print(json.dumps({'done':len(queue),'failures':len(failures)}),flush=True)


if __name__=='__main__':
    main()
