import os
import pypdf
import docx
from typing import Optional

class DocumentParser:
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        text = ""
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    def parse_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def parse_txt(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def parse_md(file_path: str) -> str:
        # Markdown can be read as plain text for chunking purposes
        return DocumentParser.parse_txt(file_path)

    @staticmethod
    def parse_file(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return DocumentParser.parse_pdf(file_path)
        elif ext == ".docx":
            return DocumentParser.parse_docx(file_path)
        elif ext in [".txt", ".md"]:
            return DocumentParser.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
