"""PDF text extraction using pdfplumber with OCR fallback."""

from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PDFParser:
    """Extracts text from PDF files.

    Uses pdfplumber for digital PDFs (text layer present).
    Falls back to OCR via pytesseract for scanned documents.
    """

    def __init__(self, ocr_fallback_threshold: int = 100) -> None:
        """Initialize the parser.

        Args:
            ocr_fallback_threshold: Average characters per page below which
                OCR fallback is triggered. Defaults to 100.
        """
        self.ocr_fallback_threshold = ocr_fallback_threshold

    def extract_text(self, pdf_path: Path | str) -> str:
        """Extract text from a PDF file.

        Attempts digital extraction with pdfplumber first. If the average
        character count per page is below the OCR threshold (indicating a
        scanned document), falls back to OCR extraction.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Extracted text as a UTF-8 string.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            RuntimeError: If text extraction fails on all methods.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        logger.info("pdf_extraction_started", path=str(path))

        text = self._extract_with_pdfplumber(path)
        pages = self._count_pages(path)

        if pages > 0:
            avg_chars = len(text) / pages
        else:
            avg_chars = 0

        logger.debug(
            "pdf_extraction_pdfplumber_result",
            path=str(path),
            total_chars=len(text),
            pages=pages,
            avg_chars_per_page=round(avg_chars, 1),
        )

        if avg_chars < self.ocr_fallback_threshold:
            logger.warning(
                "pdf_ocr_fallback_triggered",
                path=str(path),
                avg_chars_per_page=round(avg_chars, 1),
                threshold=self.ocr_fallback_threshold,
            )
            from src.parser.ocr import OCRExtractor  # lazy import to avoid loading pytesseract if not needed

            ocr = OCRExtractor()
            text = ocr.extract(path)
            logger.info(
                "pdf_ocr_extraction_complete",
                path=str(path),
                total_chars=len(text),
            )
        else:
            logger.info(
                "pdf_extraction_complete",
                path=str(path),
                method="pdfplumber",
                total_chars=len(text),
            )

        return text

    def _extract_with_pdfplumber(self, path: Path) -> str:
        """Extract text using pdfplumber.

        Args:
            path: Path to the PDF.

        Returns:
            Concatenated text from all pages.
        """
        import pdfplumber

        pages_text: list[str] = []
        with pdfplumber.open(str(path)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                    pages_text.append(page_text)
                except Exception as exc:
                    logger.warning(
                        "pdf_page_extraction_error",
                        page=page_num,
                        error=str(exc),
                    )
                    pages_text.append("")

        return "\n\n".join(pages_text)

    def _count_pages(self, path: Path) -> int:
        """Return the number of pages in a PDF."""
        import pdfplumber

        try:
            with pdfplumber.open(str(path)) as pdf:
                return len(pdf.pages)
        except Exception:
            return 0
