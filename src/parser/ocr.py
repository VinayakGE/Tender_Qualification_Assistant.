"""OCR-based text extraction for scanned PDF documents."""

from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default DPI for rendering PDF pages before OCR
DEFAULT_DPI = 300


class OCRExtractor:
    """Extracts text from scanned PDFs using pytesseract.

    Renders each PDF page as an image and runs OCR on it.
    Best suited for PDFs that have no embedded text layer.
    """

    def __init__(self, dpi: int = DEFAULT_DPI, lang: str = "eng") -> None:
        """Initialize the OCR extractor.

        Args:
            dpi: Resolution for page rendering (higher = better quality, slower).
            lang: Tesseract language code. Use "eng" for English, "eng+hin" for
                  English + Hindi if the tender has Hindi sections.
        """
        self.dpi = dpi
        self.lang = lang

    def extract(self, pdf_path: Path | str) -> str:
        """Extract text from a PDF using OCR.

        Renders each page to a PIL Image and runs pytesseract on it.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Concatenated OCR text from all pages.

        Raises:
            FileNotFoundError: If the PDF does not exist.
            RuntimeError: If pytesseract or pdf2image is not installed.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        try:
            from pdf2image import convert_from_path
        except ImportError as exc:
            raise RuntimeError(
                "pdf2image is required for OCR. Install with: pip install pdf2image"
            ) from exc

        try:
            import pytesseract
        except ImportError as exc:
            raise RuntimeError(
                "pytesseract is required for OCR. Install with: pip install pytesseract"
            ) from exc

        logger.info("ocr_extraction_started", path=str(path), dpi=self.dpi, lang=self.lang)

        images = convert_from_path(str(path), dpi=self.dpi)
        pages_text: list[str] = []

        for page_num, image in enumerate(images, start=1):
            try:
                page_text = pytesseract.image_to_string(image, lang=self.lang)
                pages_text.append(page_text)
                logger.debug(
                    "ocr_page_complete",
                    page=page_num,
                    chars=len(page_text),
                )
            except Exception as exc:
                logger.warning(
                    "ocr_page_error",
                    page=page_num,
                    error=str(exc),
                )
                pages_text.append("")

        full_text = "\n\n".join(pages_text)
        logger.info(
            "ocr_extraction_complete",
            path=str(path),
            pages=len(images),
            total_chars=len(full_text),
        )
        return full_text
