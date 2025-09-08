# antispam.py (updated with language support)
import time
from collections import defaultdict
from typing import Dict, List
from .api_client import FFCapchaAPI

class AntiSpam:
    def __init__(self, api_token: str, max_repeats=3, cooldown=10, 
                 ban_time=300, max_simultaneous=5, language: str = "en",
                 custom_messages: Dict[str, str] = None):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token")
        
        self.max_repeats = max_repeats
        self.cooldown = cooldown
        self.ban_time = ban_time
        self.max_simultaneous = max_simultaneous
        self.language = language
        self.custom_messages = custom_messages or {}
        
        self.user_requests: Dict[int, List[float]] = defaultdict(list)
        self.user_bans: Dict[int, float] = {}
        self.command_counts: Dict[str, int] = defaultdict(int)
        self.last_reset = time.time()
        
        # Load messages
        self.messages = self._load_messages()
        if self.custom_messages:
            self._apply_custom_messages()
    
    def _load_messages(self) -> Dict[str, str]:
        """Load messages for current language"""
        base_messages = {
            "en": {
                "too_many_requests": "Too many requests. Please wait.",
                "request_too_fast": "Request too fast. Please slow down.",
                "user_banned": "User {user_id} banned for {ban_time} seconds: {reason}",
                "banned_message": "You are temporarily banned due to suspicious activity."
            },
            "ru": {
                "too_many_requests": "Слишком много запросов. Пожалуйста, подождите.",
                "request_too_fast": "Слишком быстрые запросы. Пожалуйста, замедлитесь.",
                "user_banned": "Пользователь {user_id} забанен на {ban_time} секунд: {reason}",
                "banned_message": "Вы временно заблокированы за подозрительную активность."
            },
            "es": {
                "too_many_requests": "Demasiadas solicitudes. Por favor espere.",
                "request_too_fast": "Solicitud demasiado rápida. Por favor reduzca la velocidad.",
                "user_banned": "Usuario {user_id} prohibido durante {ban_time} segundos: {reason}",
                "banned_message": "Está temporalmente prohibido por actividad sospechosa."
            },
            "de": {
                "too_many_requests": "Zu viele Anfragen. Bitte warten Sie.",
                "request_too_fast": "Anfrage zu schnell. Bitte verlangsamen Sie.",
                "user_banned": "Benutzer {user_id} für {ban_time} Sekunden gesperrt: {reason}",
                "banned_message": "Sie sind vorübergehend wegen verdächtiger Aktivitäten gesperrt."
            },
            "fr": {
                "too_many_requests": "Trop de demandes. Veuillez patienter.",
                "request_too_fast": "Demande trop rapide. Veuillez ralentir.",
                "user_banned": "Utilisateur {user_id} banni pendant {ban_time} secondes: {reason}",
                "banned_message": "Vous êtes temporairement banni pour activité suspecte."
            },
            "uk": {
                "too_many_requests": "Забагато запитів. Будь ласка, зачекайте.",
                "request_too_fast": "Запит занадто швидкий. Будь ласка, уповільніть.",
                "user_banned": "Користувач {user_id} заблокований на {ban_time} секунд: {reason}",
                "banned_message": "Ви тимчасово заблоковані за підозрілу активність."
            }
        }
        
        return base_messages.get(self.language, base_messages["en"])
    
    def _apply_custom_messages(self):
        """Apply custom messages"""
        for key, value in self.custom_messages.items():
            if key in self.messages:
                self.messages[key] = value
    
    def get_message(self, key: str, **kwargs) -> str:
        """Get message with formatting"""
        message = self.messages.get(key, "")
        if message and kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
        return message
    
    def set_language(self, language: str):
        """Change language dynamically"""
        self.language = language
        self.messages = self._load_messages()
        if self.custom_messages:
            self._apply_custom_messages()
    
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
            self._ban_user(user_id, current_time, self.get_message("too_many_requests"))
            return False
        
        # Check user request pattern
        user_requests = self.user_requests[user_id]
        user_requests.append(current_time)
        user_requests = [t for t in user_requests if current_time - t < 60]
        self.user_requests[user_id] = user_requests
        
        if len(user_requests) > self.max_repeats:
            self._ban_user(user_id, current_time, self.get_message("too_many_requests"))
            return False
        
        if len(user_requests) > 1 and (current_time - user_requests[-2]) < self.cooldown:
            self._ban_user(user_id, current_time, self.get_message("request_too_fast"))
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
        print(self.get_message("user_banned", user_id=user_id, ban_time=self.ban_time, reason=reason))
    
    def check_ban(self, user_id: int) -> bool:
        """Check if user is banned"""
        return self._is_banned(user_id, time.time())
    
    def get_ban_message(self) -> str:
        """Get ban message for users"""
        return self.get_message("banned_message")
    
    def unban_user(self, user_id: int):
        """Remove user ban"""
        if user_id in self.user_bans:
            del self.user_bans[user_id]