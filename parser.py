import fitz  # PyMuPDF
from typing import Protocol


class DocumentParser(Protocol):
    def parse(self, file_bytes: bytes) -> str:
        """Parses raw bytes and returns extracted text."""
        ...


class PDFParser:
    def parse(self, file_bytes: bytes) -> str:
        """Parses a PDF using PyMuPDF and returns raw text."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_blocks = []
        
        for page in doc:
            # We use get_text("blocks") to preserve some structure
            blocks = page.get_text("blocks")
            # Sort blocks by vertical position then horizontal
            blocks.sort(key=lambda b: (b[1], b[0]))
            
            for b in blocks:
                # b[4] contains the actual text
                text = b[4].strip()
                if text:
                    text_blocks.append(text)
                    
        return "\n\n".join(text_blocks)


class DocumentParserFactory:
    @staticmethod
    def get_parser(mime_type: str, filename: str) -> DocumentParser:
        if mime_type == "application/pdf" or filename.lower().endswith(".pdf"):
            return PDFParser()
        raise ValueError(f"Unsupported document format: {mime_type} / {filename}")
