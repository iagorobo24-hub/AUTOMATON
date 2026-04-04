from fastapi import APIRouter, Depends
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from ..services.database import DatabaseService
from ..api.deps import get_db_service

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get comprehensive dashboard statistics"""
    stats = await db_service.get_dashboard_stats()
    
    # Update orchestrator metrics
    await db_service.update_orchestrator_metrics()
    
    # Get LLM usage stats from db (accessible via db_service.db)
    llm_usage = await db_service.db.llm_usage.find({}, {"_id": 0}).to_list(1000)
    total_tokens = sum(u.get("tokens_used", 0) for u in llm_usage)
    
    # Calculate PnL periods
    trades = await db_service.get_all_trades(limit=1000)
    now = datetime.now(timezone.utc)
    
    pnl_24h = sum(
        t.get('result', {}).get('pnl_usd', 0) 
        for t in trades 
        if t.get('created_at') and (now - datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))).days < 1
    )
    
    pnl_7d = sum(
        t.get('result', {}).get('pnl_usd', 0) 
        for t in trades 
        if t.get('created_at') and (now - datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))).days < 7
    )
    
    # Add extended stats
    stats["trading"]["pnl_24h"] = pnl_24h
    stats["trading"]["pnl_7d"] = pnl_7d
    stats["llm"] = {
        "total_tokens": total_tokens,
        "total_calls": len(llm_usage),
        "cost_estimate": total_tokens * 0.00001
    }
    
    return stats

@router.get("/portfolio-history")
async def get_portfolio_history(
    period: str = "7d",
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get portfolio value history based on trades"""
    now = datetime.now(timezone.utc)
    periods = {
        "1d": timedelta(days=1),
        "7d": timedelta(days=7),
        "1m": timedelta(days=30),
        "3m": timedelta(days=90),
        "all": timedelta(days=365)
    }
    delta = periods.get(period, timedelta(days=7))
    start_date = now - delta
    
    # Get all trades
    trades = await db_service.db.trades.find(
        {"created_at": {"$gte": start_date.isoformat()}},
        {"_id": 0}
    ).sort("created_at", 1).to_list(10000)
    
    # Get all agents for initial capital
    agents = await db_service.get_agents()
    initial_capital = sum(a.get('finances', {}).get('initial_capital', 0) or a.get('initial_balance', 100) for a in agents)
    
    # Build cumulative PnL over time
    history = []
    cumulative_pnl = 0
    
    if period == "1d":
        interval_seconds = 3600
    elif period in ["7d", "1m"]:
        interval_seconds = 14400
    else:
        interval_seconds = 86400
    
    current_time = start_date
    trade_index = 0
    
    while current_time <= now:
        bucket_end = current_time + timedelta(seconds=interval_seconds)
        
        while trade_index < len(trades):
            trade_time = datetime.fromisoformat(trades[trade_index]['created_at'].replace('Z', '+00:00'))
            if trade_time < bucket_end:
                pnl = trades[trade_index].get('result', {}).get('pnl_usd', 0)
                cumulative_pnl += pnl
                trade_index += 1
            else:
                break
        
        history.append({
            "timestamp": current_time.isoformat(),
            "time": current_time.strftime("%H:%M" if period == "1d" else "%m/%d"),
            "value": initial_capital + cumulative_pnl,
            "pnl": cumulative_pnl
        })
        
        current_time = bucket_end
    
    if not history or len(history) < 2:
        points = 24 if period == "1d" else 7 if period == "7d" else 30
        history = []
        for i in range(points):
            t = start_date + timedelta(seconds=interval_seconds * i)
            history.append({
                "timestamp": t.isoformat(),
                "time": t.strftime("%H:%M" if period == "1d" else "%m/%d"),
                "value": initial_capital,
                "pnl": 0
            })
    
    return {
        "period": period,
        "initial_capital": initial_capital,
        "current_value": initial_capital + cumulative_pnl,
        "total_pnl": cumulative_pnl,
        "pnl_percent": (cumulative_pnl / initial_capital * 100) if initial_capital > 0 else 0,
        "history": history
    }
