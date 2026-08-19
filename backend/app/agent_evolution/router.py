from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.agent_evolution.fitness import FitnessError, FitnessService
from app.agent_evolution.policy import active_evolution_policy
from app.database import get_session
from app.models import Agent, AgentFitnessEvaluation, AgentLineage

router = APIRouter()


def _decimal(value):
    return None if value is None else format(Decimal(value), "f")


def _policy_payload(policy) -> dict:
    return {
        "id": policy.id,
        "version": policy.version,
        "active": policy.active,
        "min_backtest_round_trips": policy.min_backtest_round_trips,
        "min_backtest_net_return": _decimal(policy.min_backtest_net_return),
        "min_backtest_expectancy": _decimal(policy.min_backtest_expectancy),
        "max_backtest_drawdown": _decimal(policy.max_backtest_drawdown),
        "min_paper_closed_trades": policy.min_paper_closed_trades,
        "min_paper_realized_pnl": _decimal(policy.min_paper_realized_pnl),
        "child_allocation_fraction": _decimal(policy.child_allocation_fraction),
    }


def _fitness_payload(item: AgentFitnessEvaluation) -> dict:
    return {
        "id": item.id,
        "agent_id": item.agent_id,
        "policy_version": item.policy_version,
        "backtest_run_id": item.backtest_run_id,
        "strategy_id": item.strategy_id,
        "strategy_version": item.strategy_version,
        "strategy_code_sha256": item.strategy_code_sha256,
        "backtest_round_trips": item.backtest_round_trips,
        "backtest_net_return": _decimal(item.backtest_net_return),
        "backtest_expectancy": _decimal(item.backtest_expectancy),
        "backtest_max_drawdown": _decimal(item.backtest_max_drawdown),
        "paper_closed_trades": item.paper_closed_trades,
        "paper_realized_pnl": _decimal(item.paper_realized_pnl),
        "decision": item.decision,
        "reason_codes": item.reason_codes,
        "consumed_by_lineage_id": item.consumed_by_lineage_id,
        "created_at": item.created_at.isoformat(),
    }


def _lineage_payload(item: AgentLineage) -> dict:
    return {
        "id": item.id,
        "parent_agent_id": item.parent_agent_id,
        "child_agent_id": item.child_agent_id,
        "generation": item.generation,
        "strategy_id": item.strategy_id,
        "strategy_version": item.strategy_version,
        "strategy_code_sha256": item.strategy_code_sha256,
        "policy_version": item.policy_version,
        "fitness_evaluation_id": item.fitness_evaluation_id,
        "allocated_capital": _decimal(item.allocated_capital),
        "created_at": item.created_at.isoformat(),
    }


@router.get("/status")
def status(session: Session = Depends(get_session)) -> dict:
    policy = active_evolution_policy(session)
    return {
        "mode": "evidence_phase_6",
        "policy_version": policy.version,
        "replication": "evidence_gated_manual",
        "capital_policy": "funded_liquid_transfer",
        "strategy_mutation": "disabled",
        "automated_trading": "disabled",
        "live_execution": "disabled",
    }


@router.get("/policies/active")
def get_active_policy(session: Session = Depends(get_session)) -> dict:
    return _policy_payload(active_evolution_policy(session))


@router.post("/agents/{agent_id}/fitness")
def evaluate_fitness(agent_id: int, session: Session = Depends(get_session)) -> dict:
    try:
        evaluation = FitnessService(session).evaluate(agent_id)
    except FitnessError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _fitness_payload(evaluation)


@router.get("/agents/{agent_id}/fitness")
def list_fitness(
    agent_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[dict]:
    if session.get(Agent, agent_id) is None:
        raise HTTPException(status_code=404, detail="agent not found")
    items = session.exec(
        select(AgentFitnessEvaluation)
        .where(AgentFitnessEvaluation.agent_id == agent_id)
        .order_by(AgentFitnessEvaluation.id.desc())
        .limit(limit)
    ).all()
    return [_fitness_payload(item) for item in items]


@router.get("/agents/{agent_id}/lineage")
def get_lineage(agent_id: int, session: Session = Depends(get_session)) -> dict:
    if session.get(Agent, agent_id) is None:
        raise HTTPException(status_code=404, detail="agent not found")
    children = session.exec(
        select(AgentLineage)
        .where(AgentLineage.parent_agent_id == agent_id)
        .order_by(AgentLineage.id)
    ).all()
    parent_link = session.exec(
        select(AgentLineage).where(AgentLineage.child_agent_id == agent_id)
    ).first()
    return {
        "as_parent": [_lineage_payload(item) for item in children],
        "as_child": _lineage_payload(parent_link) if parent_link else None,
    }
