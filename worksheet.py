import os
import requests
import pinyin as py
from pinyin.cedict import translate_word
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def get_chinese_word_png(chinese_word):
    unicode_hex = chinese_word.encode('unicode-escape').decode()[2:]
    image_path = f"assets/strokes/sequence/{unicode_hex}.png"

    if os.path.exists(image_path):
        image = Image.open(image_path)
        width, height = image.size
        return image_path, width, height

    url = f"https://ckc.eduhk.hk/apps/strokes/sequence/200/{unicode_hex}.png"
    response = requests.get(url)

    if response.status_code == 200:
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(response.content)
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        return image_path, width, height
    
def add_rice_grid(c, height):
    for index in range(1, 10):
        c.drawImage('assets/image/ricegrid.png', 50 * index, height, width=50, height=50)
    

def add_vocabulary(c, vocabulary, pdf_height):
    w, h = A4
    max_dimension = 500
    translation = translate_word(vocabulary)
    
    for index, word in enumerate(vocabulary, start=1):

        # pinyin = py.get(word, format='diacritical')
        # c.setFillColorRGB(0, 0, 0)
        # c.setFont("Cousine", 20)
        # c.drawString(50 * index, h - pdf_height, pinyin)
        
        c.drawImage('assets/image/ricegrid.png', 50 * index, h - pdf_height - 45 - 10, width=50, height=50)
        add_rice_grid(c, 100)
        c.setFillColorRGB(0.7845, 0.7845, 0.7845)
        c.setFont("baseFont", 50)
        c.drawString(50 * index, h - pdf_height - 45, word)

        url, width, height = get_chinese_word_png(word)
        scaling_factor = min(max_dimension / width, max_dimension / height)

        c.drawImage(url, 50, h - pdf_height - 40 * index - 100, width=int(width * scaling_factor), height=int(height * scaling_factor))

    return pdf_height
    
def generate_worksheet_pdf():
    pdf_buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('baseFont', 'assets/font/DFPKaiShuW3-B5.ttf'))
    pdfmetrics.registerFont(TTFont('Cousine', 'assets/font/Cousine.ttf'))
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    pdf_height = 50 
    vocabulary = ['明聰', '聰明', '做']
    for word in vocabulary:
        add_vocabulary(c, word, pdf_height)
        pdf_height += 80 

    c.save()
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_data