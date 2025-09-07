from .captcha import TextCaptcha, MathCaptcha
from .antispam import AntiSpam
from .telecapcha import TelegramCaptcha, TelegramAntiSpam

__version__ = "1.3.3"
__author__ = "VndFF"
__all__ = [
    'TextCaptcha',
    'MathCaptcha', 
    'AntiSpam',
    'TelegramCaptcha',
    'TelegramAntiSpam'
]