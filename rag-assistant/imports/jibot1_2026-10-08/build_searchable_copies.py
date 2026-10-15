"""在扫描PDF副本中叠加不可见OCR文字层；保留原页图和页数。"""
from pathlib import Path
import io
import json
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parent


def main():
    data=json.loads((ROOT/'scanned_book_ocr.json').read_text(encoding='utf-8'))
    if data['failures']:
        raise RuntimeError('OCR尚有失败页，先修复后生成')
    pdfmetrics.registerFont(TTFont('RagOCR',r'C:\Windows\Fonts\simhei.ttf'))
    queue=[]
    for book in data['books']:
        original=Path(book['path'])
        reader=PdfReader(original)
        overlay_buffer=io.BytesIO()
        layer=canvas.Canvas(overlay_buffer,pageCompression=1)
        for page,ocr in zip(reader.pages,book['pages']):
            width,height=float(page.mediabox.width),float(page.mediabox.height)
            layer.setPageSize((width,height))
            obj=layer.beginText(4,height-6)
            obj.setFont('RagOCR',4)
            obj.setLeading(max(1,min(5,(height-12)/max(1,len(ocr['lines'])))))
            obj.setTextRenderMode(3)
            for line in ocr['lines']:
                obj.textLine(line)
            layer.drawText(obj)
            layer.showPage()
        layer.save()
        overlay_buffer.seek(0)
        overlay=PdfReader(overlay_buffer)
        writer=PdfWriter()
        for page,ocr in zip(reader.pages,overlay.pages):
            page.merge_page(ocr)
            writer.add_page(page)
        title=original.name.split('_',1)[1]
        output=ROOT/'prepared'/(Path(title).stem+'（扫描件OCR文字层）.pdf')
        writer.add_metadata({'/Title':title,'/Subject':'原扫描图保留；新增本机OCR文字层，符号和代码需对照原图核实。'})
        with output.open('wb') as stream:writer.write(stream)
        check=PdfReader(output)
        text_count=sum(len(page.extract_text() or '') for page in check.pages)
        if len(check.pages)!=len(reader.pages) or text_count<100:
            raise RuntimeError(f'生成文字层核对失败：{output}')
        record={'path':str(output),'original_path':str(original),'knowledge_base_id':'c0077d246def4753bc5465e919510b52','pages':len(check.pages),'chars':text_count,'bytes':output.stat().st_size}
        queue.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
    (ROOT/'scanned_import_queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
