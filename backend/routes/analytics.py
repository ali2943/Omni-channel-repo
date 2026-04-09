"""
routes/analytics.py
-------------------
Analytics and reporting endpoints.

GET /analytics/kpis    – KPI dashboard
GET /analytics/sla     – SLA compliance report
GET /analytics/volume  – Volume report by channel and day
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/kpis")
async def kpis(db: AsyncSession = Depends(get_db)) -> dict:
    """Return high-level KPI metrics."""
    return await analytics_service.get_kpis(db)


@router.get("/sla")
async def sla_report(db: AsyncSession = Depends(get_db)) -> dict:
    """Return aggregate SLA compliance statistics."""
    return await analytics_service.get_sla_report(db)


@router.get("/volume")
async def volume_report(db: AsyncSession = Depends(get_db)) -> list:
    """Return ticket volume broken down by channel."""
    return await analytics_service.get_volume_report(db)
