from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import hashlib
import io
import json
import zipfile

from PIL import Image
from ocr_supplement import init_worker, process_image, CACHE
from prepare_and_import import ROOT, SOURCE, PREPARED, KB


def main():
    records=json.loads((ROOT/'archive_members.json').read_text(encoding='utf-8'))
    sources=[]
    for row in records:
        path=Path(row.get('extracted_path',''))
        if path.suffix=='.doc':
            path=path.with_name(path.stem+'_converted.docx')
        if path.suffix=='.docx' and path.exists():
            kb='c0077d246def4753bc5465e919510b52' if '01-技术文档' in row['source'] and '舵机知识' not in row['source'] else KB
            sources.append({'path':str(path),'source':row['source'],'kb':kb})
    sources.extend({'path':str(p),'source':str(p),'kb':KB} for p in SOURCE.rglob('*.pptx') if '快速上手' not in p.name)
    images={}
    for entry in sources:
        with zipfile.ZipFile(entry['path']) as z:
            for name in z.namelist():
                if '/media/' not in name or name.endswith('/'):
                    continue
                try:
                    img=Image.open(io.BytesIO(z.read(name))).convert('RGB')
                except Exception:
                    continue
                if img.width<120 or img.height<45:
                    continue
                key=hashlib.sha256(img.tobytes()).hexdigest()
                path=CACHE/f'{key}.png'
                if not path.exists():img.save(path)
                images.setdefault(key,{'path':str(path),'sources':[]})['sources'].append({**entry,'image':name})
    print(json.dumps({'office_images':len(images)}),flush=True)
    failures=[]
    with ProcessPoolExecutor(max_workers=3,initializer=init_worker) as pool:
        jobs={pool.submit(process_image,x['path']):key for key,x in images.items()}
        for count,future in enumerate(as_completed(jobs),1):
            try:images[jobs[future]]['ocr']=future.result()
            except Exception as exc:failures.append(str(exc))
            if count%10==0 or count==len(jobs):print(json.dumps({'done':count,'total':len(jobs),'failures':len(failures)}),flush=True)
    grouped={}
    for image in images.values():
        text='\n'.join(x['text'] for x in image.get('ocr',{}).get('rows',[]) if x['score']>=0.75)
        if len(text)<15:continue
        for src in image['sources']:
            grouped.setdefault(src['source'],{'sections':[],'kb':src['kb']})['sections'].append(f"## 图片 {src['image']}\n来源：{src['source']}\n本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。\n\n{text}\n")
    queue=[]
    for src,content in grouped.items():
        name=Path(src).stem+'（Office截图OCR补充）.md'
        output=PREPARED/name
        output.write_text('\n'.join(content['sections']),encoding='utf-8')
        queue.append({'path':str(output),'source':src,'knowledge_base_id':content['kb']})
    (ROOT/'office_ocr_queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'office_ocr_report.json').write_text(json.dumps({'images':len(images),'failures':failures,'outputs':len(queue)},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'outputs':len(queue),'failures':failures},ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
