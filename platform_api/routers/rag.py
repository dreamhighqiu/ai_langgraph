from fastapi import APIRouter, Depends, HTTPException
import httpx

from ..auth import require_api_key
from ..config import settings

router = APIRouter(prefix="/rag", tags=["rag"], dependencies=[Depends(require_api_key)])


@router.post("/query")
async def query_rag(payload: dict):
    url = f"{settings.lightrag_base_url.rstrip('/')}/query/text"
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload)
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()
