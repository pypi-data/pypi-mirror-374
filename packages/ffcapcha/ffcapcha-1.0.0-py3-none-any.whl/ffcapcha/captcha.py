import random
from PIL import Image, ImageDraw, ImageFont

class TextCaptcha:
    def __init__(self, width=200, height=80):
        self.width = width
        self.height = height
    
    def generate(self):
        text = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((20, 25), text, font=font, fill='black')
        return text, image

class MathCaptcha:
    def generate(self):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(['+', '-', '*'])
        
        question = f"{a} {op} {b}"
        answer = str(eval(question))
        
        return answer, question