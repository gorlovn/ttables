# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 10:22:26 2024

Ищем таблицы по двум частям в наименовании

@author: 1
"""
import os
import glob
from pathlib import Path
import pandas
import pdfplumber
from tqdm import tqdm
import json

# Путь до рабочей папки 
CWD = os.getcwd()
# Путь до папки с данными
DATA_PATH = os.path.join(CWD, 'data')

# Продолжение таблицы 
TABLE_CONTINUED = "续表"

# Минимальный номер страницы (исключим оглавление)
PAGE_NUMBER_MIN = 30


def find_pages(pdf_paths, t_number, t_names):
    """
    Найти все страницы с таблицей 

    Parameters
    ----------
    pdf_paths : [] str
        список путей с pdf файлами.
    t_number: str
        номер таблицы (глава)
    t_names : []str
        части наименования таблицы

    Returns
    -------
    p_in_files : dict
        страницы c найденной таблицей 
        по файлам.

    """
    
    p_in_files = {}
    
    for pdf_path in pdf_paths:
        pdf_name = Path(pdf_path).name
        print(f"Файл: {pdf_name}")
        
        # найденные страницы в текущем файле 
        pages = [] 

        table_found = False  # найдена или нет таблица 
        with pdfplumber.open(pdf_path) as pdf:
            for p_number in tqdm(range(PAGE_NUMBER_MIN, len(pdf.pages))):
                page = pdf.pages[p_number]
                text = page.extract_text()
                if t_number in text and all(t_name in text for t_name in t_names):
                    table_found = True
                
                if table_found:
                    page_number = p_number + 1
                    if len(pages) == 0:
                        # найдена первая страница таблицы
                        pages.append(page_number)
                    elif t_number in text and TABLE_CONTINUED in text:
                            pages.append(page_number)
                    else:
                        # таблица закончилась
                        break
        
        if table_found:
            print(f"Найдены страницы: {pages}")
            p_in_files[pdf_name] = pages
        else:
            print("Таблица не найдена")
            p_in_files[pdf_name] = None
    
    return p_in_files


def main(t_names_file):

    t_names_path = os.path.join(DATA_PATH, t_names_file)
    t_names_df = pandas.read_csv(t_names_path, delimiter=';')

    pdf_files_path = os.path.join(DATA_PATH, '*.pdf')
    pdf_files = glob.glob(pdf_files_path)

    for _, df_row in t_names_df.iterrows():
    
        table_number = df_row['Chapter']
        t_name1 = df_row['Table name, part 1']
        t_name2 = df_row['Table name, part 2']
        table_names = [t_name1, t_name2]
    
        print(f"******** Поиск таблицы {table_number} в pdf файлах")
        print(f"Части наименования таблицы: {table_names} ")

        pages_in_files = find_pages(pdf_files, table_number, table_names)
    
        pages_file_name = f"{table_number}.json"
        pages_file_path = os.path.join(DATA_PATH, pages_file_name)
    
        with open(pages_file_path, 'w', encoding='utf-8') as fp:
            json.dump(pages_in_files, fp, ensure_ascii=False, indent=4)

        print(f"Записали файл {pages_file_path}")


if __name__ == "__main__":

    main('table_names.csv')
