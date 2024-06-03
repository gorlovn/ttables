# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 09:21:28 2024

Извлечь текст одной страницs и сохранить в файл 

@author: 1
"""
import os
import pdfplumber
import re

# Путь до рабочей папки 
CWD = os.getcwd()
# Путь до папки с данными
DATA_PATH = os.path.join(CWD, 'data')

FILE_NAME = "新疆统计年鉴2008（O）.pdf"

PAGE_NUMBER = 111

file_path = os.path.join(DATA_PATH, FILE_NAME)

with pdfplumber.open(file_path) as pdf:
    
    page = pdf.pages[PAGE_NUMBER]
    text = page.extract_text()
    

TEXT_PATH = os.path.join(CWD, 'text')
if not os.path.isdir(TEXT_PATH):
    os.makedirs(TEXT_PATH)
    

# Определим год
numbers = re.findall(r'\d+', FILE_NAME)
year = numbers[0]

# Имя файла содер;ит год и номер страницы 
text_file_name = f"{year}_p{PAGE_NUMBER}.txt"
text_file_path = os.path.join(TEXT_PATH, text_file_name)

with open(text_file_path, "wb") as fp:
    fp.write(text.encode("utf8"))
    
print(f"Записали файл {text_file_path}")
