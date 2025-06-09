from fastapi import APIRouter, UploadFile, File
from src.app.infrastructure.file_processing.pdf import extract_text_from_pdf
from src.app.infrastructure.llm.rag_chain_instance import rag_chain

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(content)
    text = extract_text_from_pdf(temp_path)
    rag_chain.ingest_document(text)
    return {"status": "uploaded and indexed"}
