import time
from typing import Dict, Optional
from .captcha import TextCaptcha, MathCaptcha
from .antispam import AntiSpam

class TelegramCaptcha:
    def __init__(self, bot, captcha_timeout=180*60, captcha_type="text"):
        self.bot = bot
        self.captcha_timeout = captcha_timeout
        self.captcha_type = captcha_type
        self.user_last_captcha: Dict[int, float] = {}
        self.user_captcha_data: Dict[int, dict] = {}
    
    def should_show_captcha(self, user_id: int) -> bool:
        """Проверяет, нужно ли показывать капчу"""
        current_time = time.time()
        last_time = self.user_last_captcha.get(user_id, 0)
        
        if current_time - last_time > self.captcha_timeout:
            self.user_last_captcha[user_id] = current_time
            return True
        return False
    
    def send_text_captcha(self, chat_id: int):
        """Отправляет текстовую капчу"""
        captcha = TextCaptcha()
        answer, image = captcha.generate()
        
        # Сохраняем изображение в bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Отправляем изображение
        self.bot.send_photo(chat_id, img_byte_arr, 
                           caption="Please enter the text from the image:")
        
        self.user_captcha_data[chat_id] = {
            'answer': answer,
            'type': 'text',
            'time': time.time()
        }
    
    def send_math_captcha(self, chat_id: int):
        """Отправляет математическую капчу"""
        captcha = MathCaptcha()
        answer, question = captcha.generate()
        
        self.bot.send_message(chat_id, 
                            f"Solve the math problem: {question}")
        
        self.user_captcha_data[chat_id] = {
            'answer': answer,
            'type': 'math',
            'time': time.time()
        }
    
    def verify(self, chat_id: int, user_input: str) -> bool:
        """Проверяет ответ капчи"""
        if chat_id not in self.user_captcha_data:
            return False
        
        captcha_data = self.user_captcha_data[chat_id]
        
        # Проверяем таймаут капчи (5 минут)
        if time.time() - captcha_data['time'] > 300:
            del self.user_captcha_data[chat_id]
            return False
        
        # Проверяем ответ
        if user_input.strip() == captcha_data['answer']:
            del self.user_captcha_data[chat_id]
            return True
        
        return False

class TelegramAntiSpam(AntiSpam):
    def __init__(self, max_repeats=3, cooldown=10, ban_time=300, group_threshold=5):
        super().__init__(max_repeats, cooldown, ban_time, group_threshold)
    
    def check_message(self, update) -> bool:
        """Проверяет сообщение на спам"""
        user_id = update.message.from_user.id
        command = update.message.text
        
        if self.check_ban(user_id):
            update.message.reply_text("You are temporarily banned. Please try again later.")
            return False
        
        if not self.add_request(user_id, command):
            update.message.reply_text("Too many requests. Please wait.")
            return False
        
        return True