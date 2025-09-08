# telegram_integration.py (updated)
import random
import io
from typing import Dict, Optional, Callable, Any
from .captcha import TextCaptcha, MathCaptcha
from .api_client import FFCapchaAPI

class TelegramIntegration:
    def __init__(self, api_token: str, framework: str = "pytelegrambotapi", complexity: int = 3):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token. Please get a valid token from FFcapcha dashboard.")
        
        self.framework = framework.lower()
        self.complexity = max(1, min(complexity, 10))
        self.user_states: Dict[int, dict] = {}
        self.bot = None
        
        # Framework validation
        if self.framework not in ["aiogram", "pytelegrambotapi", "python-telegram-bot"]:
            raise ValueError("Framework must be 'aiogram', 'pytelegrambotapi', or 'python-telegram-bot'")
    
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
        from telegram.ext import CommandHandler, MessageHandler, Filters
        
        self.bot.dispatcher.add_handler(CommandHandler("start", self.start_handler))
        self.bot.dispatcher.add_handler(MessageHandler(Filters.text, self.message_handler))
    
    def setup_pytelegrambotapi_handlers(self):
        """Setup pytelegrambotapi handlers"""
        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            self.send_captcha(message)
        
        @self.bot.message_handler(func=lambda m: True)
        def message_handler(message):
            self.process_message(message)
    
    async def start_handler(self, update, context):
        """Start handler for python-telegram-bot"""
        await self.send_captcha(update.message)
    
    async def message_handler(self, update, context):
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
            
            if self.framework == "aiogram":
                from aiogram import types
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=types.InputFile(img_byte_arr, filename='captcha.png'),
                    caption="Enter text from image:"
                )
            elif self.framework == "python-telegram-bot":
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=img_byte_arr,
                    caption="Enter text from image:"
                )
            else:
                self.bot.send_photo(
                    chat_id=chat_id,
                    photo=img_byte_arr,
                    caption="Enter text from image:"
                )
            
            self.user_states[user_id] = {
                'awaiting_captcha': True,
                'answer': answer,
                'type': 'text'
            }
        else:
            captcha = MathCaptcha(complexity=self.complexity)
            answer, question = captcha.generate()
            
            caption = f"Solve: {question} = ?"
            
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
                success_msg = "✅ Captcha passed! Welcome!"
                self.user_states[user_id]['awaiting_captcha'] = False
                
                # Log success
                self.api.log_captcha_attempt(user_id, True, self.user_states[user_id]['type'])
            else:
                # Captcha failed
                success_msg = "❌ Wrong captcha. Try again."
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
            if self.framework == "aiogram":
                await self.bot.send_message(chat_id=chat_id, text="Please complete the captcha first with /start")
            elif self.framework == "python-telegram-bot":
                await self.bot.send_message(chat_id=chat_id, text="Please complete the captcha first with /start")
            else:
                self.bot.send_message(chat_id=chat_id, text="Please complete the captcha first with /start")
    
    def verify_captcha(self, user_id: int, user_input: str) -> bool:
        """Verify captcha answer"""
        if user_id not in self.user_states:
            return False
        
        captcha_data = self.user_states[user_id]
        success = user_input.strip() == str(captcha_data['answer'])
        return success

# Backward compatibility
TelegramCaptcha = TelegramIntegration