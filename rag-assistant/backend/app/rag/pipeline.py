import logging
import math
import re
import time
from pathlib import Path
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader, Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_community.document_loaders.parsers.images import RapidOCRBlobParser
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import OLLAMA_BASE_URL, OLLAMA_CLIENT_KWARGS, OLLAMA_EMBED_MODEL, RAG_MIN_RELEVANCE, RAG_TOP_K, VECTOR_DIR
from ..schemas import ECOMMERCE_DOC_TYPES

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}
logger = logging.getLogger(__name__)


def add_documents_with_retry(store: Chroma, documents, ids: list[str]) -> None:
    """Ollama 偶发返回 502/503 时重试，避免一次临时故障让整份资料导入失败。"""
    delays = (0.0, 1.5, 4.0)
    for attempt, delay in enumerate(delays, start=1):
        if delay:
            time.sleep(delay)
        try:
            store.add_documents(documents, ids=ids)
            return
        except Exception as exc:
            message = str(exc).lower()
            retryable = any(
                marker in message
                for marker in (
                    "status code: 502",
                    "status code: 503",
                    "status code: 429",
                    "temporarily unavailable",
                    "connection refused",
                )
            )
            if not retryable or attempt == len(delays):
                raise
            logger.warning("向量服务暂时不可用，第 %s/%s 次重试：%s", attempt, len(delays), exc)


def get_embeddings():
    return OllamaEmbeddings(
        model=OLLAMA_EMBED_MODEL,
        base_url=OLLAMA_BASE_URL,
        client_kwargs=OLLAMA_CLIENT_KWARGS,
    )


def get_vector_store(knowledge_base_id: str) -> Chroma:
    return Chroma(
        collection_name=f"kb_{knowledge_base_id.replace('-', '_')}",
        persist_directory=str(VECTOR_DIR),
        embedding_function=get_embeddings(),
    )


def text_encoding(path: Path) -> str:
    """兼容常见 Windows 中文文本，避免编码探测依赖导致上传失败。"""
    content = path.read_bytes()
    if content.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"
    try:
        content.decode("utf-8-sig")
        return "utf-8-sig"
    except UnicodeDecodeError:
        try:
            content.decode("gb18030")
            return "gb18030"
        except UnicodeDecodeError as exc:
            raise ValueError("无法识别文本编码，请将文件另存为 UTF-8 后重新上传") from exc


def repair_pdf_text(text: str) -> str:
    """修复部分 CAD/PDF 导出器缺少 ToUnicode 映射造成的 GBK 乱码。"""
    if not text:
        return text
    try:
        candidate = text.encode("latin-1").decode("gb18030")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    original_cjk = sum("\u4e00" <= char <= "\u9fff" for char in text)
    candidate_cjk = sum("\u4e00" <= char <= "\u9fff" for char in candidate)
    if candidate_cjk >= 2 and candidate_cjk > original_cjk:
        return candidate
    return text


def load_pdf(path: Path):
    documents = PyPDFLoader(str(path), extract_images=False).load()
    for document in documents:
        document.page_content = repair_pdf_text(document.page_content)

    # 逐页判断：普通文字页不能掩盖同一份 PDF 中的扫描页。
    needs_ocr = [
        index for index, document in enumerate(documents)
        if len(document.page_content.strip()) < 80
    ]
    if needs_ocr:
        try:
            image_parser = RapidOCRBlobParser()
            image_documents = PyPDFLoader(
                str(path), extract_images=True, images_parser=image_parser
            ).load()
            image_pages = {
                document.metadata.get("page", index): document
                for index, document in enumerate(image_documents)
            }
            for index in needs_ocr:
                image_document = image_pages.get(documents[index].metadata.get("page", index))
                if image_document is None:
                    continue
                repaired = repair_pdf_text(image_document.page_content)
                if len(repaired.strip()) > len(documents[index].page_content.strip()):
                    documents[index].page_content = repaired
        except Exception:
            logger.warning("PDF 图片视觉解析失败，保留文字层：%s", path.name, exc_info=True)
    return documents


def load_file(path: Path, original_filename: str):
    extension = Path(original_filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("目前支持 PDF、DOCX、TXT、Markdown 和 CSV 文件")

    if extension == ".pdf":
        documents = load_pdf(path)
    elif extension == ".docx":
        documents = Docx2txtLoader(str(path)).load()
    elif extension == ".csv":
        documents = CSVLoader(str(path), encoding=text_encoding(path)).load()
    else:
        documents = TextLoader(str(path), encoding=text_encoding(path)).load()

    for document in documents:
        document.metadata["filename"] = original_filename
        document.metadata["source"] = original_filename
        if isinstance(document.metadata.get("page"), int):
            document.metadata["page"] += 1
        if extension == ".csv":
            csv_fields = {}
            for key in ("record_id", "doc_type", "source_table", "source_id", "product_id", "review_id", "rating", "name", "category", "has_image"):
                match = re.search(rf"(?m)^{re.escape(key)}:[ \t]*([^\r\n]*)$", document.page_content)
                if match:
                    csv_fields[key] = match.group(1).strip()
            if csv_fields.get("doc_type") in ECOMMERCE_DOC_TYPES:
                for key in ("record_id", "doc_type", "source_table", "source_id", "name", "category"):
                    if csv_fields.get(key):
                        document.metadata[key] = csv_fields[key]
                for key in ("product_id", "review_id", "rating"):
                    try:
                        if csv_fields.get(key):
                            document.metadata[key] = int(csv_fields[key])
                    except ValueError:
                        pass
                if "has_image" in csv_fields:
                    document.metadata["has_image"] = csv_fields["has_image"].lower() in {"true", "1", "yes"}
    return documents


def index_file(knowledge_base_id: str, document_id: str, path: Path, original_filename: str):
    source_documents = load_file(path, original_filename)
    if not source_documents:
        raise ValueError("文件中没有提取到可索引的文字")

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(source_documents)
    if not chunks:
        raise ValueError("文件内容为空，无法建立索引")

    vector_ids = [f"{document_id}-{index}-{uuid4().hex[:8]}" for index in range(len(chunks))]
    for index, chunk in enumerate(chunks):
        chunk.metadata["knowledge_base_id"] = knowledge_base_id
        chunk.metadata["document_id"] = document_id
        chunk.metadata["filename"] = original_filename
        chunk.metadata["chunk_index"] = index + 1
        chunk.metadata["chunk_id"] = vector_ids[index]

    store = get_vector_store(knowledge_base_id)
    try:
        # 分批处理长文档，避免一次提交数千分片。
        for start in range(0, len(chunks), 64):
            add_documents_with_retry(
                store,
                chunks[start:start + 64],
                vector_ids[start:start + 64],
            )
    except Exception:
        try:
            store.delete(ids=vector_ids)
        except Exception:
            logger.exception("清理未完成的文档索引失败：%s", document_id)
        raise
    return len(chunks), vector_ids


def remove_document_vectors(knowledge_base_id: str, vector_ids: list[str]):
    if vector_ids:
        get_vector_store(knowledge_base_id).delete(ids=vector_ids)


def delete_knowledge_base_collection(knowledge_base_id: str):
    get_vector_store(knowledge_base_id).delete_collection()


def read_document_chunks(knowledge_base_id: str, document_id: str, filename: str,
                         vector_ids: list[str], offset: int, limit: int):
    """只读已有向量的文本和元数据；浏览分片无需调用 Ollama。"""
    selected_ids = vector_ids[offset:offset + limit]
    if not selected_ids:
        return []
    result = get_vector_store(knowledge_base_id).get(
        ids=selected_ids, include=["documents", "metadatas"]
    )
    records = {
        item_id: (content, metadata or {})
        for item_id, content, metadata in zip(
            result["ids"], result["documents"], result["metadatas"]
        )
    }
    items = []
    for position, item_id in enumerate(selected_ids, offset + 1):
        if item_id not in records:
            continue
        content, metadata = records[item_id]
        if metadata.get("document_id", document_id) != document_id:
            continue
        if metadata.get("knowledge_base_id", knowledge_base_id) != knowledge_base_id:
            continue
        items.append({
            "id": item_id,
            "content": content or "",
            "filename": filename,
            "page": metadata.get("page"),
            "index": metadata.get("chunk_index", position),
        })
    return items


def retrieve_contexts(
    question: str,
    knowledge_base_ids: list[str],
    names_by_id: dict[str, str],
    top_k: int | None = None,
    product_ids: list[int] | None = None,
    doc_types: list[str] | None = None,
):
    matches = []
    per_base_limit = top_k or RAG_TOP_K
    filters = []
    if product_ids:
        filters.append({"product_id": {"$in": product_ids}})
    if doc_types:
        filters.append({"doc_type": {"$in": doc_types}})
    metadata_filter = {"$and": filters} if len(filters) > 1 else (filters[0] if filters else None)
    for knowledge_base_id in knowledge_base_ids:
        store = get_vector_store(knowledge_base_id)
        if not store.get(limit=1, include=["metadatas"])["ids"]:
            continue
        results = store.similarity_search_with_relevance_scores(
            question,
            k=per_base_limit,
            filter=metadata_filter,
        )
        for document, score in results:
            if not math.isfinite(score) or score < RAG_MIN_RELEVANCE:
                continue
            metadata = document.metadata or {}
            matches.append(
                {
                    "content": document.page_content,
                    "filename": metadata.get("filename") or Path(metadata.get("source", "资料")).name,
                    "page": metadata.get("page"),
                    "knowledge_base_id": knowledge_base_id,
                    "knowledge_base_name": names_by_id.get(knowledge_base_id, "知识库"),
                    "metadata": metadata,
                    "chunk_id": metadata.get("chunk_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "score": float(score),
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[: (per_base_limit if top_k is not None else RAG_TOP_K * 2)]
