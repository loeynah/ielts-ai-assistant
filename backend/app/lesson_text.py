from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path


class _HtmlTextExtractor(HTMLParser):
    _SKIP_TAGS = frozenset({"script", "style", "noscript"})

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text and not text.startswith("/*") and "var(" not in text:
            self._chunks.append(text)

    def text(self) -> str:
        return "\n".join(self._chunks)


def html_to_text(path: Path, *, max_chars: int = 6000) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    parser = _HtmlTextExtractor()
    parser.feed(raw)
    text = re.sub(r"\n{3,}", "\n\n", parser.text())
    return text[:max_chars]


def pdf_to_text(path: Path, *, max_chars: int = 6000) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages[:8]:
        parts.append(page.extract_text() or "")
    text = "\n".join(parts)
    return text[:max_chars]


def extract_lesson_text(html_path: Path | None, pdf_path: Path | None, *, max_chars: int = 6000) -> str:
    if html_path and html_path.exists():
        return html_to_text(html_path, max_chars=max_chars)
    if pdf_path and pdf_path.exists():
        return pdf_to_text(pdf_path, max_chars=max_chars)
    return ""
