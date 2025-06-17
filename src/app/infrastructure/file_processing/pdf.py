import fitz  # PyMuPDF
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_pdf_with_annexes(filepath: str) -> dict:
    reader = PdfReader(filepath)
    summary = ""
    annexes = []

    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        if "ANEXO" in text.upper():
            annexes.append(text)
        elif "RESUMEN" in text.upper() or len(summary) < 1000:
            summary += text

    return {
        "summary": summary.strip(),
        "annexes": annexes
    }