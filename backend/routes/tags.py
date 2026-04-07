"""
routes/tags.py
--------------
Tag management endpoints.

GET /tags/ – list all tags
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.tag import TagOut
from services import tag_service

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)) -> list[TagOut]:
    """Return all tags."""
    return await tag_service.list_tags(db)
