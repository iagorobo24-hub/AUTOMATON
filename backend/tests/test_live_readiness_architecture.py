from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
APP = BACKEND / 'app'


def _text_tree(root: Path, suffixes={'.py'}):
    return '\n'.join(path.read_text(encoding='utf-8') for path in root.rglob('*') if path.is_file() and path.suffix in suffixes)


def test_live_phase10_has_no_real_order_transport_or_secret_storage_surface():
    live = _text_tree(APP / 'live_execution')
    lowered = live.lower()
    for forbidden in ('def create_order(', 'def place_order(', 'def submit_order(', 'api_secret', 'secret_key=', 'private_key='):
        assert forbidden not in lowered
    router = (APP / 'live_execution' / 'router.py').read_text(encoding='utf-8').lower()
    for forbidden_route in ('@router.post("/orders")', '@router.post("/buy")', '@router.post("/sell")', '@router.post("/activate")'):
        assert forbidden_route not in router


def test_paper_domains_do_not_route_into_live_execution():
    for relative in ('paper_execution', 'paper_runtime'):
        text = _text_tree(APP / relative)
        assert 'app.live_execution' not in text


def test_runtime_separates_readiness_from_execution_and_keeps_real_capital_disabled():
    main = (APP / 'main.py').read_text(encoding='utf-8')
    assert 'LIVE_READINESS_MODE = "readiness_phase_10"' in main
    assert 'LIVE_ADAPTER_MODE = "disabled_adapter"' in main
    assert 'LIVE_EXECUTION_MODE = "disabled"' in main
    assert 'REAL_CAPITAL_EXECUTION_MODE = "disabled"' in main
    assert 'prefix="/api/live"' in main


def test_s1_s4_remain_single_active_strategy_service():
    services = sorted(path.name for path in (APP / 'services').glob('*.py') if path.name != '__init__.py')
    assert services == ['strategies.py']


def test_no_live_secret_fields_are_persisted():
    models = (APP / 'models' / 'live_execution.py').read_text(encoding='utf-8').lower()
    for forbidden in ('api_key:', 'api_secret:', 'secret_key:', 'private_key:', 'exchange_secret:'):
        assert forbidden not in models
