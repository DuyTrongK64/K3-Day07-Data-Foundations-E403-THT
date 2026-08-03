from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """Answer questions using retrieval-augmented generation."""

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        context_blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            source = metadata.get("source_url") or metadata.get("source") or "không rõ"
            context_blocks.append(f"[{index}] Nguồn: {source}\n{result['content']}")

        context = "\n\n".join(context_blocks) or "Không tìm thấy ngữ cảnh liên quan."
        prompt = (
            "Bạn là trợ lý hỏi đáp dựa trên cơ sở tri thức. Chỉ trả lời bằng "
            "thông tin có trong ngữ cảnh. Nếu ngữ cảnh không đủ, hãy nói rõ rằng "
            "không đủ thông tin; không suy đoán. Khi có thể, hãy dẫn số nguồn [1], [2]...\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI: {question}\n\n"
            "TRẢ LỜI:"
        )
        return self.llm_fn(prompt)
