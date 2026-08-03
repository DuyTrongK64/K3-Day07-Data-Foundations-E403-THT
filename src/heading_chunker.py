from __future__ import annotations

import re

from .chunking import RecursiveChunker


class HeadingSectionChunker:
    """Split Markdown at headings and keep each heading with its section body.

    University policies are usually organized into named rules or procedures.
    Preserving those names in every chunk gives retrieval both a semantic label
    and a coherent body. Oversized sections are split recursively as a fallback.
    """

    HEADING_PATTERN = re.compile(r"(?m)^(#{1,6}\s+.+)$")

    def __init__(self, chunk_size: int = 500) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        matches = list(self.HEADING_PATTERN.finditer(text))
        if not matches:
            return self._fallback.chunk(text)

        sections: list[str] = []
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append(preamble)
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections.append(text[match.start() : end].strip())

        chunks: list[str] = []
        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            heading_match = self.HEADING_PATTERN.match(section)
            heading = heading_match.group(1) if heading_match else ""
            body = section[heading_match.end() :].strip() if heading_match else section
            for piece in self._fallback.chunk(body):
                candidate = f"{heading}\n\n{piece}".strip() if heading else piece
                if len(candidate) <= self.chunk_size:
                    chunks.append(candidate)
                else:
                    chunks.extend(self._fallback.chunk(candidate))
        return chunks
