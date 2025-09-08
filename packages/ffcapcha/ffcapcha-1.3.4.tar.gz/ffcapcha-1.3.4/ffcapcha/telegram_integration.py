
import random
import io
import asyncio
import time
import json
import os
from typing import Dict, Optional, Callable, Any
from .captcha import TextCaptcha, MathCaptcha
from .api_client import FFCapchaAPI

class TelegramCapcha:
    def __init__(self, api_token: str, API_type: str = "pytelegrambotapi", 
                 complexity: int = 3, language: str = "en", 
                 custom_messages: Dict[str, str] = None,
                 check_periodicity: int = 0):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token. Please get a valid token from FFcapcha dashboard.")
        
        self.API_type = API_type.lower()
        self.complexity = max(1, min(complexity, 10))
        self.language = language
        self.custom_messages = custom_messages or {}
        self.check_periodicity = check_periodicity  # 0 = always, -1 = once, >0 = minutes
        self.user_states: Dict[int, dict] = {}
        self.user_passed_times: Dict[int, float] = {}
        self.bot = None
        
        # Available languages
        self.supported_languages = ["en", "ru", "es", "de", "fr", "uk"]
        if self.language not in self.supported_languages:
            self.language = "en"
        
        # Default messages for all languages
        self.messages = self._load_default_messages()
        
        # Apply custom messages
        if self.custom_messages:
            self._apply_custom_messages()
        
        # API type validation
        if self.API_type not in ["aiogram", "pytelegrambotapi", "python-telegram-bot"]:
            raise ValueError("API_type must be 'aiogram', 'pytelegrambotapi', or 'python-telegram-bot'")
    
    def _load_default_messages(self) -> Dict[str, Dict[str, str]]:
        """Load default messages for all supported languages"""
        return {
            "en": {
                "text_captcha_caption": "Enter text from image:",
                "math_captcha_caption": "Solve: {question} = ?",
                "captcha_passed": "✅ Captcha passed! Welcome!",
                "captcha_failed": "❌ Wrong captcha. Try again.",
                "start_captcha": "Please complete the captcha first with /start",
                "too_many_requests": "Too many requests. Please wait.",
                "banned": "You are temporarily banned due to suspicious activity."
            },
            "ru": {
                "text_captcha_caption": "😁Пр, введи текст с картинки:",
                "math_captcha_caption": "😍Пр, реши пж: {question} = ?",
                "captcha_passed": "👌Все окей, проходи",
                "captcha_failed": "🤣Хахаха, неправильно, пробуй еще раз",
                "start_captcha": "Пожалуйста, сначала пройдите капчу с помощью /start",
                "too_many_requests": "Слишком много запросов. Пожалуйста, подождите.",
                "banned": "Вы временно заблокированы за подозрительную активность."
            },
            "es": {
                "text_captcha_caption": "Ingrese el texto de la imagen:",
                "math_captcha_caption": "Resuelva: {question} = ?",
                "captcha_passed": "✅ ¡Captcha pasado! ¡Bienvenido!",
                "captcha_failed": "❌ Captcha incorrecto. Intente de nuevo.",
                "start_captcha": "Por favor, complete el captcha primero con /start",
                "too_many_requests": "Demasiadas solicitudes. Por favor espere.",
                "banned": "Está temporalmente prohibido por actividad sospechosa."
            },
            "de": {
                "text_captcha_caption": "Geben Sie den Text aus dem Bild ein:",
                "math_captcha_caption": "Lösen Sie: {question} = ?",
                "captcha_passed": "✅ Captcha bestanden! Willkommen!",
                "captcha_failed": "❌ Falsches Captcha. Versuchen Sie es erneut.",
                "start_captcha": "Bitte vervollständigen Sie zuerst das Captcha mit /start",
                "too_many_requests": "Zu viele Anfragen. Bitte warten Sie.",
                "banned": "Sie sind vorübergehend wegen verdächtiger Aktivitäten gesperrt."
            },
            "fr": {
                "text_captcha_caption": "Entrez le texte de l'image:",
                "math_captcha_caption": "Résoudre: {question} = ?",
                "captcha_passed": "✅ Captcha réussi! Bienvenue!",
                "captcha_failed": "❌ Captcha incorrect. Réessayer.",
                "start_captcha": "Veuillez d'abord compléter le captcha avec /start",
                "too_many_requests": "Trop de demandes. Veuillez patienter.",
                "banned": "Vous êtes temporairement banni pour activité suspecte."
            },
            "uk": {
                "text_captcha_caption": "Введіть текст з зображення:",
                "math_captcha_caption": "Розв'яжіть: {question} = ?",
                "captcha_passed": "✅ Капчу пройдено! Ласкаво просимо!",
                "captcha_failed": "❌ Невірна капча. Спробуйте ще раз.",
                "start_captcha": "Будь ласка, спочатку пройдіть капчу за допомогою /start",
                "too_many_requests": "Забагато запитів. Будь ласка, зачекайте.",
                "banned": "Ви тимчасово заблоковані за підозрілу активність."
            }
        }
    
    def _apply_custom_messages(self):
        """Apply custom messages to the current language"""
        current_lang_messages = self.messages.get(self.language, self.messages["en"])
        for key, value in self.custom_messages.items():
            if key in current_lang_messages:
                current_lang_messages[key] = value
        self.messages[self.language] = current_lang_messages
    
    def get_message(self, key: str, **kwargs) -> str:
        """Get message in current language with optional formatting"""
        lang_messages = self.messages.get(self.language, self.messages["en"])
        message = lang_messages