from fastapi import APIRouter, Depends
from typing import List, Optional
from ..services.database import DatabaseService
from ..api.deps import get_db_service

router = APIRouter()


@router.get("/")
async def get_audit_logs(
    agent_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    db_service: DatabaseService = Depends(get_db_service),
):
    """Get audit logs with optional filters"""
    logs = await db_service.get_audit_logs(agent_id, event_type, limit)
    return {"logs": logs}


@router.get("/llm-usage")
async def get_llm_usage(db_service: DatabaseService = Depends(get_db_service)):
    """Get LLM usage statistics"""
    usage = await db_service.db.llm_usage.find({}, {"_id": 0}).to_list(100)

    by_provider = {}
    total_tokens = 0
    total_cost = 0

    for u in usage:
        provider = u.get("provider", "unknown")
        if provider not in by_provider:
            by_provider[provider] = {"tokens": 0, "cost": 0, "calls": 0}
        by_provider[provider]["tokens"] += u.get("tokens_used", 0)
        by_provider[provider]["cost"] += u.get("cost_estimate", 0)
        by_provider[provider]["calls"] += 1
        total_tokens += u.get("tokens_used", 0)
        total_cost += u.get("cost_estimate", 0)

    return {
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "by_provider": by_provider,
        "recent": usage[-10:] if usage else [],
    }
