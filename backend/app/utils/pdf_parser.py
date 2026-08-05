"""PDF parser using PyMuPDF — extracts text with structure detection."""

import re
from typing import Any

import fitz  # PyMuPDF


class PDFParser:
    """Parse PDF documents, extracting text with Bab/Pasal/Ayat structure."""

    # Patterns for Indonesian legal/policy document structure
    BAB_PATTERN = re.compile(
        r"^BAB\s+([IVXLCDM]+|[0-9]+|[A-Z])\b",
        re.IGNORECASE | re.MULTILINE,
    )
    PASAL_PATTERN = re.compile(
        r"^Pasal\s+([0-9]+[A-Za-z]?|[A-Z])\b",
        re.IGNORECASE | re.MULTILINE,
    )
    AYAT_PATTERN = re.compile(
        r"^Ayat\s*\((\d+[a-z]?)\)\b",
        re.IGNORECASE | re.MULTILINE,
    )

    # Document title patterns
    TITLE_PATTERN = re.compile(
        r"^(?:PERATURAN|KEPUTUSAN|SOP|KEBIJAKAN|PEDOMAN|PETUNJUK|SURAT)\s",
        re.IGNORECASE,
    )

    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_sections(self) -> list[dict[str, Any]]:
        """Extract structured sections from PDF.

        Returns list of dicts with keys:
            teks, bab, bab_judul, pasal, pasal_judul, ayat, halaman
        """
        doc = fitz.open(self.file_path)
        sections: list[dict[str, Any]] = []
        current_bab = None
        current_bab_judul = None
        current_pasal = None
        current_pasal_judul = None
        current_ayat = None
        buffer: list[str] = []

        def flush_buffer() -> None:
            if not buffer:
                return
            teks = " ".join(buffer).strip()
            if teks:
                sections.append({
                    "teks": teks,
                    "bab": current_bab,
                    "bab_judul": current_bab_judul,
                    "pasal": current_pasal,
                    "pasal_judul": current_pasal_judul,
                    "ayat": current_ayat,
                    "halaman": page_num,
                })

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            lines = text.split("\n")

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                bab_match = self.BAB_PATTERN.match(stripped)
                if bab_match:
                    flush_buffer()
                    current_bab = bab_match.group(1)
                    current_bab_judul = None
                    current_pasal = None
                    current_pasal_judul = None
                    current_ayat = None
                    buffer = [stripped]
                    continue

                pasal_match = self.PASAL_PATTERN.match(stripped)
                if pasal_match:
                    flush_buffer()
                    current_pasal = pasal_match.group(1)
                    current_pasal_judul = None
                    current_ayat = None
                    buffer = [stripped]
                    continue

                ayat_match = self.AYAT_PATTERN.match(stripped)
                if ayat_match:
                    flush_buffer()
                    current_ayat = ayat_match.group(1)
                    buffer = [stripped]
                    continue

                # Check for judgment lines following BAB / Pasal headers
                if current_bab and current_bab_judul is None and len(buffer) <= 1:
                    # First content line after BAB header is likely the title
                    current_bab_judul = stripped
                    buffer.append(stripped)
                    continue

                if current_pasal and current_pasal_judul is None and len(buffer) <= 1:
                    current_pasal_judul = stripped
                    buffer.append(stripped)
                    continue

                buffer.append(stripped)

            # Page boundary: insert a space between pages
            buffer.append(" ")

        flush_buffer()
        doc.close()
        return sections

    def extract_title(self) -> str | None:
        """Try to extract document title from first page."""
        doc = fitz.open(self.file_path)
        first_page = doc[0]
        text = first_page.get_text("text")
        doc.close()

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines:
            if self.TITLE_PATTERN.match(line):
                return line
        return lines[0] if lines else None
