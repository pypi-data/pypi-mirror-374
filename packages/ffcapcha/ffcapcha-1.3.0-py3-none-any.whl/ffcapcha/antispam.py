import time
from collections import defaultdict
from typing import Dict, List
from .api_client import FFCapchaAPI

class AntiSpam:
    def __init__(self, api_token: str, max_repeats=3, cooldown=10, ban_time=300, max_simultaneous=5):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token")
        
        self.max_repeats = max_repeats
        self.cooldown = cooldown
        self.ban_time = ban_time
        self.max_simultaneous = max_simultaneous
        
        self.user_requests: Dict[int, List[float]] = defaultdict(list)
        self.user_bans: Dict[int, float] = {}
        self.command_counts: Dict[str, int] = defaultdict(int)
        self.last_reset = time.time()
    
    def add_request(self, user_id: int, command: str) -> bool:
        """Add user request and check if it's suspicious"""
        current_time = time.time()
        
        if self._is_banned(user_id, current_time):
            return False
        
        # Reset command counts every minute
        if current_time - self.last_reset > 60:
            self.command_counts.clear()
            self.last_reset = current_time
        
        # Count simultaneous commands
        self.command_counts[command] += 1
        if self.command_counts[command] > self.max_simultaneous:
            self._ban_user(user_id, current_time, "Too many simultaneous requests")
            return False
        
        # Check user request pattern
        user_requests = self.user_requests[user_id]
        user_requests.append(current_time)
        user_requests = [t for t in user_requests if current_time - t < 60]
        self.user_requests[user_id] = user_requests
        
        if len(user_requests) > self.max_repeats:
            self._ban_user(user_id, current_time, "Too many repeated requests")
            return False
        
        if len(user_requests) > 1 and (current_time - user_requests[-2]) < self.cooldown:
            self._ban_user(user_id, current_time, "Request too fast")
            return False
        
        return True
    
    def _is_banned(self, user_id: int, current_time: float) -> bool:
        """Check if user is currently banned"""
        if user_id in self.user_bans:
            if current_time - self.user_bans[user_id] < self.ban_time:
                return True
            else:
                del self.user_bans[user_id]
        return False
    
    def _ban_user(self, user_id: int, current_time: float, reason: str):
        """Ban user temporarily and log to API"""
        self.user_bans[user_id] = current_time
        self.api.log_ban(user_id, reason)
        print(f"🚨 User {user_id} banned for {self.ban_time} seconds: {reason}")
    
    def check_ban(self, user_id: int) -> bool:
        """Check if user is banned"""
        return self._is_banned(user_id, time.time())
    
    def unban_user(self, user_id: int):
        """Remove user ban"""
        if user_id in self.user_bans:
            del self.user_bans[user_id]