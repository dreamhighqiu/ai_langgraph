from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import httpx

from ..auth import require_api_key
from ..config import settings

router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[Depends(require_api_key)])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    url = f"{settings.lightrag_base_url.rstrip('/')}/documents/upload"
    file_bytes = await file.read()
    files = {"file": (file.filename, file_bytes, file.content_type or "application/octet-stream")}
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, files=files)
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"LightRAG 上传失败: {response.text}",
        )
    return response.json()
