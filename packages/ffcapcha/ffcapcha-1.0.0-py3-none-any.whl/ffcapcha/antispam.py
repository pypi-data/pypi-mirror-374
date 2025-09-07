import time
from collections import defaultdict
from .database import block_db

class AntiSpam:
    def __init__(self, max_repeats=3, cooldown=10, ban_time=300):
        self.max_repeats = max_repeats
        self.cooldown = cooldown
        self.ban_time = ban_time
        self.user_requests = defaultdict(list)
    
    def add_request(self, user_id, command):
        current_time = time.time()
        
        # Проверка блокировки
        if block_db.is_blocked(user_id):
            return False
        
        # Очистка старых запросов
        self.user_requests[user_id] = [
            t for t in self.user_requests[user_id] 
            if current_time - t < self.cooldown
        ]
        
        # Добавление нового запроса
        self.user_requests[user_id].append(current_time)
        
        # Проверка на спам
        if len(self.user_requests[user_id]) >= self.max_repeats:
            block_db.add_block(user_id, "spam", self.ban_time)
            print(f"User {user_id} blocked for spam")
            return False
        
        return True