# captcha.py (enhanced text complexity)
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import os

class BaseCaptcha:
    def __init__(self, complexity: int = 3, text_scatter: bool = True, 
                 noise_level: int = None, blur_effect: bool = True,
                 distortion_level: int = None):
        self.complexity = max(1, min(complexity, 10))
        self.text_scatter = text_scatter
        self.noise_level = noise_level if noise_level is not None else self.complexity * 25
        self.blur_effect = blur_effect and self.complexity > 3
        self.distortion_level = distortion_level if distortion_level is not None else self.complexity
    
    def generate_text(self, length: int = None) -> str:
        """Generate random text for captcha with complexity"""
        if length is None:
            base_length = 5 + (self.complexity // 2)
            actual_length = min(max(base_length, 5), 12)
        else:
            actual_length = max(5, min(length, 12))
        
        # Use similar-looking characters to make it harder
        similar_chars = {
            'o': '0',
            'l': '1',
            'i': '1',
            's': '5',
            'b': '8',
            'g': '9'
        }
        
        chars = string.ascii_letters + string.digits
        if self.complexity > 4:
            chars += "!@#$%^&*"
        if self.complexity > 6:
            chars += "₴₵€£¥₳₲₪₮"
        
        text = ''.join(random.choice(chars) for _ in range(actual_length))
        
        # Replace some characters with similar ones for extra difficulty
        if self.complexity > 5:
            text_list = list(text)
            for i in range(len(text_list)):
                if text_list[i].lower() in similar_chars and random.random() > 0.7:
                    text_list[i] = similar_chars[text_list[i].lower()]
            text = ''.join(text_list)
        
        return text
    
    def create_image(self, text: str, width: int = 250, height: int = 100) -> Image.Image:
        """Create captcha image with enhanced complexity"""
        # Create image with gradient background
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Add gradient background
        for y in range(height):
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            draw.line([(0, y), (width, y)], fill=color)
        
        # Font size based on complexity
        font_size = 35 + (self.complexity * 3)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Draw text with enhanced distortion
        char_width = width // (len(text) + 2)
        for i, char in enumerate(text):
            # More extreme scattering for higher complexity
            x_offset = random.randint(-10, 10) * (self.complexity // 2)
            y_offset = random.randint(-15, 15) * (self.complexity // 3)
            
            x = char_width + i * char_width + x_offset
            y = (height - font_size) // 2 + y_offset
            
            # Random rotation
            rotation = random.randint(-self.complexity*5, self.complexity*5)
            
            # Create individual character image
            char_img = Image.new('RGBA', (font_size + 10, font_size + 10), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)
            
            # Draw character with random color and effects
            char_color = (
                random.randint(0, 100) if self.complexity > 3 else 0,
                random.randint(0, 100) if self.complexity > 3 else 0,
                random.randint(0, 100) if self.complexity > 3 else 0
            )
            
            char_draw.text((5, 5), char, font=font, fill=char_color)
            
            # Apply rotation
            if rotation:
                char_img = char_img.rotate(rotation, expand=1, fillcolor=(0, 0, 0, 0))
            
            # Paste character onto main image
            image.paste(char_img, (x, y), char_img)
        
        # Add enhanced noise
        for _ in range(self.noise_level):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, min(4, self.complexity//2 + 2))
            draw.ellipse([x, y, x+size, y+size], fill=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ))
        
        # Add lines and curves for higher complexity
        if self.complexity > 3:
            for _ in range(self.complexity * 2):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)
                draw.line([x1, y1, x2, y2], fill=(
                    random.randint(0, 200),
                    random.randint(0, 200),
                    random.randint(0, 200)
                ), width=random.randint(1, 2))
        
        # Add wave distortion for very high complexity
        if self.complexity > 7:
            image = self._apply_wave_distortion(image)
        
        # Apply blur for higher complexity
        if self.blur_effect:
            image = image.filter(ImageFilter.GaussianBlur(radius=min(1.5, self.complexity/8)))
        
        # Add border
        image = ImageOps.expand(image, border=2, fill=(0, 0, 0))
        
        return image
    
    def _apply_wave_distortion(self, image: Image.Image) -> Image.Image:
        """Apply wave distortion to image"""
        width, height = image.size
        distorted = Image.new('RGB', (width, height))
        
        for y in range(height):
            for x in range(width):
                # Sine wave distortion
                offset_x = int(5 * self.complexity * math.sin(2 * 3.14 * y / 60))
                offset_y = int(3 * self.complexity * math.cos(2 * 3.14 * x / 45))
                
                src_x = max(0, min(x + offset_x, width - 1))
                src_y = max(0, min(y + offset_y, height - 1))
                
                distorted.putpixel((x, y), image.getpixel((src_x, src_y)))
        
        return distorted

class TextCaptcha(BaseCaptcha):
    def __init__(self, complexity: int = 3, text_scatter: bool = True, 
                 noise_level: int = None, blur_effect: bool = True,
                 distortion_level: int = None):
        super().__init__(complexity, text_scatter, noise_level, blur_effect, distortion_level)
    
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
            max_val = 15 + (self.complexity * 8)
            a = random.randint(1, max_val)
            b = random.randint(1, max_val)
            answer = a + b
        elif op == '-':
            max_val = 20 + (self.complexity * 8)
            a = random.randint(max_val//2, max_val)
            b = random.randint(1, a-1)
            answer = a - b
        elif op == '*':
            max_val = 8 + self.complexity
            a = random.randint(1, max_val)
            b = random.randint(1, max_val)
            answer = a * b
        else:  # /
            b = random.randint(1, 6 + self.complexity//2)
            answer = random.randint(1, 12 + self.complexity)
            a = answer * b
        
        question = f"{a} {op} {b}"
        return answer, question