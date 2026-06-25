"""PDF text extraction with layered fallbacks.

Extraction order:
  1. pdfplumber  — best quality for digital PDFs (requires pdfplumber installed)
  2. Pure-Python stream parser — stdlib only, works without cryptography
  3. OCR via pytesseract  — last resort for scanned documents
"""

import re
import subprocess
import sys
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


# Probe once at module load — pdfplumber's dependency chain may cause an
# unrecoverable Rust panic that cannot be caught inside this process.
def _probe_pdfplumber() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import pdfplumber"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


_PDFPLUMBER_AVAILABLE: bool = _probe_pdfplumber()


class PDFParser:
    """Extracts text from PDF files.

    Tries pdfplumber for digital PDFs; falls back to a pure-Python stream
    extractor (no external dependencies) if pdfplumber is unavailable or
    broken; finally falls back to OCR for scanned documents.
    """

    def __init__(self, ocr_fallback_threshold: int = 100) -> None:
        self.ocr_fallback_threshold = ocr_fallback_threshold

    def extract_text(self, pdf_path: Path | str) -> str:
        """Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Extracted text as a UTF-8 string.

        Raises:
            FileNotFoundError: If the PDF does not exist.
            RuntimeError: If all extraction methods fail.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        logger.info("pdf_extraction_started", path=str(path))

        # Method 1: pdfplumber
        text, method = self._try_pdfplumber(path)

        # Method 2: pure-Python stream extraction
        if not text:
            text = self._extract_streams(path)
            method = "stream"
            logger.info("pdf_extraction_method", path=str(path), method=method)

        pages = self._count_pages(path)
        avg_chars = len(text) / max(pages, 1)

        logger.debug(
            "pdf_extraction_result",
            path=str(path),
            method=method,
            total_chars=len(text),
            pages=pages,
            avg_chars_per_page=round(avg_chars, 1),
        )

        # Method 3: OCR fallback
        if avg_chars < self.ocr_fallback_threshold:
            logger.warning(
                "pdf_ocr_fallback_triggered",
                path=str(path),
                avg_chars_per_page=round(avg_chars, 1),
                threshold=self.ocr_fallback_threshold,
            )
            try:
                from src.parser.ocr import OCRExtractor

                text = OCRExtractor().extract(path)
                method = "ocr"
                logger.info("pdf_ocr_extraction_complete", path=str(path), total_chars=len(text))
            except Exception as exc:
                logger.warning("pdf_ocr_unavailable", error=str(exc))
                if not text:
                    raise RuntimeError(f"All PDF extraction methods failed for {path}") from exc

        logger.info("pdf_extraction_complete", path=str(path), method=method, total_chars=len(text))
        return text

    # ------------------------------------------------------------------
    # Method 1: pdfplumber
    # ------------------------------------------------------------------

    def _try_pdfplumber(self, path: Path) -> tuple[str, str]:
        """Attempt extraction with pdfplumber. Returns (text, method)."""
        if not _PDFPLUMBER_AVAILABLE:
            logger.debug("pdfplumber_skipped", reason="import probe failed")
            return "", ""
        try:
            import pdfplumber

            pages_text: list[str] = []
            with pdfplumber.open(str(path)) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        pages_text.append(page.extract_text() or "")
                    except Exception as exc:
                        logger.warning("pdf_page_error", page=page_num, error=str(exc))
                        pages_text.append("")
            return "\n\n".join(pages_text), "pdfplumber"
        except Exception as exc:
            logger.debug("pdfplumber_failed", error=str(exc))
            return "", ""

    # ------------------------------------------------------------------
    # Method 2: pure-Python PDF stream extractor (no external deps)
    # ------------------------------------------------------------------

    def _extract_streams(self, path: Path) -> str:
        """Extract text from PDF content streams using stdlib only.

        Handles uncompressed Type1/TrueType text operators (Tj, TJ, ').
        Does not handle FlateDecode-compressed streams — for those, the
        pdfplumber or OCR path is needed.
        """
        with open(path, "rb") as f:
            data = f.read()

        # Extract raw stream bytes
        raw_streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL)

        text_parts: list[str] = []
        for stream in raw_streams:
            page_text = self._parse_content_stream(stream)
            if page_text.strip():
                text_parts.append(page_text)

        return "\n\n".join(text_parts)

    @staticmethod
    def _parse_content_stream(stream: bytes) -> str:
        """Parse a PDF content stream and extract visible text.

        Handles PDF string escaping: \\( and \\) are literal parens inside
        a string, not string delimiters.  Simple regex breaks on these.
        """
        parts: list[str] = []
        i = 0
        n = len(stream)

        while i < n:
            if stream[i : i + 1] != b"(":
                i += 1
                continue

            # Read a PDF string literal, respecting escape sequences
            j = i + 1
            depth = 1
            text_buf = bytearray()
            while j < n and depth > 0:
                b = stream[j]
                if stream[j : j + 1] == b"\\" and j + 1 < n:
                    # Escape sequence — keep the escaped byte, skip the backslash
                    text_buf.append(stream[j + 1])
                    j += 2
                    continue
                if b == ord("("):
                    depth += 1
                elif b == ord(")"):
                    depth -= 1
                    if depth == 0:
                        break
                text_buf.append(b)
                j += 1

            # Check whether this string literal is followed by Tj (with optional whitespace)
            after = stream[j + 1 : j + 10].lstrip(b" \t\r\n")
            if after.startswith(b"Tj"):
                try:
                    text = bytes(text_buf).decode("latin-1")
                    if text.strip():
                        parts.append(text)
                except Exception:
                    pass

            i = j + 1

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _count_pages(self, path: Path) -> int:
        """Count pages from PDF structure without full parse.

        Returns 0 if the file is not a valid PDF or has no detectable pages.
        Callers should use max(pages, 1) before dividing.
        """
        if _PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber

                with pdfplumber.open(str(path)) as pdf:
                    return len(pdf.pages)
            except Exception:
                pass

        # Fallback: count /Type /Page entries in raw bytes (no external deps)
        try:
            with open(path, "rb") as f:
                data = f.read()
            return len(re.findall(rb"/Type\s*/Page\b", data))
        except Exception:
            return 0
