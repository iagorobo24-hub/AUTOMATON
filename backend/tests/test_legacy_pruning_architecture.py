from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_APP = REPO_ROOT / "backend" / "app"
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"


DELETED_BACKEND_PATHS = [
    "routers/simulation.py",
    "routers/paper_trading.py",
    "routers/trading.py",
    "routers/risk.py",
    "routers/auth.py",
    "routers/chat.py",
    "routers/payments.py",
    "routers/notifications.py",
    "routers/dashboard.py",
    "routers/strategies.py",
    "routers/audit.py",
    "routers/signals.py",
    "routers/system.py",
    "services/paper_engine.py",
    "services/trading_engine.py",
    "services/replication.py",
    "services/mock_engine.py",
    "services/registry.py",
    "services/portfolio_snapshot.py",
    "services/risk_manager.py",
    "services/agent_engine.py",
    "services/agent_replication.py",
    "services/binance_service.py",
    "services/database.py",
    "services/notifications.py",
    "services/auth_service.py",
    "services/strategy_alpha.py",
    "services/strategy_beta.py",
    "services/strategy_gamma.py",
    "services/indicators.py",
    "services/regime_detector.py",
    "api/api.py",
    "api/deps.py",
    "api/deps_sql.py",
    "core/config.py",
    "core/seed.py",
    "models/auth.py",
    "models/agent.py",
    "models/requests.py",
    "models/system.py",
    "models/trading.py",
    "models/finance.py",
]

DELETED_FRONTEND_PATHS = [
    "pages/ActivityPage.jsx",
    "pages/Agents.jsx",
    "pages/ChatPage.jsx",
    "pages/CryptoPage.jsx",
    "pages/Dashboard.jsx",
    "pages/DashboardPage.jsx",
    "pages/LoginPage.jsx",
    "pages/Memory.jsx",
    "pages/Settings.jsx",
    "pages/SimulationPage.jsx",
    "pages/Trades.jsx",
    "pages/WalletPage.jsx",
    "lib/mockData.js",
    "lib/types.js",
    "hooks/useAppMode.js",
    "hooks/use-crypto.js",
    "hooks/usePullToRefresh.js",
]

DELETED_LEGACY_TESTS = [
    "test_auth.py",
    "test_config.py",
    "test_replication_service.py",
    "test_trading_engine.py",
]


def test_superseded_backend_architecture_is_physically_removed():
    remaining = [path for path in DELETED_BACKEND_PATHS if (BACKEND_APP / path).exists()]
    assert remaining == [], f"legacy backend files still present: {remaining}"
    assert not (REPO_ROOT / "backend" / "test_strategies.py").exists()


def test_obsolete_legacy_tests_are_physically_removed():
    tests_dir = REPO_ROOT / "backend" / "tests"
    remaining = [name for name in DELETED_LEGACY_TESTS if (tests_dir / name).exists()]
    assert remaining == [], f"legacy tests still present: {remaining}"


def test_unreachable_legacy_frontend_surfaces_are_physically_removed():
    remaining = [path for path in DELETED_FRONTEND_PATHS if (FRONTEND_SRC / path).exists()]
    assert remaining == [], f"legacy frontend files still present: {remaining}"


def test_active_main_has_no_legacy_database_or_synthetic_engine_imports():
    source = (BACKEND_APP / "main.py").read_text(encoding="utf-8")
    for forbidden in (
        "motor", "pymongo", "DatabaseService", "AgentEngine", "mock_engine",
        "paper_engine", "trading_engine", "binance_service",
    ):
        assert forbidden not in source
    assert 'LEGACY_PRUNING_MODE = "pruned_phase_9"' in source
    assert 'LIVE_EXECUTION_MODE = "disabled"' in source


def test_active_financial_and_evidence_domains_do_not_import_legacy_engines():
    protected_dirs = [
        "accounting", "market_data", "paper_execution", "risk", "backtesting",
        "agent_evolution", "paper_runtime", "strategy_research",
    ]
    forbidden = (
        "services.database", "services.mock_engine", "services.paper_engine",
        "services.trading_engine", "services.binance_service", "services.agent_engine",
        "motor.motor_asyncio", "pymongo",
    )
    offenders = []
    for directory in protected_dirs:
        for path in (BACKEND_APP / directory).rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in source:
                    offenders.append(f"{path.relative_to(REPO_ROOT)} -> {token}")
    assert offenders == []


def test_active_strategy_enum_module_is_preserved_for_sqlmodel_contract():
    assert (BACKEND_APP / "models" / "enums.py").exists()
    sql_models = (BACKEND_APP / "models" / "sql_models.py").read_text(encoding="utf-8")
    assert "from app.models.enums import AgentStatus, StrategyEnum, TradeType" in sql_models


def test_only_active_strategy_service_remains_in_services_package():
    service_files = sorted(path.name for path in (BACKEND_APP / "services").glob("*.py"))
    assert service_files == ["__init__.py", "strategies.py"]


def test_runtime_requirements_do_not_keep_deleted_legacy_subsystems():
    requirements = (REPO_ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8").lower()
    for package in (
        "motor==", "pymongo==", "pyjwt==", "passlib", "python-multipart==",
        "python-binance==", "slowapi==", "pydantic-settings==",
    ):
        assert package not in requirements
