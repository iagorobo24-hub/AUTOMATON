from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
APP = BACKEND / 'app'
REPO = BACKEND.parent


def _text_tree(root: Path, suffixes={'.py'}):
    return '\n'.join(path.read_text(encoding='utf-8') for path in root.rglob('*') if path.is_file() and path.suffix in suffixes)


def test_live_phase10_has_no_real_order_transport_or_secret_storage_surface():
    live = _text_tree(APP / 'live_execution')
    lowered = live.lower()
    for forbidden in ('def create_order(', 'def place_order(', 'def submit_order(', 'api_secret', 'secret_key=', 'private_key='):
        assert forbidden not in lowered
    router = (APP / 'live_execution' / 'router.py').read_text(encoding='utf-8').lower()
    assert '@router.post("/orders")' not in router
    assert 'credential' not in router or 'credential_write_available' in router


def test_paper_domains_do_not_route_into_live_execution():
    for relative in ('paper_execution', 'paper_runtime'):
        text = _text_tree(APP / relative)
        assert 'app.live_execution' not in text


def test_runtime_keeps_real_capital_disabled():
    main = (APP / 'main.py').read_text(encoding='utf-8')
    assert 'LIVE_EXECUTION_MODE = "readiness_phase_10"' in main
    assert 'REAL_CAPITAL_EXECUTION_MODE = "disabled"' in main
    assert 'prefix="/api/live"' in main


def test_s1_s4_remain_single_active_strategy_service():
    services = sorted(path.name for path in (APP / 'services').glob('*.py') if path.name != '__init__.py')
    assert services == ['strategies.py']
