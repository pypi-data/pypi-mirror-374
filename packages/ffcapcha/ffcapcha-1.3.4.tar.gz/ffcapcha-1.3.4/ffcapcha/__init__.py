from .captcha import TextCaptcha, MathCaptcha
from .antispam import AntiSpam
from .telegram_integration import TelegramCapcha

__version__ = "1.3.4"
__author__ = "VndFF"
__all__ = [
    'TextCaptcha',
    'MathCaptcha', 
    'AntiSpam',
    'TelegramCapcha'
]