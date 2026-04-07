"""
services/analytics_service.py
------------------------------
Analytics and reporting queries for the support platform.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ticket import Ticket, TicketStatus


async def get_kpis(db: AsyncSession) -> dict:
    """Return high-level KPI metrics for the support dashboard."""
    # All tickets
    all_result = await db.execute(select(Ticket))
    all_tickets = list(all_result.scalars().all())

    total = len(all_tickets)
    open_count = sum(1 for t in all_tickets if t.status == TicketStatus.open)
    in_progress = sum(1 for t in all_tickets if t.status == TicketStatus.in_progress)
    closed_count = sum(1 for t in all_tickets if t.status == TicketStatus.closed)

    # SLA compliance: closed tickets where closed_at <= sla_due_at
    sla_eligible = [
        t for t in all_tickets
        if t.status == TicketStatus.closed
        and t.closed_at is not None
        and t.sla_due_at is not None
    ]
    compliant = sum(1 for t in sla_eligible if t.closed_at <= t.sla_due_at)
    sla_compliance_rate = (compliant / len(sla_eligible) * 100) if sla_eligible else None

    # Average handle time
    handle_times = [
        (t.closed_at - t.created_at).total_seconds() / 60
        for t in all_tickets
        if t.status == TicketStatus.closed
        and t.closed_at is not None
    ]
    avg_handle_time = (sum(handle_times) / len(handle_times)) if handle_times else None

    # Volume by channel
    volume_by_channel: dict[str, int] = defaultdict(int)
    for t in all_tickets:
        key = t.channel.value if t.channel else "unknown"
        volume_by_channel[key] += 1

    # Volume by status
    volume_by_status: dict[str, int] = defaultdict(int)
    for t in all_tickets:
        volume_by_status[t.status.value] += 1

    return {
        "total_tickets": total,
        "open_tickets": open_count,
        "in_progress_tickets": in_progress,
        "closed_tickets": closed_count,
        "sla_compliance_rate": sla_compliance_rate,
        "avg_handle_time_minutes": avg_handle_time,
        "volume_by_channel": dict(volume_by_channel),
        "volume_by_status": dict(volume_by_status),
    }


async def get_sla_report(db: AsyncSession) -> list[dict]:
    """Return per-ticket SLA compliance status."""
    result = await db.execute(select(Ticket))
    tickets = list(result.scalars().all())

    report = []
    for t in tickets:
        compliant: bool | None = None
        if t.closed_at is not None and t.sla_due_at is not None:
            compliant = t.closed_at <= t.sla_due_at
        report.append(
            {
                "ticket_id": t.id,
                "sla_due_at": t.sla_due_at.isoformat() if t.sla_due_at else None,
                "closed_at": t.closed_at.isoformat() if t.closed_at else None,
                "compliant": compliant,
            }
        )
    return report


async def get_volume_report(db: AsyncSession) -> dict:
    """Return ticket volume broken down by channel and by creation date."""
    result = await db.execute(select(Ticket))
    tickets = list(result.scalars().all())

    by_channel: dict[str, int] = defaultdict(int)
    by_day: dict[str, int] = defaultdict(int)

    for t in tickets:
        channel_key = t.channel.value if t.channel else "unknown"
        by_channel[channel_key] += 1

        day_key = t.created_at.astimezone(timezone.utc).strftime("%Y-%m-%d")
        by_day[day_key] += 1

    return {
        "volume_by_channel": dict(by_channel),
        "volume_by_day": dict(by_day),
    }
