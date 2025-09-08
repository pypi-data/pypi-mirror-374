# telegram_integration.py (updated with language customization)
import random
import io
import asyncio
from typing import Dict, Optional, Callable, Any
from .captcha import TextCaptcha, MathCaptcha
from .api_client import FFCapchaAPI

class TelegramIntegration:
    def __init__(self, api_token: str, framework: str = "pytelegrambotapi", 
                 complexity: int = 3, language: str = "en", custom_messages: Dict[str, str] = None):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token. Please get a valid token from FFcapcha dashboard.")
        
        self.framework = framework.lower()
        self.complexity = max(1, min(complexity, 10))
        self.language = language
        self.custom_messages = custom_messages or {}
        self.user_states: Dict[int, dict] = {}
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
        
        # Framework validation
        if self.framework not in ["aiogram", "pytelegrambotapi", "python-telegram-bot"]:
            raise ValueError("Framework must be 'aiogram', 'pytelegrambotapi', or 'python-telegram-bot'")
    
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
                "text_captcha_caption": "Введите текст с изображения:",
                "math_captcha_caption": "Решите: {question} = ?",
                "captcha_passed": "✅ Капча пройдена! Добро пожаловать!",
                "captcha_failed": "❌ Неверная капча. Попробуйте снова.",
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
        message = lang_messages.get(key, "")
        if message and kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
        return message
    
    def set_language(self, language: str):
        """Change language dynamically"""
        if language in self.supported_languages:
            self.language = language
    
    def update_custom_messages(self, custom_messages: Dict[str, str]):
        """Update custom messages dynamically"""
        self.custom_messages = custom_messages
        self._apply_custom_messages()
    
    def init_bot(self, bot: Any):
        """Initialize bot framework"""
        self.bot = bot
        
        if self.framework == "aiogram":
            self.setup_aiogram_handlers()
        elif self.framework == "python-telegram-bot":
            self.setup_python_telegram_bot_handlers()
        else:
            self.setup_pytelegrambotapi_handlers()
    
    def setup_aiogram_handlers(self):
        """Setup aiogram handlers"""
        try:
            from aiogram import Dispatcher, types
            from aiogram.dispatcher import filters
            
            dp = Dispatcher.get_current()
            
            @dp.message_handler(filters.CommandStart())
            async def start_handler(message: types.Message):
                await self.send_captcha(message)
            
            @dp.message_handler()
            async def message_handler(message: types.Message):
                await self.process_message(message)
                
        except ImportError:
            raise ImportError("Aiogram is not installed. Please install it with 'pip install aiogram'")
    
    def setup_python_telegram_bot_handlers(self):
        """Setup python-telegram-bot handlers"""
        try:
            from telegram.ext import CommandHandler, MessageHandler, Filters
            
            self.bot.dispatcher.add_handler(CommandHandler("start", self.start_handler_ptb))
            self.bot.dispatcher.add_handler(MessageHandler(Filters.text, self.message_handler_ptb))
        except ImportError:
            raise ImportError("Python-telegram-bot is not installed. Please install it with 'pip install python-telegram-bot'")
    
    def setup_pytelegrambotapi_handlers(self):
        """Setup pytelegrambotapi handlers"""
        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            asyncio.run(self.send_captcha(message))
        
        @self.bot.message_handler(func=lambda m: True)
        def message_handler(message):
            asyncio.run(self.process_message(message))
    
    async def start_handler_ptb(self, update, context):
        """Start handler for python-telegram-bot"""
        await self.send_captcha(update.message)
    
    async def message_handler_ptb(self, update, context):
        """Message handler for python-telegram-bot"""
        await self.process_message(update.message)
    
    async def send_captcha(self, message) -> bool:
        """Send captcha to user"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Choose captcha type randomly
        captcha_type = "text" if random.random() > 0.5 else "math"
        
        if captcha_type == "text":
            captcha = TextCaptcha(complexity=self.complexity)
            answer, image = captcha.generate()
            
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            caption = self.get_message("text_captcha_caption")
            
            if self.framework == "aiogram":
                from aiogram import types
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=types.InputFile(img_byte_arr, filename='captcha.png'),
                    caption=caption
                )
            elif self.framework == "python-telegram-bot":
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=img_byte_arr,
                    caption=caption
                )
            else:
                self.bot.send_photo(
                    chat_id=chat_id,
                    photo=img_byte_arr,
                    caption=caption
                )
            
            self.user_states[user_id] = {
                'awaiting_captcha': True,
                'answer': answer,
                'type': 'text'
            }
        else:
            captcha = MathCaptcha(complexity=self.complexity)
            answer, question = captcha.generate()
            
            caption = self.get_message("math_captcha_caption", question=question)
            
            if self.framework == "aiogram":
                await self.bot.send_message(chat_id=chat_id, text=caption)
            elif self.framework == "python-telegram-bot":
                await self.bot.send_message(chat_id=chat_id, text=caption)
            else:
                self.bot.send_message(chat_id=chat_id, text=caption)
            
            self.user_states[user_id] = {
                'awaiting_captcha': True,
                'answer': str(answer),
                'type': 'math'
            }
        
        return True
    
    async def process_message(self, message):
        """Process incoming messages"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if user_id in self.user_states and self.user_states[user_id].get('awaiting_captcha'):
            if self.verify_captcha(user_id, message.text):
                # Captcha passed
                success_msg = self.get_message("captcha_passed")
                self.user_states[user_id]['awaiting_captcha'] = False
                
                # Log success
                self.api.log_captcha_attempt(user_id, True, self.user_states[user_id]['type'])
            else:
                # Captcha failed
                success_msg = self.get_message("captcha_failed")
                self.api.log_captcha_attempt(user_id, False, self.user_states[user_id]['type'])
                await self.send_captcha(message)
            
            # Send response
            if self.framework == "aiogram":
                await self.bot.send_message(chat_id=chat_id, text=success_msg)
            elif self.framework == "python-telegram-bot":
                await self.bot.send_message(chat_id=chat_id, text=success_msg)
            else:
                self.bot.send_message(chat_id=chat_id, text=success_msg)
        else:
            # User hasn't started or completed captcha
            start_msg = self.get_message("start_captcha")
            
            if self.framework == "aiogram":
                await self.bot.send_message(chat_id=chat_id, text=start_msg)
            elif self.framework == "python-telegram-bot":
                await self.bot.send_message(chat_id=chat_id, text=start_msg)
            else:
                self.bot.send_message(chat_id=chat_id, text=start_msg)
    
    def verify_captcha(self, user_id: int, user_input: str) -> bool:
        """Verify captcha answer"""
        if user_id not in self.user_states:
            return False
        
        captcha_data = self.user_states[user_id]
        success = user_input.strip() == str(captcha_data['answer'])
        return success

# Backward compatibility
TelegramCaptcha = TelegramIntegration