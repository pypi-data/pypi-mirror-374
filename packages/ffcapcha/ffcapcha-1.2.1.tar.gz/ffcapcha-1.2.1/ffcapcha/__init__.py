from .captcha import TextCaptcha, MathCaptcha
from .antispam import AntiSpam
from .telegram_integration import TelegramCaptcha, TelegramAntiSpam

__version__ = "1.2.1"
__author__ = "VndFF"
__all__ = [
    'TextCaptcha',
    'MathCaptcha', 
    'AntiSpam',
    'TelegramCaptcha',
    'TelegramAntiSpam'
]