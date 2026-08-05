from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.audit import AuditLog
from app.models.conversation import Conversation, Message
from app.models.document import Document, DocumentChunk
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _admin_or_manager(user: User) -> None:
    if user.role.name not in ("super_admin", "data_manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/analytics/overview")
async def analytics_overview(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _admin_or_manager(user)

    total_docs = await db.scalar(select(func.count(Document.id)))
    active_docs = await db.scalar(
        select(func.count(Document.id)).where(Document.status == "active")
    )
    total_convos = await db.scalar(select(func.count(Conversation.id)))
    questions_today = await db.scalar(
        select(func.count(Message.id)).where(
            Message.role == "user",
            func.date(Message.created_at) == func.current_date(),
        )
    )
    total_chunks = await db.scalar(select(func.count()).select_from(DocumentChunk))
    questions_total = await db.scalar(
        select(func.count(Message.id)).where(Message.role == "user")
    )

    return {
        "total_documents": total_docs or 0,
        "active_documents": active_docs or 0,
        "total_chunks": total_chunks or 0,
        "total_conversations": total_convos or 0,
        "questions_today": questions_today or 0,
        "questions_total": questions_total or 0,
    }


@router.get("/analytics/faq")
async def analytics_faq(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Top questions by frequency, aggregated from message content."""
    _admin_or_manager(user)

    sql = text("""
        SELECT content, COUNT(*) AS cnt
        FROM messages
        WHERE role = 'user'
        GROUP BY content
        ORDER BY cnt DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, {"limit": limit})
    return [
        {"question": row[0], "count": row[1]}
        for row in result.fetchall()
    ]


@router.get("/analytics/unanswered")
async def analytics_unanswered(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Recent questions that got a 'not found' response."""
    _admin_or_manager(user)

    # Find assistant messages containing "tidak ditemukan" that follow user messages
    sql = text("""
        SELECT m_user.content AS question, m_ai.content AS answer, m_ai.created_at
        FROM messages m_ai
        JOIN messages m_user
            ON m_user.conversation_id = m_ai.conversation_id
            AND m_user.role = 'user'
            AND m_user.created_at < m_ai.created_at
        WHERE m_ai.role = 'assistant'
          AND m_ai.content ILIKE '%tidak ditemukan%'
        ORDER BY m_ai.created_at DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, {"limit": limit})
    return [
        {
            "question": row[0],
            "answer": row[1][:200] + ("..." if len(row[1]) > 200 else ""),
            "created_at": row[2].isoformat(),
        }
        for row in result.fetchall()
    ]


@router.get("/analytics/per-day")
async def analytics_per_day(
    days: int = Query(14, ge=1, le=90),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Question count per day for charts."""
    _admin_or_manager(user)

    sql = text("""
        SELECT DATE(created_at) AS day, COUNT(*) AS cnt
        FROM messages
        WHERE role = 'user'
          AND created_at >= CURRENT_DATE - :days * INTERVAL '1 day'
        GROUP BY day
        ORDER BY day
    """)
    result = await db.execute(sql, {"days": days})
    return [
        {"date": str(row[0]), "count": row[1]}
        for row in result.fetchall()
    ]


@router.get("/analytics/weekly-report")
async def analytics_weekly_report(
    weeks: int = Query(4, ge=1, le=12),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Weekly report: total questions, unique users, top topics per week."""
    _admin_or_manager(user)

    sql = text("""
        SELECT
            DATE_TRUNC('week', m.created_at) AS week_start,
            COUNT(*) AS total_questions,
            COUNT(DISTINCT c.user_id) AS unique_users,
            COUNT(DISTINCT m.conversation_id) AS conversations
        FROM messages m
        JOIN conversations c ON c.id = m.conversation_id
        WHERE m.role = 'user'
          AND m.created_at >= CURRENT_DATE - :weeks * 7 * INTERVAL '1 day'
        GROUP BY week_start
        ORDER BY week_start DESC
    """)
    result = await db.execute(sql, {"weeks": weeks})
    return [
        {
            "week_start": str(row[0].date()) if row[0] else None,
            "total_questions": row[1],
            "unique_users": row[2],
            "conversations": row[3],
        }
        for row in result.fetchall()
    ]


@router.get("/analytics/trends")
async def analytics_trends(
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Trend analysis: topics rising or falling in popularity.

    Compares recent period (half) vs previous period (half).
    """
    _admin_or_manager(user)

    # Get keyword frequency for recent half vs older half
    half_days = days // 2

    sql_recent = text("""
        SELECT LOWER(TRIM(content)) AS question, COUNT(*) AS cnt
        FROM messages
        WHERE role = 'user'
          AND created_at >= CURRENT_DATE - :half_days * INTERVAL '1 day'
        GROUP BY question
        HAVING COUNT(*) >= 2
        ORDER BY cnt DESC
        LIMIT 20
    """)

    sql_older = text("""
        SELECT LOWER(TRIM(content)) AS question, COUNT(*) AS cnt
        FROM messages
        WHERE role = 'user'
          AND created_at >= CURRENT_DATE - :days * INTERVAL '1 day'
          AND created_at < CURRENT_DATE - :half_days * INTERVAL '1 day'
        GROUP BY question
        HAVING COUNT(*) >= 2
        ORDER BY cnt DESC
        LIMIT 20
    """)

    recent = await db.execute(sql_recent, {"half_days": half_days})
    older = await db.execute(sql_older, {"days": days, "half_days": half_days})

    recent_map = {row[0]: row[1] for row in recent.fetchall()}
    older_map = {row[0]: row[1] for row in older.fetchall()}

    trends = []
    all_questions = set(list(recent_map.keys()) + list(older_map.keys()))
    for q in all_questions:
        r = recent_map.get(q, 0)
        o = older_map.get(q, 0)
        if r == 0 and o == 0:
            continue
        # Calculate trend: positive = rising, negative = falling
        if o == 0:
            trend = "new"
            change = r
        elif r == 0:
            trend = "gone"
            change = -o
        else:
            change = r - o
            trend = "rising" if change > 0 else "falling" if change < 0 else "stable"

        trends.append({
            "question": q[:100],
            "recent_count": r,
            "older_count": o,
            "change": change,
            "trend": trend,
        })

    # Sort by absolute change (most significant first)
    trends.sort(key=lambda x: abs(x["change"]), reverse=True)
    return trends[:15]


@router.get("/analytics/satisfaction")
async def analytics_satisfaction(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """User satisfaction trend from feedback (thumbs up/down)."""
    _admin_or_manager(user)

    sql = text("""
        SELECT
            DATE(created_at) AS day,
            feedback,
            COUNT(*) AS cnt
        FROM messages
        WHERE feedback IS NOT NULL
          AND created_at >= CURRENT_DATE - :days * INTERVAL '1 day'
        GROUP BY day, feedback
        ORDER BY day
    """)
    result = await db.execute(sql, {"days": days})

    # Group by day
    daily: dict[str, dict] = {}
    for row in result.fetchall():
        day = str(row[0])
        if day not in daily:
            daily[day] = {"date": day, "up": 0, "down": 0, "total": 0, "satisfaction": 0}
        daily[day][row[1]] = row[2]
        daily[day]["total"] += row[2]

    # Calculate satisfaction percentage
    for d in daily.values():
        if d["total"] > 0:
            d["satisfaction"] = round((d["up"] / d["total"]) * 100, 1)

    return sorted(daily.values(), key=lambda x: x["date"])


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: str | None = Query(None),
    user_id: str | None = Query(None),
    entity_type: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role.name != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    stmt = select(AuditLog)

    if action:
        stmt = stmt.where(AuditLog.action == action)
    if user_id:
        from uuid import UUID

        stmt = stmt.where(AuditLog.user_id == UUID(user_id))
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if date_from:
        stmt = stmt.where(AuditLog.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(AuditLog.created_at <= datetime.fromisoformat(date_to))

    stmt = stmt.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    # Enrich with usernames
    user_ids = [str(log.user_id) for log in logs if log.user_id]
    usernames: dict[str, str] = {}
    if user_ids:
        from uuid import UUID

        user_result = await db.execute(
            select(User.id, User.username).where(User.id.in_([UUID(uid) for uid in user_ids]))
        )
        usernames = {str(row[0]): row[1] for row in user_result.fetchall()}

    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "username": usernames.get(str(log.user_id)),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
