from fastapi.testclient import TestClient

from app.main import app


def test_live_status_exposes_readiness_but_not_real_capital_execution():
    with TestClient(app) as client:
        response = client.get('/api/live/status')
        assert response.status_code == 200
        data = response.json()
        assert data['mode'] == 'readiness_phase_10'
        assert data['real_capital_execution'] == 'disabled'
        assert data['adapter'] == 'disabled_read_only'
        assert data['order_submission_available'] is False
        assert data['credential_write_available'] is False


def test_no_executable_live_order_route_exists():
    with TestClient(app) as client:
        response = client.post('/api/live/orders', json={'symbol': 'BTC/USDT', 'side': 'BUY'})
        assert response.status_code in {404, 405}


def test_health_separates_live_readiness_from_real_capital_activation():
    with TestClient(app) as client:
        data = client.get('/health').json()
        assert data['live_execution'] == 'readiness_phase_10'
        assert data['real_capital_execution'] == 'disabled'
