import requests
import sys
import json
from datetime import datetime

class AutomatonAPITester:
    def __init__(self, base_url="https://money-bot-5.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    self.results.append({
                        "test": name,
                        "status": "PASS",
                        "response_data": response_data
                    })
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error response: {error_data}")
                except:
                    print(f"Error response: {response.text}")
                self.results.append({
                    "test": name,
                    "status": "FAIL",
                    "expected": expected_status,
                    "actual": response.status_code,
                    "error": response.text
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.results.append({
                "test": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False, {}

    def test_health_endpoints(self):
        """Test basic health and root endpoints"""
        print("\n=== TESTING HEALTH ENDPOINTS ===")
        
        self.run_test("API Root", "GET", "", 200)
        self.run_test("Health Check", "GET", "health", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        print("\n=== TESTING DASHBOARD ===")
        
        success, data = self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)
        if success:
            required_keys = ["agents", "finances", "opportunities"]
            for key in required_keys:
                if key in data:
                    print(f"  ✅ {key} data present")
                else:
                    print(f"  ❌ Missing {key} data")

    def test_agents_api(self):
        """Test agents CRUD operations"""
        print("\n=== TESTING AGENTS API ===")
        
        # Get agents
        success, agents_data = self.run_test("Get Agents", "GET", "agents", 200)
        
        # Create agent
        agent_data = {
            "name": f"TestAgent_{datetime.now().strftime('%H%M%S')}",
            "type": "crypto_analyzer",
            "initial_balance": 100.0
        }
        
        success, created_agent = self.run_test(
            "Create Agent", 
            "POST", 
            "agents", 
            200, 
            data=agent_data
        )
        
        if success and 'id' in created_agent:
            agent_id = created_agent['id']
            print(f"  ✅ Agent created with ID: {agent_id}")
            
            # Get specific agent
            self.run_test(
                "Get Specific Agent", 
                "GET", 
                f"agents/{agent_id}", 
                200
            )
            
            # Simulate trade
            self.run_test(
                "Simulate Positive Trade", 
                "POST", 
                f"agents/{agent_id}/simulate-trade",
                200,
                params={"profit": 10}
            )
            
            # Try replication (needs sufficient balance)
            self.run_test(
                "Attempt Replication", 
                "POST", 
                f"agents/{agent_id}/replicate",
                200
            )
            
            # Destroy agent
            self.run_test(
                "Destroy Agent", 
                "DELETE", 
                f"agents/{agent_id}",
                200
            )

    def test_crypto_api(self):
        """Test cryptocurrency data endpoints"""
        print("\n=== TESTING CRYPTO API ===")
        
        # Get top coins
        success, coins_data = self.run_test(
            "Get Top Coins", 
            "GET", 
            "crypto/top-coins", 
            200,
            params={"limit": 5}
        )
        
        if success and 'coins' in coins_data and len(coins_data['coins']) > 0:
            coin_id = coins_data['coins'][0]['id']
            print(f"  ✅ Testing with coin: {coin_id}")
            
            # Get coin price
            self.run_test(
                "Get Coin Price", 
                "GET", 
                f"crypto/price/{coin_id}", 
                200
            )
            
            # Get coin history
            self.run_test(
                "Get Coin History", 
                "GET", 
                f"crypto/history/{coin_id}",
                200,
                params={"days": 7}
            )
        
        # Get trending
        self.run_test("Get Trending Coins", "GET", "crypto/trending", 200)

    def test_chat_api(self):
        """Test chat with orchestrator"""
        print("\n=== TESTING CHAT API ===")
        
        chat_data = {
            "message": "¿Cuál es el estado actual del sistema?",
            "session_id": None
        }
        
        success, response = self.run_test(
            "Chat with Orchestrator", 
            "POST", 
            "chat", 
            200, 
            data=chat_data
        )
        
        if success:
            if 'response' in response:
                print(f"  ✅ AI response received: {response['response'][:50]}...")
            if 'session_id' in response:
                print(f"  ✅ Session ID: {response['session_id']}")

    def test_payments_api(self):
        """Test payments endpoints"""
        print("\n=== TESTING PAYMENTS API ===")
        
        # Get transactions
        self.run_test("Get Transactions", "GET", "payments/transactions", 200)
        
        # Note: Not testing actual payment creation to avoid charges

    def test_opportunities_api(self):
        """Test opportunities endpoint"""
        print("\n=== TESTING OPPORTUNITIES API ===")
        
        self.run_test("Get Opportunities", "GET", "opportunities", 200)

    def test_llm_usage_api(self):
        """Test LLM usage tracking"""
        print("\n=== TESTING LLM USAGE API ===")
        
        self.run_test("Get LLM Usage", "GET", "llm/usage", 200)

def main():
    print("🤖 AUTOMATON ORCHESTRATOR API TESTING")
    print("=====================================")
    
    tester = AutomatonAPITester()
    
    # Run all tests
    try:
        tester.test_health_endpoints()
        tester.test_dashboard_stats()
        tester.test_crypto_api()
        tester.test_agents_api()
        tester.test_chat_api()
        tester.test_payments_api()
        tester.test_opportunities_api()
        tester.test_llm_usage_api()
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return 1

    # Print results
    print(f"\n📊 FINAL RESULTS")
    print(f"================")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Show failed tests
    failed_tests = [r for r in tester.results if r['status'] != 'PASS']
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"  - {test['test']}: {test.get('error', 'Status code mismatch')}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())