from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import os
import uuid
from datetime import datetime, timezone
from ..services.database import DatabaseService
from ..api.deps import get_db_service
from ..core.config import settings

router = APIRouter()


@router.post("/")
async def chat_with_orchestrator(
    message: str,
    session_id: Optional[str] = None,
    db_service: DatabaseService = Depends(get_db_service),
):
    """Chat with the orchestrator AI"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    api_key = settings.EMERGENT_LLM_KEY or os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")

    session_id = session_id or str(uuid.uuid4())

    # Get context
    stats = await db_service.get_dashboard_stats()

    system_message = f"""Eres el Orquestador Principal de Automaton, un sistema de agentes autoreplicantes con capacidades de trading crypto.

Tu rol:
1. Gestionar el ecosistema de agentes (crear, replicar, destruir según rendimiento)
2. Analizar mercados crypto y detectar oportunidades
3. Investigar nuevos modelos de negocio para autoreplicación
4. Optimizar el uso de recursos y tokens de LLM
5. Proporcionar análisis estratégicos

Estado actual del sistema:
- Agentes activos: {stats["agents"]["active"]} de {stats["agents"]["total"]}
- Balance total: ${stats["finances"]["total_balance"]:.2f}
- ROI promedio: {stats["finances"]["avg_roi"]:.1f}%
- Trades totales: {stats["trading"]["total_trades"]}
- Tasa de éxito: {stats["trading"]["win_rate"] * 100:.1f}%
- Generaciones: {stats["lineage"]["total_generations"]}
- Replicaciones: {stats["lineage"]["total_replications"]}

Responde de forma concisa, técnica y orientada a la acción. Usa datos cuando estén disponibles."""

    chat = LlmChat(
        api_key=api_key, session_id=session_id, system_message=system_message
    ).with_model("openai", "gpt-4o")

    user_message = UserMessage(text=message)
    response = await chat.send_message(user_message)

    # Save chat and track usage directly using db client
    await db_service.db.chat_history.insert_one(
        {
            "session_id": session_id,
            "message": message,
            "response": response,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    await db_service.db.llm_usage.insert_one(
        {
            "id": str(uuid.uuid4()),
            "provider": "openai",
            "model": "gpt-4o",
            "tokens_used": len(message.split()) + len(response.split()),
            "cost_estimate": 0.001,
            "task_type": "orchestrator_chat",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    return {"response": response, "session_id": session_id}
