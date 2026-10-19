import os
from pathlib import Path
from typing import Optional, Tuple
import pypdf
from PIL import Image
from app.core.logging import logger

class DocumentParser:
    """
    Extracts text content from uploaded assignments:
    - Text-based PDFs
    - Plain text files
    - Images (with basic metadata & OCR fallback if pytesseract installed)
    """

    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".png", ".jpg", ".jpeg"}
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

    @classmethod
    def validate_upload(cls, filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
        ext = Path(filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file format '{ext}'. Supported formats: {', '.join(cls.ALLOWED_EXTENSIONS)}"
        if file_size > cls.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum limit of {cls.MAX_FILE_SIZE // (1024 * 1024)} MB."
        return True, None

    @classmethod
    def parse_file(cls, file_path: Path) -> str:
        """Parses the given file into clean extracted text."""
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return cls._parse_pdf(file_path)
        elif ext in {".txt", ".md"}:
            return cls._parse_text(file_path)
        elif ext in {".png", ".jpg", ".jpeg"}:
            return cls._parse_image(file_path)
        else:
            raise ValueError(f"Unsupported extension: {ext}")

    @classmethod
    def _parse_pdf(cls, file_path: Path) -> str:
        text_content = []
        try:
            reader = pypdf.PdfReader(str(file_path))
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_content.append(f"--- Page {i + 1} ---\n{page_text}")
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise ValueError(f"Could not read PDF: {str(e)}")

        extracted = "\n\n".join(text_content).strip()
        if not extracted:
            # If standard PDF extraction produced empty string, likely scanned
            return "[Scanned Document / Image PDF: Text extraction returned no extractable text layer. Please review or paste assignment text.]"
            
        return extracted

    @classmethod
    def _parse_text(cls, file_path: Path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise ValueError(f"Could not read text file: {str(e)}")

    @classmethod
    def _parse_image(cls, file_path: Path) -> str:
        # Check if pytesseract is available for OCR
        try:
            import pytesseract
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            if text.strip():
                return text.strip()
        except ImportError:
            logger.info("pytesseract not installed; using image header notice.")
        except Exception as e:
            logger.warning(f"OCR failed on image: {e}")

        # Fallback when OCR engine is not active
        return f"[Image File: {file_path.name} uploaded. Please enter or review the assignment question description.]"
