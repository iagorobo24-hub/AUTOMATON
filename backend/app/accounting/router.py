from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Account, Agent, LedgerEntry, Position


router = APIRouter()


def _decimal(value) -> str:
    return str(value)


@router.get("/agents/{agent_id}")
def get_agent_account(
    agent_id: int,
    session: Session = Depends(get_session),
) -> dict:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    account = session.exec(
        select(Account).where(Account.agente_id == agent_id)
    ).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Cuenta contable no encontrada")

    positions = session.exec(
        select(Position)
        .where(Position.account_id == account.id)
        .order_by(Position.symbol)
    ).all()
    ledger = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.account_id == account.id)
        .order_by(LedgerEntry.id)
    ).all()

    return {
        "account": {
            "id": account.id,
            "agente_id": account.agente_id,
            "currency": account.currency,
            "initial_capital": _decimal(account.initial_capital),
            "funded_capital": _decimal(account.funded_capital),
            "cash": _decimal(account.cash),
            "reserved_cash": _decimal(account.reserved_cash),
            "realized_pnl": _decimal(account.realized_pnl),
            "fees_paid": _decimal(account.fees_paid),
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat(),
        },
        "positions": [
            {
                "id": position.id,
                "symbol": position.symbol,
                "quantity": _decimal(position.quantity),
                "average_cost": _decimal(position.average_cost),
                "realized_pnl": _decimal(position.realized_pnl),
                "updated_at": position.updated_at.isoformat(),
            }
            for position in positions
        ],
        "ledger": [
            {
                "id": entry.id,
                "entry_type": entry.entry_type,
                "amount": _decimal(entry.amount),
                "reason": entry.reason,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in ledger
        ],
        "execution_mutations": "not_exposed_phase_2",
    }
