# captcha.py (updated with more customization)
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import os

class BaseCaptcha:
    def __init__(self, complexity: int = 3, text_scatter: bool = True, noise_level: int = None, blur_effect: bool = True):
        self.complexity = max(1, min(complexity, 10))
        self.text_scatter = text_scatter
        self.noise_level = noise_level if noise_level is not None else self.complexity * 15
        self.blur_effect = blur_effect and self.complexity > 5
    
    def generate_text(self, length: int = None) -> str:
        """Generate random text for captcha with complexity"""
        if length is None:
            base_length = 4 + (self.complexity // 2)
            actual_length = min(max(base_length, 4), 10)
        else:
            actual_length = max(4, min(length, 12))
        
        chars = string.ascii_letters + string.digits
        if self.complexity > 5:
            chars += "!@#$%^&*"
        if self.complexity > 7:
            chars += "₴₵€£¥₳₲₪₮"
        
        return ''.join(random.choice(chars) for _ in range(actual_length))
    
    def create_image(self, text: str, width: int = 200, height: int = 80) -> Image.Image:
        """Create captcha image with complexity settings"""
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Font size based on complexity
        font_size = 30 + (self.complexity * 2)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Draw text with complexity-based distortion
        for i, char in enumerate(text):
            if self.text_scatter:
                x = 10 + i * ((width - 20) // len(text)) + random.randint(-5, 5)
                y = random.randint(10, height - 40)
            else:
                x = 20 + i * (width // (len(text) + 1))
                y = (height - font_size) // 2
            
            # More distortion for higher complexity
            rotation = random.randint(-self.complexity*3, self.complexity*3) if self.text_scatter else 0
            
            draw.text((x, y), char, font=font, fill=(
                random.randint(0, 100) if self.complexity > 3 else 0,
                random.randint(0, 100) if self.complexity > 3 else 0,
                random.randint(0, 100) if self.complexity > 3 else 0
            ))
        
        # Add noise based on complexity
        for _ in range(self.noise_level):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, min(3, self.complexity//2 + 1))
            draw.ellipse([x, y, x+size, y+size], fill=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ))
        
        # Add lines for higher complexity
        if self.complexity > 4:
            for _ in range(self.complexity - 3):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)
                draw.line([x1, y1, x2, y2], fill=(
                    random.randint(0, 200),
                    random.randint(0, 200),
                    random.randint(0, 200)
                ), width=1)
        
        # Apply blur for higher complexity
        if self.blur_effect:
            image = image.filter(ImageFilter.GaussianBlur(radius=min(1, self.complexity/10)))
        
        return image

class TextCaptcha(BaseCaptcha):
    def __init__(self, complexity: int = 3, text_scatter: bool = True, noise_level: int = None, blur_effect: bool = True):
        super().__init__(complexity, text_scatter, noise_level, blur_effect)
    
    def generate(self, length: int = None) -> tuple:
        """Generate text captcha"""
        text = self.generate_text(length)
        image = self.create_image(text)
        return text, image

class MathCaptcha(BaseCaptcha):
    def __init__(self, complexity: int = 3):
        super().__init__(complexity, text_scatter=False, noise_level=0, blur_effect=False)
    
    def generate(self) -> tuple:
        """Generate math captcha with complexity"""
        operations = ['+', '-', '*']
        
        if self.complexity > 5:
            operations.append('/')
        
        op = random.choice(operations)
        
        if op == '+':
            max_val = 10 + (self.complexity * 5)
            a = random.randint(1, max_val)
            b = random.randint(1, max_val)
            answer = a + b
        elif op == '-':
            max_val = 15 + (self.complexity * 5)
            a = random.randint(max_val//2, max_val)
            b = random.randint(1, a-1)
            answer = a - b
        elif op == '*':
            max_val = 5 + self.complexity
            a = random.randint(1, max_val)
            b = random.randint(1, max_val)
            answer = a * b
        else:  # /
            b = random.randint(1, 5 + self.complexity//2)
            answer = random.randint(1, 10 + self.complexity)
            a = answer * b
        
        question = f"{a} {op} {b}"
        return answer, question