# api_client.py (new file for API integration)
import requests
import json
from typing import Dict, Any

class FFCapchaAPI:
    def __init__(self, api_token: str, base_url: str = "https://ffcapcha.pythonanywhere.com"):
        self.api_token = api_token
        self.base_url = base_url
    
    def validate_token(self) -> bool:
        """Validate API token"""
        try:
            response = requests.get(
                f"{self.base_url}/api/validate",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=10
            )
            return response.status_code == 200 and response.json().get('valid', False)
        except:
            return False
    
    def log_captcha_attempt(self, user_id: int, success: bool, captcha_type: str) -> bool:
        """Log captcha attempt"""
        try:
            response = requests.post(
                f"{self.base_url}/api/log/captcha",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "user_id": user_id,
                    "success": success,
                    "captcha_type": captcha_type
                },
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def log_ban(self, user_id: int, reason: str) -> bool:
        """Log user ban"""
        try:
            response = requests.post(
                f"{self.base_url}/api/log/ban",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "user_id": user_id,
                    "reason": reason
                },
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for this API token"""
        try:
            response = requests.get(
                f"{self.base_url}/api/stats",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}