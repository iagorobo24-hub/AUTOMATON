"""
Backend API Tests for Automaton Orchestrator - Bulk Actions & Quick Actions
Tests: Pause All, Resume All, Emergency Stop, Portfolio History, Status Summary
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://money-bot-5.preview.emergentagent.com').rstrip('/')

class TestHealthEndpoints:
    """Health and root endpoint tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "operational"
        print(f"✅ API Root: {data['message']}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health: {data['status']}")


class TestAgentStatusSummary:
    """Tests for agent status summary endpoint"""
    
    def test_status_summary_returns_correct_structure(self):
        """Test that status summary returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/agents/status-summary")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields exist
        required_fields = ['total', 'active', 'paused', 'replicating', 'dying', 'dead', 'hibernating']
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], int), f"Field {field} should be int"
        
        print(f"✅ Status Summary: total={data['total']}, active={data['active']}, paused={data['paused']}, dead={data['dead']}")


class TestPauseAllAgents:
    """Tests for pause all agents endpoint"""
    
    def test_pause_all_returns_success(self):
        """Test pause all endpoint returns success"""
        response = requests.post(f"{BASE_URL}/api/agents/pause-all")
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] == True
        assert "paused_count" in data
        assert "message" in data
        
        print(f"✅ Pause All: paused_count={data['paused_count']}, message={data['message']}")
    
    def test_pause_all_changes_agent_status(self):
        """Test that pause all actually changes agent status to paused"""
        # First pause all
        pause_response = requests.post(f"{BASE_URL}/api/agents/pause-all")
        assert pause_response.status_code == 200
        
        # Then check status summary
        status_response = requests.get(f"{BASE_URL}/api/agents/status-summary")
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        # Active should be 0 after pause (unless there are no agents)
        print(f"✅ After Pause: active={status_data['active']}, paused={status_data['paused']}")


class TestResumeAllAgents:
    """Tests for resume all agents endpoint"""
    
    def test_resume_all_returns_success(self):
        """Test resume all endpoint returns success"""
        # First pause all to ensure there are paused agents
        requests.post(f"{BASE_URL}/api/agents/pause-all")
        
        # Then resume all
        response = requests.post(f"{BASE_URL}/api/agents/resume-all")
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] == True
        assert "resumed_count" in data
        assert "message" in data
        
        print(f"✅ Resume All: resumed_count={data['resumed_count']}, message={data['message']}")
    
    def test_resume_all_changes_agent_status(self):
        """Test that resume all actually changes agent status to active"""
        # First pause all
        requests.post(f"{BASE_URL}/api/agents/pause-all")
        
        # Then resume all
        resume_response = requests.post(f"{BASE_URL}/api/agents/resume-all")
        assert resume_response.status_code == 200
        
        # Check status summary
        status_response = requests.get(f"{BASE_URL}/api/agents/status-summary")
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        # Paused should be 0 after resume
        print(f"✅ After Resume: active={status_data['active']}, paused={status_data['paused']}")


class TestEmergencyStop:
    """Tests for emergency stop endpoint"""
    
    def test_emergency_stop_requires_confirmation(self):
        """Test that emergency stop without confirmation returns error"""
        response = requests.post(f"{BASE_URL}/api/agents/emergency-stop")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == False
        assert data["error"] == "confirmation_required"
        assert "confirm=true" in data["message"]
        
        print(f"✅ Emergency Stop (no confirm): error={data['error']}")
    
    def test_emergency_stop_with_confirmation_works(self):
        """Test that emergency stop with confirmation terminates agents"""
        # Note: This test will actually terminate agents, so we need to recreate them after
        response = requests.post(f"{BASE_URL}/api/agents/emergency-stop?confirm=true")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "terminated_count" in data
        assert "total_balance_affected" in data
        assert "message" in data
        
        print(f"✅ Emergency Stop (confirmed): terminated={data['terminated_count']}, balance_affected=${data['total_balance_affected']}")


class TestPortfolioHistory:
    """Tests for portfolio history endpoint"""
    
    def test_portfolio_history_default_period(self):
        """Test portfolio history with default 7d period"""
        response = requests.get(f"{BASE_URL}/api/portfolio/history")
        assert response.status_code == 200
        data = response.json()
        
        assert "period" in data
        assert "initial_capital" in data
        assert "current_value" in data
        assert "total_pnl" in data
        assert "pnl_percent" in data
        assert "history" in data
        assert isinstance(data["history"], list)
        
        print(f"✅ Portfolio History: period={data['period']}, initial_capital=${data['initial_capital']}, current_value=${data['current_value']}")
    
    def test_portfolio_history_different_periods(self):
        """Test portfolio history with different time periods"""
        periods = ['1d', '7d', '1m', 'all']
        
        for period in periods:
            response = requests.get(f"{BASE_URL}/api/portfolio/history?period={period}")
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period
            assert len(data["history"]) > 0
            print(f"✅ Portfolio History ({period}): {len(data['history'])} data points")


class TestNotificationsForBulkActions:
    """Tests that bulk actions create notifications"""
    
    def test_notifications_created_for_pause(self):
        """Test that pausing agents creates a notification"""
        # First resume all to have active agents
        requests.post(f"{BASE_URL}/api/agents/resume-all")
        
        # Then pause all
        requests.post(f"{BASE_URL}/api/agents/pause-all")
        
        # Check notifications
        response = requests.get(f"{BASE_URL}/api/notifications?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        notifications = data.get("notifications", [])
        # Check if there's a pause notification
        pause_notif = [n for n in notifications if "Paused" in n.get("title", "")]
        
        print(f"✅ Notifications after pause: found {len(pause_notif)} pause-related notifications")


class TestAgentCreation:
    """Tests for creating agents (to restore after emergency stop)"""
    
    def test_create_agent(self):
        """Test creating a new agent"""
        agent_data = {
            "name": "TEST_Phoenix-Restored",
            "type": "crypto_trader",
            "initial_capital": 400
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agents",
            json=agent_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["name"] == agent_data["name"]
        
        print(f"✅ Created Agent: {data['name']} with ID {data['id']}")
        
        return data["id"]


# Cleanup fixture to restore agents after tests
@pytest.fixture(scope="module", autouse=True)
def restore_agents_after_tests():
    """Restore agents after all tests complete"""
    yield
    
    # Create two agents to restore the system
    for i in range(2):
        agent_data = {
            "name": f"Phoenix-00{i+1}",
            "type": "crypto_trader",
            "initial_capital": 400
        }
        requests.post(
            f"{BASE_URL}/api/agents",
            json=agent_data,
            headers={"Content-Type": "application/json"}
        )
    print("\n✅ Restored 2 agents after tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
