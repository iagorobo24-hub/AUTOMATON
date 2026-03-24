# Automaton Database Architecture
## Sistema de Agentes Autoreplicantes - Crypto Trader

---

## 1. VISIÓN GENERAL DE LA ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR (CEREBRO)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Agent Pool  │  │  Strategy   │  │   Market    │  │  Risk       │        │
│  │  Manager    │  │   Engine    │  │   Analyzer  │  │  Controller │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MONGODB COLLECTIONS                             │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │    AGENTS       │  │   STRATEGIES    │  │  MARKET_DATA    │             │
│  │  (Hierarchy)    │  │  (Inheritable)  │  │   (Shared)      │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│  ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐             │
│  │    TRADES       │  │   POSITIONS     │  │    SIGNALS      │             │
│  │  (Per Agent)    │  │  (Per Agent)    │  │   (Shared)      │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│  ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐             │
│  │   WALLETS       │  │  RISK_PROFILES  │  │  PERFORMANCE    │             │
│  │  (Per Agent)    │  │  (Inheritable)  │  │   METRICS       │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  AGENT_LINEAGE  │  │  CLONE_CONFIG   │  │   AUDIT_LOGS    │             │
│  │  (Family Tree)  │  │  (Inheritance)  │  │  (Immutable)    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. COLECCIONES PRINCIPALES

### 2.1 AGENTS (Colección Principal de Agentes)

```javascript
{
  // === IDENTIFICACIÓN ===
  "_id": ObjectId,
  "agent_id": "uuid",                    // ID público único
  "name": "Alpha-Trader-001",
  "display_name": "Alpha Prime",
  "version": "1.0.0",
  
  // === CLASIFICACIÓN ===
  "agent_type": "crypto_trader",         // crypto_trader | business_scout | market_analyzer
  "agent_class": "trader",               // trader | analyzer | scout | hybrid
  "specialization": ["BTC", "ETH"],      // Activos en los que se especializa
  "generation": 1,                       // Generación (1 = original, 2+ = clones)
  
  // === JERARQUÍA Y LINAJE ===
  "lineage": {
    "parent_id": null,                   // null si es agente original
    "root_ancestor_id": "uuid",          // ID del agente fundador de la línea
    "children_ids": ["uuid1", "uuid2"],
    "siblings_ids": [],
    "generation_depth": 0,               // Profundidad en el árbol genealógico
    "clone_count": 5,                    // Número de clones directos creados
    "total_descendants": 12              // Total de descendientes en toda la línea
  },
  
  // === ESTADO Y CICLO DE VIDA ===
  "status": "active",                    // active | replicating | dying | dead | paused | hibernating
  "lifecycle": {
    "created_at": ISODate,
    "activated_at": ISODate,
    "last_active_at": ISODate,
    "death_at": null,
    "death_reason": null,                // bankruptcy | manual | performance | risk_breach
    "resurrection_count": 0,             // Veces que ha sido "revivido"
    "total_uptime_hours": 1250.5
  },
  
  // === FINANCIERO ===
  "finances": {
    "initial_capital": 100.00,
    "current_balance": 156.78,
    "reserved_balance": 20.00,           // Balance reservado para operaciones abiertas
    "available_balance": 136.78,
    "lifetime_deposited": 150.00,
    "lifetime_withdrawn": 0,
    "lifetime_fees_paid": 12.50,
    "currency": "USD"
  },
  
  // === MÉTRICAS DE RENDIMIENTO ===
  "performance": {
    "roi_percent": 56.78,
    "roi_24h": 2.3,
    "roi_7d": 8.5,
    "roi_30d": 23.4,
    "sharpe_ratio": 1.85,
    "sortino_ratio": 2.1,
    "max_drawdown_percent": 15.2,
    "win_rate": 0.68,
    "profit_factor": 2.4,
    "avg_trade_duration_hours": 4.5,
    "trades_per_day_avg": 3.2
  },
  
  // === ESTADÍSTICAS DE TRADING ===
  "trading_stats": {
    "total_trades": 450,
    "winning_trades": 306,
    "losing_trades": 144,
    "open_positions": 3,
    "largest_win": 45.60,
    "largest_loss": -22.30,
    "avg_win": 8.50,
    "avg_loss": -4.20,
    "consecutive_wins_max": 12,
    "consecutive_losses_max": 4,
    "current_streak": 3,                 // Positivo = wins, Negativo = losses
    "streak_type": "win"
  },
  
  // === CONFIGURACIÓN ===
  "config": {
    "strategy_id": "uuid",               // Referencia a estrategia activa
    "risk_profile_id": "uuid",           // Referencia a perfil de riesgo
    "auto_trade": true,
    "max_concurrent_trades": 5,
    "default_position_size_percent": 5,
    "allowed_pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
    "blacklisted_pairs": [],
    "trading_hours": {
      "enabled": false,
      "start_utc": "08:00",
      "end_utc": "22:00",
      "timezone": "UTC"
    }
  },
  
  // === REGLAS DE REPLICACIÓN ===
  "replication_rules": {
    "auto_replicate": true,
    "min_roi_to_replicate": 50.0,        // ROI mínimo para auto-replicarse
    "min_trades_to_replicate": 100,
    "min_age_days": 7,
    "max_children": 10,
    "capital_split_ratio": 0.5,          // 50% del capital va al clon
    "inherit_strategy": true,
    "inherit_risk_profile": true,
    "mutation_enabled": true,            // Permitir variaciones en clones
    "mutation_rate": 0.1                 // 10% de variación en parámetros
  },
  
  // === REGLAS DE MUERTE ===
  "death_rules": {
    "min_balance_usd": 1.00,             // Balance mínimo antes de morir
    "max_drawdown_percent": 80,
    "max_consecutive_losses": 20,
    "inactivity_days_to_die": 30
  },
  
  // === METADATA ===
  "metadata": {
    "tags": ["high-frequency", "btc-specialist"],
    "notes": "",
    "created_by": "user_id or parent_agent_id",
    "last_modified_by": "orchestrator",
    "custom_data": {}
  },
  
  // === TIMESTAMPS ===
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.2 STRATEGIES (Estrategias de Trading)

```javascript
{
  "_id": ObjectId,
  "strategy_id": "uuid",
  "name": "Momentum Breakout v2",
  "description": "Estrategia de ruptura con confirmación de volumen",
  "version": "2.1.0",
  
  // === CLASIFICACIÓN ===
  "type": "momentum",                    // momentum | mean_reversion | arbitrage | trend_following | scalping
  "timeframe": "4h",                     // 1m | 5m | 15m | 1h | 4h | 1d
  "complexity": "intermediate",          // simple | intermediate | advanced
  
  // === HERENCIA ===
  "inheritance": {
    "is_template": true,                 // Si es plantilla base
    "parent_strategy_id": null,
    "derived_count": 15,                 // Cuántas estrategias derivan de esta
    "is_locked": false,                  // Si puede ser modificada
    "shareable": true                    // Si puede ser compartida entre agentes
  },
  
  // === INDICADORES TÉCNICOS ===
  "indicators": [
    {
      "name": "RSI",
      "params": {"period": 14, "overbought": 70, "oversold": 30},
      "weight": 0.3
    },
    {
      "name": "MACD",
      "params": {"fast": 12, "slow": 26, "signal": 9},
      "weight": 0.25
    },
    {
      "name": "EMA",
      "params": {"periods": [20, 50, 200]},
      "weight": 0.25
    },
    {
      "name": "Volume_SMA",
      "params": {"period": 20, "threshold": 1.5},
      "weight": 0.2
    }
  ],
  
  // === REGLAS DE ENTRADA ===
  "entry_rules": {
    "conditions": [
      {
        "indicator": "RSI",
        "condition": "crosses_above",
        "value": 30,
        "required": true
      },
      {
        "indicator": "MACD",
        "condition": "histogram_positive",
        "required": true
      },
      {
        "indicator": "price",
        "condition": "above_ema",
        "params": {"ema_period": 50},
        "required": false
      }
    ],
    "min_conditions_met": 2,
    "confirmation_candles": 1
  },
  
  // === REGLAS DE SALIDA ===
  "exit_rules": {
    "take_profit": {
      "type": "percentage",              // percentage | fixed | trailing | indicator
      "value": 5.0,
      "partial_exits": [
        {"at_percent": 2.5, "close_percent": 50},
        {"at_percent": 5.0, "close_percent": 100}
      ]
    },
    "stop_loss": {
      "type": "percentage",
      "value": 2.0,
      "trailing": {
        "enabled": true,
        "activation_percent": 1.5,
        "trail_percent": 1.0
      }
    },
    "time_exit": {
      "enabled": true,
      "max_hours": 48
    }
  },
  
  // === FILTROS DE MERCADO ===
  "market_filters": {
    "min_volume_24h_usd": 1000000,
    "min_market_cap_usd": 100000000,
    "max_spread_percent": 0.5,
    "avoid_during_news": true,
    "trend_filter": {
      "enabled": true,
      "indicator": "EMA_200",
      "condition": "price_above"
    }
  },
  
  // === BACKTEST RESULTS ===
  "backtest_results": {
    "period_tested": "2023-01-01 to 2024-12-31",
    "total_trades": 1250,
    "win_rate": 0.62,
    "profit_factor": 1.85,
    "max_drawdown": 18.5,
    "sharpe_ratio": 1.65,
    "annual_return_percent": 45.2
  },
  
  // === RENDIMIENTO LIVE ===
  "live_performance": {
    "agents_using": 8,
    "total_trades_all_agents": 3500,
    "avg_roi_percent": 32.5,
    "best_performing_agent_id": "uuid",
    "worst_performing_agent_id": "uuid"
  },
  
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.3 TRADES (Historial de Operaciones)

```javascript
{
  "_id": ObjectId,
  "trade_id": "uuid",
  "agent_id": "uuid",
  "strategy_id": "uuid",
  
  // === IDENTIFICACIÓN DEL TRADE ===
  "symbol": "BTC/USDT",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "exchange": "binance",                 // Para futuro multi-exchange
  
  // === TIPO Y DIRECCIÓN ===
  "side": "long",                        // long | short
  "type": "market",                      // market | limit | stop_market | stop_limit
  "trade_category": "spot",              // spot | futures | margin
  
  // === ENTRADA ===
  "entry": {
    "order_id": "exchange_order_id",
    "price": 42150.50,
    "quantity": 0.0025,
    "value_usd": 105.38,
    "fee": 0.11,
    "fee_currency": "USDT",
    "timestamp": ISODate,
    "slippage_percent": 0.02
  },
  
  // === SALIDA ===
  "exit": {
    "order_id": "exchange_order_id",
    "price": 43500.00,
    "quantity": 0.0025,
    "value_usd": 108.75,
    "fee": 0.11,
    "fee_currency": "USDT",
    "timestamp": ISODate,
    "slippage_percent": 0.01,
    "exit_reason": "take_profit"         // take_profit | stop_loss | trailing_stop | manual | signal | time_exit
  },
  
  // === RESULTADO ===
  "result": {
    "pnl_usd": 3.15,
    "pnl_percent": 2.99,
    "net_pnl_usd": 2.93,                 // Después de fees
    "net_pnl_percent": 2.78,
    "is_winner": true,
    "duration_seconds": 14400,
    "duration_formatted": "4h 0m"
  },
  
  // === GESTIÓN DE RIESGO ===
  "risk_management": {
    "initial_stop_loss": 41100.00,
    "initial_take_profit": 43500.00,
    "risk_reward_ratio": 2.5,
    "position_size_percent": 5.0,
    "max_risk_usd": 2.63
  },
  
  // === CONTEXTO DE MERCADO ===
  "market_context": {
    "trend": "bullish",
    "volatility": "medium",
    "btc_dominance": 48.5,
    "fear_greed_index": 65,
    "volume_24h_change_percent": 15.2
  },
  
  // === SEÑALES QUE ACTIVARON EL TRADE ===
  "signals": [
    {
      "signal_id": "uuid",
      "indicator": "RSI",
      "value": 32,
      "condition_met": "oversold_bounce"
    },
    {
      "signal_id": "uuid",
      "indicator": "MACD",
      "value": "bullish_crossover"
    }
  ],
  
  // === METADATA ===
  "status": "closed",                    // open | closed | cancelled | partial
  "notes": "",
  "tags": ["momentum", "breakout"],
  
  "created_at": ISODate,
  "updated_at": ISODate,
  "closed_at": ISODate
}
```

### 2.4 POSITIONS (Posiciones Abiertas)

```javascript
{
  "_id": ObjectId,
  "position_id": "uuid",
  "agent_id": "uuid",
  "trade_id": "uuid",                    // Referencia al trade de apertura
  
  // === POSICIÓN ===
  "symbol": "ETH/USDT",
  "side": "long",
  "status": "open",                      // open | partial | closing
  
  // === CANTIDADES ===
  "quantity": {
    "initial": 0.5,
    "current": 0.5,
    "closed": 0
  },
  
  // === PRECIOS ===
  "prices": {
    "entry_avg": 2250.00,
    "current": 2340.00,
    "highest": 2380.00,
    "lowest": 2220.00
  },
  
  // === PNL EN TIEMPO REAL ===
  "unrealized_pnl": {
    "usd": 45.00,
    "percent": 4.0,
    "updated_at": ISODate
  },
  
  // === ÓRDENES ACTIVAS ===
  "active_orders": {
    "stop_loss": {
      "order_id": "uuid",
      "price": 2150.00,
      "type": "stop_market"
    },
    "take_profit": {
      "order_id": "uuid",
      "price": 2500.00,
      "type": "limit"
    },
    "trailing_stop": {
      "enabled": true,
      "callback_rate": 2.0,
      "activation_price": 2350.00
    }
  },
  
  // === TIEMPO ===
  "opened_at": ISODate,
  "last_update": ISODate,
  "age_hours": 12.5
}
```

### 2.5 WALLETS (Billeteras por Agente)

```javascript
{
  "_id": ObjectId,
  "wallet_id": "uuid",
  "agent_id": "uuid",
  
  // === BALANCES ===
  "balances": {
    "USDT": {
      "total": 1500.00,
      "available": 1200.00,
      "reserved": 300.00,
      "in_orders": 300.00
    },
    "BTC": {
      "total": 0.025,
      "available": 0.020,
      "reserved": 0.005,
      "in_orders": 0.005,
      "value_usd": 1050.00
    },
    "ETH": {
      "total": 0.5,
      "available": 0.5,
      "reserved": 0,
      "in_orders": 0,
      "value_usd": 1175.00
    }
  },
  
  // === TOTAL EN USD ===
  "total_value_usd": 3725.00,
  "last_valuation_at": ISODate,
  
  // === HISTORIAL DE TRANSACCIONES ===
  "transaction_summary": {
    "total_deposits": 3000.00,
    "total_withdrawals": 500.00,
    "total_trading_fees": 125.00,
    "total_funding_fees": 25.00,
    "net_trading_pnl": 1375.00
  },
  
  // === LÍMITES ===
  "limits": {
    "max_position_value_usd": 500.00,
    "max_daily_loss_usd": 100.00,
    "daily_loss_used": 15.00,
    "daily_reset_at": ISODate
  },
  
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.6 RISK_PROFILES (Perfiles de Riesgo)

```javascript
{
  "_id": ObjectId,
  "risk_profile_id": "uuid",
  "name": "Conservative Trader",
  "description": "Perfil de bajo riesgo para preservación de capital",
  
  // === HERENCIA ===
  "is_template": true,
  "parent_profile_id": null,
  "inheritable": true,
  
  // === LÍMITES DE POSICIÓN ===
  "position_limits": {
    "max_position_size_percent": 5,
    "max_positions_concurrent": 3,
    "max_exposure_single_asset_percent": 20,
    "max_exposure_correlated_assets_percent": 40
  },
  
  // === LÍMITES DE PÉRDIDA ===
  "loss_limits": {
    "max_loss_per_trade_percent": 2,
    "max_daily_loss_percent": 5,
    "max_weekly_loss_percent": 10,
    "max_monthly_loss_percent": 20,
    "max_drawdown_percent": 25
  },
  
  // === ACCIONES EN BREACH ===
  "breach_actions": {
    "on_daily_limit": "pause_trading",   // pause_trading | reduce_size | notify | none
    "on_weekly_limit": "pause_trading",
    "on_drawdown_limit": "stop_and_notify",
    "cooldown_hours": 24
  },
  
  // === VOLATILIDAD ===
  "volatility_adjustments": {
    "enabled": true,
    "high_volatility_reduction": 0.5,    // Reducir tamaño al 50%
    "low_volatility_increase": 1.2       // Aumentar tamaño al 120%
  },
  
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.7 AGENT_LINEAGE (Árbol Genealógico)

```javascript
{
  "_id": ObjectId,
  "lineage_id": "uuid",
  "root_agent_id": "uuid",               // Agente fundador
  "root_agent_name": "Alpha Prime",
  
  // === ÁRBOL COMPLETO ===
  "tree": {
    "agent_id": "uuid",
    "name": "Alpha Prime",
    "generation": 1,
    "created_at": ISODate,
    "status": "active",
    "roi": 156.78,
    "children": [
      {
        "agent_id": "uuid",
        "name": "Alpha-001",
        "generation": 2,
        "created_at": ISODate,
        "status": "active",
        "roi": 45.2,
        "children": [
          {
            "agent_id": "uuid",
            "name": "Alpha-001-A",
            "generation": 3,
            "status": "dead",
            "roi": -80.0,
            "death_reason": "bankruptcy",
            "children": []
          }
        ]
      },
      {
        "agent_id": "uuid",
        "name": "Alpha-002",
        "generation": 2,
        "status": "replicating",
        "roi": 78.5,
        "children": []
      }
    ]
  },
  
  // === ESTADÍSTICAS DE LINAJE ===
  "stats": {
    "total_agents": 15,
    "active_agents": 8,
    "dead_agents": 4,
    "replicating_agents": 3,
    "max_generation": 4,
    "total_capital_managed": 15000.00,
    "combined_roi": 89.5,
    "best_performer_id": "uuid",
    "survival_rate": 0.73
  },
  
  // === GENÉTICA / MUTACIONES ===
  "genetics": {
    "original_strategy_id": "uuid",
    "mutation_history": [
      {
        "generation": 2,
        "agent_id": "uuid",
        "mutation_type": "parameter_adjustment",
        "parameter": "take_profit_percent",
        "original_value": 5.0,
        "mutated_value": 4.5,
        "result": "improved"
      }
    ],
    "successful_mutations": 5,
    "failed_mutations": 2
  },
  
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.8 MARKET_DATA (Datos de Mercado Compartidos)

```javascript
{
  "_id": ObjectId,
  "symbol": "BTC/USDT",
  "exchange": "binance",
  
  // === PRECIO ACTUAL ===
  "ticker": {
    "price": 42500.00,
    "bid": 42498.50,
    "ask": 42501.50,
    "spread_percent": 0.007,
    "volume_24h": 25000000000,
    "change_24h_percent": 2.5,
    "high_24h": 43200.00,
    "low_24h": 41800.00,
    "updated_at": ISODate
  },
  
  // === OHLCV RECIENTE ===
  "ohlcv": {
    "1h": [
      {
        "timestamp": ISODate,
        "open": 42400.00,
        "high": 42600.00,
        "low": 42350.00,
        "close": 42500.00,
        "volume": 1500000000
      }
      // ... últimas 24 velas
    ],
    "4h": [],
    "1d": []
  },
  
  // === INDICADORES PRECALCULADOS ===
  "indicators": {
    "rsi_14": 55.5,
    "macd": {
      "macd": 150.5,
      "signal": 120.3,
      "histogram": 30.2
    },
    "ema_20": 42200.00,
    "ema_50": 41800.00,
    "ema_200": 40500.00,
    "atr_14": 850.00,
    "bollinger": {
      "upper": 43500.00,
      "middle": 42000.00,
      "lower": 40500.00
    },
    "updated_at": ISODate
  },
  
  // === ANÁLISIS DE MERCADO ===
  "analysis": {
    "trend": "bullish",                  // bullish | bearish | sideways
    "trend_strength": 0.7,               // 0-1
    "support_levels": [41000, 40000, 38000],
    "resistance_levels": [44000, 45000, 48000],
    "volatility_regime": "medium",       // low | medium | high | extreme
    "market_phase": "accumulation"       // accumulation | markup | distribution | markdown
  },
  
  // === ORDER BOOK SNAPSHOT ===
  "orderbook_summary": {
    "bid_volume_10_levels": 150.5,
    "ask_volume_10_levels": 145.2,
    "imbalance_ratio": 1.036,
    "updated_at": ISODate
  },
  
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.9 SIGNALS (Señales de Trading)

```javascript
{
  "_id": ObjectId,
  "signal_id": "uuid",
  "symbol": "BTC/USDT",
  
  // === TIPO DE SEÑAL ===
  "type": "entry",                       // entry | exit | alert
  "direction": "long",                   // long | short | neutral
  "strength": 0.85,                      // 0-1 confianza de la señal
  
  // === ORIGEN ===
  "source": {
    "type": "indicator",                 // indicator | pattern | ai_analysis | news
    "name": "RSI_Oversold_Bounce",
    "strategy_id": "uuid"                // Si viene de una estrategia específica
  },
  
  // === DETALLES ===
  "details": {
    "indicator_values": {
      "RSI": 28,
      "MACD_histogram": "bullish_divergence"
    },
    "reasoning": "RSI cruzó por encima de 30 con divergencia alcista en MACD",
    "timeframe": "4h"
  },
  
  // === PRECIOS SUGERIDOS ===
  "suggested_prices": {
    "entry": 42000.00,
    "stop_loss": 41000.00,
    "take_profit": [43000.00, 44000.00],
    "risk_reward": 2.0
  },
  
  // === CONSUMIDORES ===
  "consumed_by": [
    {
      "agent_id": "uuid",
      "consumed_at": ISODate,
      "action_taken": "trade_opened",
      "trade_id": "uuid"
    }
  ],
  
  // === VALIDEZ ===
  "valid_until": ISODate,
  "status": "active",                    // active | consumed | expired | invalidated
  
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.10 CLONE_CONFIG (Configuración de Clonación)

```javascript
{
  "_id": ObjectId,
  "config_id": "uuid",
  "name": "Default Clone Config",
  
  // === HERENCIA DE DATOS ===
  "inheritance": {
    // Qué se hereda del padre
    "strategy": {
      "inherit": true,
      "allow_mutation": true,
      "mutation_params": ["take_profit", "stop_loss", "position_size"]
    },
    "risk_profile": {
      "inherit": true,
      "allow_mutation": false
    },
    "trading_pairs": {
      "inherit": true,
      "allow_expansion": true
    },
    "blacklist": {
      "inherit": true
    }
  },
  
  // === DISTRIBUCIÓN DE CAPITAL ===
  "capital_distribution": {
    "method": "equal_split",             // equal_split | percentage | fixed_amount
    "parent_retention_percent": 50,
    "min_child_capital": 50.00,
    "max_child_capital": 1000.00
  },
  
  // === MUTACIONES GENÉTICAS ===
  "mutations": {
    "enabled": true,
    "rate": 0.1,                         // 10% de variación
    "parameters": {
      "take_profit_percent": {
        "min": 3.0,
        "max": 10.0,
        "step": 0.5
      },
      "stop_loss_percent": {
        "min": 1.0,
        "max": 5.0,
        "step": 0.25
      },
      "position_size_percent": {
        "min": 2.0,
        "max": 10.0,
        "step": 1.0
      }
    }
  },
  
  // === DIVERSIFICACIÓN ===
  "diversification": {
    "strategy_variation": true,          // Clonar con variación de estrategia
    "asset_variation": true,             // Clonar especializándose en diferentes activos
    "timeframe_variation": true          // Clonar con diferentes timeframes
  },
  
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2.11 AUDIT_LOGS (Registros de Auditoría)

```javascript
{
  "_id": ObjectId,
  "log_id": "uuid",
  
  // === EVENTO ===
  "event_type": "agent_replicated",      // Ver lista completa abajo
  "event_category": "lifecycle",         // lifecycle | trading | financial | config | system
  
  // === ACTOR ===
  "actor": {
    "type": "agent",                     // agent | orchestrator | user | system
    "id": "uuid",
    "name": "Alpha Prime"
  },
  
  // === OBJETIVO ===
  "target": {
    "type": "agent",
    "id": "uuid",
    "name": "Alpha-001"
  },
  
  // === DETALLES ===
  "details": {
    "action": "replication",
    "parent_balance_before": 200.00,
    "parent_balance_after": 100.00,
    "child_initial_balance": 100.00,
    "inherited_strategy": "uuid",
    "mutations_applied": []
  },
  
  // === RESULTADO ===
  "result": "success",                   // success | failure | partial
  "error_message": null,
  
  // === INMUTABLE ===
  "created_at": ISODate,
  "hash": "sha256_hash_for_integrity"    // Hash para verificar integridad
}

// TIPOS DE EVENTOS:
// lifecycle: agent_created, agent_replicated, agent_died, agent_resurrected, agent_paused
// trading: trade_opened, trade_closed, position_modified, order_placed, order_cancelled
// financial: deposit, withdrawal, fee_charged, balance_transfer, capital_split
// config: strategy_changed, risk_profile_changed, settings_updated
// system: signal_generated, market_data_updated, error_occurred
```

### 2.12 ORCHESTRATOR_STATE (Estado del Orquestador)

```javascript
{
  "_id": ObjectId,
  "orchestrator_id": "main",
  
  // === ESTADO GLOBAL ===
  "status": "active",
  "mode": "auto",                        // auto | semi_auto | manual | maintenance
  
  // === MÉTRICAS GLOBALES ===
  "global_metrics": {
    "total_agents": 50,
    "active_agents": 35,
    "total_capital_managed": 125000.00,
    "daily_pnl": 1250.00,
    "weekly_pnl": 5600.00,
    "monthly_pnl": 18500.00,
    "system_health": 0.95
  },
  
  // === LÍMITES GLOBALES ===
  "global_limits": {
    "max_agents": 100,
    "max_capital_per_agent": 10000.00,
    "max_daily_loss_total": 5000.00,
    "emergency_stop_drawdown": 20
  },
  
  // === COLA DE TAREAS ===
  "task_queue": {
    "pending_replications": 3,
    "pending_terminations": 1,
    "pending_rebalances": 5
  },
  
  // === LLM USAGE ===
  "llm_stats": {
    "tokens_used_today": 15000,
    "tokens_used_month": 450000,
    "cost_estimate_month": 4.50,
    "primary_model": "gpt-4o",
    "fallback_models": ["gpt-4o-mini", "claude-sonnet"]
  },
  
  "last_health_check": ISODate,
  "updated_at": ISODate
}
```

---

## 3. ÍNDICES RECOMENDADOS

```javascript
// agents
db.agents.createIndex({ "agent_id": 1 }, { unique: true })
db.agents.createIndex({ "status": 1 })
db.agents.createIndex({ "agent_type": 1 })
db.agents.createIndex({ "lineage.parent_id": 1 })
db.agents.createIndex({ "lineage.root_ancestor_id": 1 })
db.agents.createIndex({ "performance.roi_percent": -1 })
db.agents.createIndex({ "created_at": -1 })

// trades
db.trades.createIndex({ "trade_id": 1 }, { unique: true })
db.trades.createIndex({ "agent_id": 1, "created_at": -1 })
db.trades.createIndex({ "symbol": 1, "created_at": -1 })
db.trades.createIndex({ "status": 1 })
db.trades.createIndex({ "strategy_id": 1 })

// positions
db.positions.createIndex({ "position_id": 1 }, { unique: true })
db.positions.createIndex({ "agent_id": 1, "status": 1 })
db.positions.createIndex({ "symbol": 1 })

// signals
db.signals.createIndex({ "signal_id": 1 }, { unique: true })
db.signals.createIndex({ "symbol": 1, "status": 1, "created_at": -1 })
db.signals.createIndex({ "valid_until": 1 }, { expireAfterSeconds: 0 })

// market_data
db.market_data.createIndex({ "symbol": 1, "exchange": 1 }, { unique: true })
db.market_data.createIndex({ "updated_at": 1 })

// audit_logs
db.audit_logs.createIndex({ "created_at": -1 })
db.audit_logs.createIndex({ "actor.id": 1, "created_at": -1 })
db.audit_logs.createIndex({ "event_type": 1, "created_at": -1 })
```

---

## 4. FLUJO DE REPLICACIÓN

```
┌──────────────────────────────────────────────────────────────────┐
│                    FLUJO DE AUTO-REPLICACIÓN                      │
└──────────────────────────────────────────────────────────────────┘

1. TRIGGER: Agente alcanza ROI > 50% con > 100 trades

2. VALIDACIÓN:
   ├── ¿Balance suficiente? (>= min_child_capital * 2)
   ├── ¿No excede max_children?
   ├── ¿Edad mínima cumplida?
   └── ¿Sistema permite más agentes?

3. PREPARACIÓN:
   ├── Calcular capital a transferir
   ├── Cargar configuración de clonación
   └── Determinar mutaciones (si aplica)

4. CREACIÓN DEL CLON:
   ├── Crear documento en 'agents'
   ├── Heredar estrategia (con mutaciones)
   ├── Heredar perfil de riesgo
   ├── Crear wallet con capital inicial
   └── Registrar en 'agent_lineage'

5. ACTUALIZACIÓN DEL PADRE:
   ├── Reducir balance
   ├── Añadir child_id a children_ids
   └── Incrementar clone_count

6. AUDIT:
   └── Registrar evento en 'audit_logs'

7. ACTIVACIÓN:
   └── Nuevo agente comienza a operar
```

---

## 5. DIAGRAMA DE RELACIONES

```
                                    ┌─────────────────┐
                                    │  ORCHESTRATOR   │
                                    │     STATE       │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
           ┌───────────────┐        ┌───────────────┐        ┌───────────────┐
           │    AGENTS     │◄──────►│  STRATEGIES   │        │  RISK_PROFILES│
           └───────┬───────┘        └───────────────┘        └───────────────┘
                   │
     ┌─────────────┼─────────────┬─────────────┬─────────────┐
     │             │             │             │             │
     ▼             ▼             ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐
│ TRADES  │  │POSITIONS│  │ WALLETS │  │ LINEAGE │  │ AUDIT_LOGS  │
└────┬────┘  └─────────┘  └─────────┘  └─────────┘  └─────────────┘
     │
     ▼
┌─────────────┐
│  SIGNALS    │◄─────────┐
└─────────────┘          │
                         │
              ┌──────────┴──────────┐
              │    MARKET_DATA      │
              └─────────────────────┘
```

---

## 6. CONSIDERACIONES DE ESCALABILIDAD

1. **Sharding**: Cuando supere 1M de trades, considerar sharding por `agent_id`
2. **Time-Series**: Usar colección time-series para `market_data` y `ohlcv`
3. **Archivado**: Mover trades cerrados >90 días a colección de archivo
4. **Caché**: Redis para `market_data` y `signals` activas
5. **Agregaciones**: Pre-calcular métricas diarias en colección separada

---

Este documento define la estructura completa. ¿Procedemos con la implementación?
