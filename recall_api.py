"""
Recall Network API Client
"""
import requests
import json
import time
from typing import Dict, List, Optional, Any
from config import Config

class RecallAPI:
    def __init__(self):
        self.api_key = Config.get_api_key()
        self.base_url = Config.get_base_url()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Recall API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=self.headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.ok:
                return response.json()
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return {"error": response.text, "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return {"error": str(e)}
    
    def execute_trade(self, from_token: str, to_token: str, amount: str, reason: str = "") -> Dict:
        """Execute a trade"""
        endpoint = "/api/trade"
        data = {
            "fromToken": from_token,
            "toToken": to_token,
            "amount": amount,
            "reason": reason
        }
        return self._make_request("POST", endpoint, data)
    
    def get_portfolio(self) -> Dict:
        """Get current portfolio information - using balances endpoint"""
        try:
            endpoint = "/api/agent/balances"
            result = self._make_request("GET", endpoint)
            
            # If API fails, return error
            if 'error' in result:
                return result
            
            # Transform API response to our expected format
            if 'success' in result and result['success']:
                balances = result.get('balances', [])
                total_value = sum(balance.get('amount', 0) for balance in balances)
                available_balance = next((b['amount'] for b in balances if b.get('symbol') == 'USDC'), 0)
                
                return {
                    'total_value': total_value,
                    'available_balance': available_balance,
                    'positions': balances,
                    'current_prices': {}
                }
            else:
                return {'error': 'API response format error'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_competition_leaderboard(self, competition_id: Optional[str] = None) -> Dict:
        """Get competition leaderboard"""
        endpoint = "/api/competition/leaderboard"
        if competition_id:
            endpoint += f"?competition_id={competition_id}"
        return self._make_request("GET", endpoint)
    
    def get_price_data(self, token_address: str) -> Dict:
        """Get current price data for a token"""
        endpoint = f"/api/price?token={token_address}"
        return self._make_request("GET", endpoint)
    
    def get_agent_info(self) -> Dict:
        """Get agent information"""
        endpoint = "/api/agent/profile"
        return self._make_request("GET", endpoint)
    
    def get_trade_history(self) -> Dict:
        """Get agent trade history"""
        endpoint = "/api/agent/trades"
        return self._make_request("GET", endpoint)
    
    def health_check(self) -> Dict:
        """Check API health"""
        endpoint = "/api/health"
        return self._make_request("GET", endpoint)
    
    def get_competitions(self) -> Dict:
        """Get available competitions"""
        endpoint = "/api/competitions"
        return self._make_request("GET", endpoint)
