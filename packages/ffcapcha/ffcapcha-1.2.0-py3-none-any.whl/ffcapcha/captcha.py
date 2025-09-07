import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import os

class BaseCaptcha:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty
    
    def generate_text(self, length=6):
        """Generate random text for captcha"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_image(self, text, width=200, height=80):
        """Create captcha image with text"""
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Draw text with some noise
        for i, char in enumerate(text):
            x = 20 + i * 30 + random.randint(-5, 5)
            y = 20 + random.randint(-10, 10)
            draw.text((x, y), char, font=font, fill=(0, 0, 0))
        
        # Add noise
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        return image

class TextCaptcha(BaseCaptcha):
    def __init__(self, difficulty=1):
        super().__init__(difficulty)
    
    def generate(self, length=6):
        """Generate text captcha"""
        text = self.generate_text(length)
        image = self.create_image(text)
        return text, image

class MathCaptcha(BaseCaptcha):
    def __init__(self, difficulty=1):
        super().__init__(difficulty)
    
    def generate(self):
        """Generate math captcha"""
        operations = ['+', '-', '*']
        op = random.choice(operations)
        
        if op == '+':
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            answer = a + b
        elif op == '-':
            a = random.randint(10, 30)
            b = random.randint(1, a)
            answer = a - b
        else:  # *
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            answer = a * b
        
        question = f"{a} {op} {b}"
        return answer, question