"""对现有知识库执行只读检索，检查已人工核对的问题能否命中指定文件。"""

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import DB_PATH, RAG_MIN_RELEVANCE, RAG_TOP_K  # noqa: E402
from app.rag.pipeline import retrieve_contexts  # noqa: E402


def run(cases_path: Path) -> dict:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    with sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True) as db:
        knowledge_bases = {name: kb_id for kb_id, name in db.execute("SELECT id, name FROM knowledge_bases")}

    results = []
    for case in cases:
        name = case["knowledge_base"]
        if name not in knowledge_bases:
            raise ValueError(f"找不到知识库：{name}")
        kb_id = knowledge_bases[name]
        started = time.perf_counter()
        try:
            hits = retrieve_contexts(case["question"], [kb_id], {kb_id: name})
            files = [hit["filename"] for hit in hits]
            expected_files = case["expected_files"]
            matched = (
                bool(set(files) & set(expected_files)) if expected_files else not hits
            )
            results.append({
                "question": case["question"],
                "matched": matched,
                "expected_no_result": not expected_files,
                "top_score": round(hits[0]["score"], 3) if hits else None,
                "returned_files": files,
                "elapsed_seconds": round(time.perf_counter() - started, 2),
            })
        except Exception as exc:
            results.append({
                "question": case["question"],
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed_seconds": round(time.perf_counter() - started, 2),
            })
            break

    errors = [item for item in results if "error" in item]
    complete = not errors and len(results) == len(cases)
    positives = [item for item in results if not item.get("expected_no_result")]
    negatives = [item for item in results if item.get("expected_no_result")]
    return {
        "cases": len(cases),
        "completed": len(results) - len(errors),
        "top_k_per_knowledge_base": RAG_TOP_K,
        "min_relevance": RAG_MIN_RELEVANCE,
        "pass_rate": (
            round(sum(item["matched"] for item in results) / len(cases), 3)
            if complete and cases else None
        ),
        "positive_hit_rate": (
            round(sum(item["matched"] for item in positives) / len(positives), 3)
            if complete and positives else None
        ),
        "negative_rejection_rate": (
            round(sum(item["matched"] for item in negatives) / len(negatives), 3)
            if complete and negatives else None
        ),
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases", type=Path, default=ROOT / "eval" / "retrieval_cases.json",
        help="人工核对过的 JSON 测试集",
    )
    args = parser.parse_args()
    report = run(args.cases)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["pass_rate"] is None:
        raise SystemExit(1)
