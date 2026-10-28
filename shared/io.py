"""Read input documents (PDF, DOCX, TXT) and read/write JSON."""
import json
from pathlib import Path


def read_document(path):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    if ext == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(path).paragraphs)
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return str(path)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
