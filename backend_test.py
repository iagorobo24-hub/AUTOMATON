#!/usr/bin/env python3
"""
Backend API Testing for Automaton Orchestrator
Tests all endpoints including new dashboard stats with llm field
"""
import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class AutomatonAPITester:
    def __init__(self, base_url="https://money-bot-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int = 200, 
                 data: Dict = None, headers: Dict = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {"raw_response": response.text}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:500]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": str(e)
            })
            return False, {}

    def test_health_endpoints(self):
        """Test basic health and root endpoints"""
        print("\n" + "="*50)
        print("TESTING HEALTH & ROOT ENDPOINTS")
        print("="*50)
        
        self.run_test("API Root", "GET", "/")
        self.run_test("Health Check", "GET", "/health")

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint with llm field"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD STATS (with LLM field)")
        print("="*50)
        
        success, data = self.run_test("Dashboard Stats", "GET", "/dashboard/stats")
        if success and data:
            print("📊 Dashboard Stats Structure:")
            
            # Check required fields
            required_fields = ['agents', 'finances', 'trading', 'lineage']
            for field in required_fields:
                if field in data:
                    print(f"   ✅ {field}: {data[field]}")
                else:
                    print(f"   ❌ Missing field: {field}")
            
            # Check for LLM field specifically
            if 'llm' in data:
                print(f"   ✅ llm field present: {data['llm']}")
                llm_data = data['llm']
                if 'total_tokens' in llm_data:
                    print(f"      - Total tokens: {llm_data['total_tokens']}")
                if 'cost_estimate' in llm_data:
                    print(f"      - Cost estimate: ${llm_data['cost_estimate']:.4f}")
            else:
                print("   ❌ Missing LLM field in dashboard stats")
            
            # Check new metrics
            if 'trading' in data:
                trading = data['trading']
                new_metrics = ['win_rate', 'total_trades', 'pnl_24h', 'pnl_7d']
                for metric in new_metrics:
                    if metric in trading:
                        print(f"   ✅ {metric}: {trading[metric]}")
                    else:
                        print(f"   ❌ Missing metric: {metric}")

    def test_notifications_api(self):
        """Test notifications endpoints"""
        print("\n" + "="*50)
        print("TESTING NOTIFICATIONS API")
        print("="*50)
        
        # Get notifications
        success, data = self.run_test("Get Notifications", "GET", "/notifications")
        if success:
            print(f"   📬 Found {len(data.get('notifications', []))} notifications")
            print(f"   📬 Unread count: {data.get('unread_count', 0)}")
        
        # Get notification count
        self.run_test("Get Notification Count", "GET", "/notifications/count")
        
        # Test read all (should work even if no notifications)
        self.run_test("Mark All Read", "POST", "/notifications/read-all")

    def test_activity_api(self):
        """Test activity feed endpoints"""
        print("\n" + "="*50)
        print("TESTING ACTIVITY FEED API")
        print("="*50)
        
        # Get activity feed
        success, data = self.run_test("Get Activity Feed", "GET", "/activity")
        if success:
            events = data.get('events', [])
            print(f"   📋 Found {len(events)} activity events")
            
            # Check event structure
            if events:
                event = events[0]
                required_fields = ['id', 'type', 'title', 'description', 'created_at']
                for field in required_fields:
                    if field in event:
                        print(f"   ✅ Event has {field}")
                    else:
                        print(f"   ❌ Event missing {field}")
        
        # Test with filters
        self.run_test("Activity - Agent Filter", "GET", "/activity?type_filter=agent")
        self.run_test("Activity - Trade Filter", "GET", "/activity?type_filter=trade")

    def test_agents_api(self):
        """Test agents endpoints"""
        print("\n" + "="*50)
        print("TESTING AGENTS API")
        print("="*50)
        
        # Get all agents
        success, data = self.run_test("Get All Agents", "GET", "/agents")
        if success:
            agents = data.get('agents', [])
            print(f"   🤖 Found {len(agents)} agents")
            
            # Check agent structure
            if agents:
                agent = agents[0]
                required_fields = ['id', 'name', 'status', 'finances', 'performance']
                for field in required_fields:
                    if field in agent:
                        print(f"   ✅ Agent has {field}")
                    else:
                        print(f"   ❌ Agent missing {field}")

    def test_crypto_api(self):
        """Test crypto market endpoints"""
        print("\n" + "="*50)
        print("TESTING CRYPTO API")
        print("="*50)
        
        # Get top coins
        success, data = self.run_test("Get Top Coins", "GET", "/crypto/top-coins?limit=5")
        if success:
            coins = data.get('coins', [])
            print(f"   💰 Found {len(coins)} coins")
            
            if coins:
                coin = coins[0]
                required_fields = ['id', 'symbol', 'name', 'current_price', 'price_change_24h']
                for field in required_fields:
                    if field in coin:
                        print(f"   ✅ Coin has {field}")
                    else:
                        print(f"   ❌ Coin missing {field}")
        
        # Get trending
        self.run_test("Get Trending Coins", "GET", "/crypto/trending")

    def test_llm_usage_api(self):
        """Test LLM usage tracking"""
        print("\n" + "="*50)
        print("TESTING LLM USAGE API")
        print("="*50)
        
        success, data = self.run_test("Get LLM Usage", "GET", "/llm/usage")
        if success:
            print(f"   🧠 Total tokens: {data.get('total_tokens', 0)}")
            print(f"   💰 Total cost: ${data.get('total_cost', 0):.4f}")
            print(f"   📊 Providers: {list(data.get('by_provider', {}).keys())}")

    def test_orchestrator_endpoints(self):
        """Test orchestrator specific endpoints"""
        print("\n" + "="*50)
        print("TESTING ORCHESTRATOR ENDPOINTS")
        print("="*50)
        
        self.run_test("Get Orchestrator State", "GET", "/orchestrator/state")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Automaton Orchestrator API Tests")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🔗 API URL: {self.api_url}")
        
        # Run test suites
        self.test_health_endpoints()
        self.test_dashboard_stats()
        self.test_notifications_api()
        self.test_activity_api()
        self.test_agents_api()
        self.test_crypto_api()
        self.test_llm_usage_api()
        self.test_orchestrator_endpoints()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Tests failed: {len(self.failed_tests)}")
        
        if self.failed_tests:
            print("\n🚨 FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['test']} - {test['endpoint']}")
                if 'error' in test:
                    print(f"   Error: {test['error']}")
                else:
                    print(f"   Expected: {test['expected']}, Got: {test['actual']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AutomatonAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())