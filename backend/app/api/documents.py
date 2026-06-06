import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import DocumentResponse
from app.services import embeddings as embedding_service
from app.services import vector_store
from app.services.chunking import chunk_text
from app.services.extraction import extract_text

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "markdown"}
# Normalize .markdown to the canonical type used everywhere else
_EXT_TO_TYPE = {"markdown": "md"}


def _upload_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=422, detail="No filename provided.")

    raw_ext = Path(file.filename).suffix.lstrip(".").lower()
    if raw_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '.{raw_ext}'. Allowed: pdf, txt, md, markdown.",
        )

    file_type = _EXT_TO_TYPE.get(raw_ext, raw_ext)
    doc_id = str(uuid.uuid4())
    upload_dir = _upload_dir()
    save_path = upload_dir / f"{doc_id}.{raw_ext}"

    content = await file.read()
    save_path.write_bytes(content)

    try:
        text = extract_text(save_path, file_type)
    except Exception as exc:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Text extraction failed: {exc}") from exc

    if not text.strip():
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="No text could be extracted from the file.")

    chunks = chunk_text(text, doc_id, file.filename, file_type)
    chunk_embeddings = embedding_service.embed_texts([c.text for c in chunks])
    vector_store.add_document_chunks(chunks, chunk_embeddings)

    meta = DocumentResponse(
        document_id=doc_id,
        filename=file.filename,
        file_type=file_type,
        character_count=len(text),
        chunk_count=len(chunks),
        status="processed",
    )
    meta_path = upload_dir / f"{doc_id}.meta.json"
    meta_path.write_text(meta.model_dump_json())

    return meta


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents():
    upload_dir = _upload_dir()
    docs = []
    for meta_file in sorted(upload_dir.glob("*.meta.json")):
        docs.append(DocumentResponse.model_validate_json(meta_file.read_text()))
    return docs


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str):
    upload_dir = _upload_dir()
    meta_path = upload_dir / f"{document_id}.meta.json"

    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove the uploaded file — extension may differ from file_type (e.g. .markdown)
    for f in upload_dir.glob(f"{document_id}.*"):
        if not f.name.endswith(".meta.json"):
            f.unlink(missing_ok=True)

    meta_path.unlink(missing_ok=True)
    vector_store.delete_document(document_id)
