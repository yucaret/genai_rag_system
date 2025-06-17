from fastapi import APIRouter, UploadFile, File
from src.app.infrastructure.file_processing.pdf import parse_pdf_with_annexes
from src.app.infrastructure.llm.rag_container import rag_chain
import uuid
import os

router = APIRouter()
#rag_chain = RAGChain()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Save PDF to /tmp
    content = await file.read()
    filename = file.filename or f"{uuid.uuid4()}.pdf"
    temp_path = f"/tmp/{filename}"
    
    with open(temp_path, "wb") as f:
        f.write(content)

    # Parse into sections
    parsed = parse_pdf_with_annexes(temp_path)  # returns {"summary": ..., "annexes": [...]}

    # Create doc_id based on filename (or UUID if needed)
    doc_id = os.path.splitext(filename)[0]  # e.g., contrato_2024.pdf → contrato_2024

    # Embed summary
    if parsed.get("summary"):
        rag_chain.ingest_document(
            text=parsed["summary"],
            doc_id=doc_id,
            section="summary"
        )

    # Embed annexes individually with sub-sections
    for idx, annex_text in enumerate(parsed.get("annexes", []), start=1):
        rag_chain.ingest_document(
            text=annex_text,
            doc_id=doc_id,
            section=f"annex_{idx}"
        )

    return {
        "status": "uploaded and embedded",
        "doc_id": doc_id,
        "summary_chunks": len(parsed.get("summary", "").split("\n")),
        "annexes": len(parsed.get("annexes", []))
    }
