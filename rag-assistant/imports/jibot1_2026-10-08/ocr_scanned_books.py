from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import sys
from pypdf import PdfReader

from ocr_supplement import init_worker, process_image, CACHE
from prepare_and_import import ROOT


def init_gpu_worker():
    sys.path.insert(0,str(ROOT/'ocr_dml_runtime'))
    import ocr_supplement
    from rapidocr import RapidOCR
    ocr_supplement.ENGINE=RapidOCR(params={
        'Global.font_path':r'C:\Windows\Fonts\simhei.ttf',
        'Global.log_level':'error',
        'Global.use_cls':False,
        'EngineConfig.onnxruntime.use_dml':True,
        'EngineConfig.onnxruntime.dml_ep_cfg':{'device_id':0},
        'EngineConfig.onnxruntime.intra_op_num_threads':1,
        'EngineConfig.onnxruntime.inter_op_num_threads':1,
    })


def main():
    patterns=['*C和指针.pdf','*嵌入式c编程语言入门与深入.pdf','*STM32时钟图.pdf']
    books=[]
    images={}
    for pattern in patterns:
        path=next((ROOT/'extracted').glob(pattern))
        pages=[]
        for number,page in enumerate(PdfReader(path).pages,1):
            items=list(page.images)
            largest=max(items,key=lambda x:x.image.width*x.image.height)
            img=largest.image.convert('RGB')
            key=hashlib.sha256(img.tobytes()).hexdigest()
            output=CACHE/f'{key}.png'
            if not output.exists():img.save(output)
            images[key]=str(output)
            pages.append({'page':number,'image_key':key})
        books.append({'path':str(path),'pages':pages})
    print(json.dumps({'scan_pages':sum(len(b['pages']) for b in books),'images':len(images)}),flush=True)
    failures=[]
    with ProcessPoolExecutor(max_workers=2,initializer=init_gpu_worker) as pool:
        jobs={pool.submit(process_image,path):key for key,path in images.items()}
        for count,future in enumerate(as_completed(jobs),1):
            try:future.result()
            except Exception as exc:failures.append({'image_key':jobs[future],'error':str(exc)})
            if count%25==0 or count==len(jobs):print(json.dumps({'done':count,'total':len(jobs),'failures':len(failures)}),flush=True)
    for book in books:
        for page in book['pages']:
            path=CACHE/f"{page['image_key']}.json"
            rows=json.loads(path.read_text(encoding='utf-8'))['rows'] if path.exists() else []
            page['lines']=[row['text'] for row in rows if row['score']>=0.65]
    (ROOT/'scanned_book_ocr.json').write_text(json.dumps({'books':books,'failures':failures},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed_books':len(books),'failures':failures}),flush=True)


if __name__=='__main__':
    main()
