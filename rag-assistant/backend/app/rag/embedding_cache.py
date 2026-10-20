"""按模型版本和正文摘要缓存向量；不保存正文，不混用不同模型的结果。"""

import hashlib
import math
import struct

from ..database import connect, now_iso


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_cached_vectors(model_key: str, hashes) -> dict[str, list[float]]:
    keys = list(dict.fromkeys(hashes))
    result = {}
    with connect() as db:
        for start in range(0, len(keys), 400):
            batch = keys[start:start + 400]
            placeholders = ",".join("?" for _ in batch)
            rows = db.execute(
                f"SELECT text_hash, dimensions, embedding FROM embedding_cache "
                f"WHERE model_key = ? AND text_hash IN ({placeholders})",
                (model_key, *batch),
            ).fetchall()
            for row in rows:
                size, blob = row["dimensions"], row["embedding"]
                if size <= 0 or len(blob) != size * 4:
                    continue
                vector = list(struct.unpack(f"<{size}f", blob))
                if all(math.isfinite(value) for value in vector):
                    result[row["text_hash"]] = vector
    return result


def save_cached_vectors(model_key: str, vectors: dict[str, list[float]]):
    rows = []
    stamp = now_iso()
    for digest, values in vectors.items():
        vector = [float(value) for value in values]
        if not vector or not all(math.isfinite(value) for value in vector):
            raise ValueError("向量服务返回空值或无效数字")
        rows.append((model_key, digest, len(vector), struct.pack(f"<{len(vector)}f", *vector), stamp))
    if rows:
        with connect() as db:
            db.executemany(
                "INSERT OR REPLACE INTO embedding_cache "
                "(model_key, text_hash, dimensions, embedding, created_at) VALUES (?, ?, ?, ?, ?)",
                rows,
            )
