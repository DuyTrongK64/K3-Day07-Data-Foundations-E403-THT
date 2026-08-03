"""Reproducible K3 retrieval benchmark using the multilingual local embedder.

Run from the repository root:
    EMBEDDING_PROVIDER=local .venv/bin/python scripts/run_benchmark.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ingest import build_knowledge_base, load_documents  # noqa: E402
from src import (  # noqa: E402
    ChunkingStrategyComparator,
    FixedSizeChunker,
    HeadingSectionChunker,
    LocalEmbedder,
    RecursiveChunker,
    SentenceChunker,
    compute_similarity,
)

DATA_DIR = ROOT / "data" / "k3_university"

BENCHMARKS = [
    {
        "query": "Người dùng thư viện RMIT được mượn tối đa bao nhiêu tài liệu và trong bao lâu?",
        "expected_doc_id": "rmit-student-library-2026",
        "metadata_filter": {"audience": "student"},
    },
    {
        "query": "Điều kiện tín chỉ và GPA của học bổng thành tích RMIT năm 2026 là gì?",
        "expected_doc_id": "rmit-current-student-scholarship-2026",
    },
    {
        "query": "Trạng thái Conflict khi đăng ký học phần VinUni có nghĩa là gì?",
        "expected_doc_id": "vinuni-course-registration-2026",
    },
    {
        "query": "Nếu sinh viên RMIT không trả học phí đúng hạn thì điều gì có thể xảy ra?",
        "expected_doc_id": "rmit-fees-and-finance",
    },
    {
        "query": "Mức hỗ trợ học phí cho người thân của sinh viên hoặc cựu sinh viên RMIT bắt đầu học năm 2026 là bao nhiêu?",
        "expected_doc_id": "rmit-tuition-fee-assistance-2026",
    },
]

SIMILARITY_PAIRS = [
    (
        "Sinh viên được mượn tối đa 25 cuốn sách trong một tháng.",
        "Hạn mức thư viện cho người học là 25 đầu sách trong 30 ngày.",
        "cao",
    ),
    (
        "Lớp có trạng thái Conflict khi bị trùng thời khóa biểu.",
        "Xung đột lịch học khiến sinh viên không thể đăng ký lớp.",
        "cao",
    ),
    (
        "Ứng viên học bổng cần GPA tích lũy tối thiểu 3,4.",
        "Thư viện cung cấp dịch vụ in và photocopy.",
        "thấp",
    ),
    (
        "Sinh viên có thể thanh toán học phí bằng chuyển khoản.",
        "Cựu sinh viên chịu chi phí gửi trả sách qua bưu điện.",
        "thấp",
    ),
    (
        "Học bổng 50% được phân bổ trước học bổng 25%.",
        "Chính sách hỗ trợ học phí không được dùng đồng thời với chính sách khác.",
        "trung bình-thấp",
    ),
]


def print_baseline() -> None:
    print("\n=== BASELINE CHUNKING (chunk_size=300) ===")
    comparator = ChunkingStrategyComparator()
    for doc in load_documents(DATA_DIR)[:3]:
        stats = comparator.compare(doc.content, chunk_size=300)
        custom = HeadingSectionChunker(chunk_size=300).chunk(doc.content)
        print(f"DOC {doc.id}")
        for name, values in stats.items():
            print(f"  {name}: count={values['count']} avg={values['avg_length']:.2f}")
        average = sum(map(len, custom)) / len(custom) if custom else 0.0
        print(f"  heading_section: count={len(custom)} avg={average:.2f}")


def print_similarity_predictions(embedder: LocalEmbedder) -> None:
    print("\n=== SIMILARITY PREDICTIONS ===")
    for index, (sentence_a, sentence_b, prediction) in enumerate(SIMILARITY_PAIRS, start=1):
        score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
        print(f"PAIR {index}: prediction={prediction} score={score:.4f}")


def print_retrieval_results(embedder: LocalEmbedder) -> None:
    print("\n=== RETRIEVAL BENCHMARK ===")
    strategies = {
        "fixed_size": FixedSizeChunker(chunk_size=300, overlap=50),
        "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
        "recursive": RecursiveChunker(chunk_size=300),
        "heading_section": HeadingSectionChunker(chunk_size=300),
    }
    for strategy_name, chunker in strategies.items():
        store = build_knowledge_base(
            DATA_DIR,
            embedding_fn=embedder,
            chunker=chunker,
            collection_name=f"k3-{strategy_name}",
        )
        successes = 0
        print(f"\nSTRATEGY {strategy_name}: chunks={store.get_collection_size()}")
        for index, item in enumerate(BENCHMARKS, start=1):
            metadata_filter = item.get("metadata_filter")
            results = store.search_with_filter(
                item["query"], top_k=3, metadata_filter=metadata_filter
            )
            ids = [result["metadata"]["doc_id"] for result in results]
            relevant = item["expected_doc_id"] in ids
            successes += int(relevant)
            ranking = ", ".join(
                f"{result['metadata']['doc_id']}:{result['score']:.4f}"
                for result in results
            )
            print(
                f"  Q{index} relevant={relevant} expected={item['expected_doc_id']} "
                f"filter={metadata_filter} top3=[{ranking}]"
            )
        print(f"  TOP3_SUCCESS={successes}/5")


def main() -> int:
    embedder = LocalEmbedder()
    print(f"EMBEDDER={embedder._backend_name}")
    print_baseline()
    print_similarity_predictions(embedder)
    print_retrieval_results(embedder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
