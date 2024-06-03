# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:56:18 2024

 Извлечение таблиц из заданных страниц 

@author: 1
"""
import os
import pandas
import tabula
import json
import re

# Путь до рабочей папки 
CWD = os.getcwd()
# Путь до папки с данными
DATA_PATH = os.path.join(CWD, 'data')

regions_file = "Regions.csv"
regions_path = os.path.join(DATA_PATH, regions_file)

regions_df = pandas.read_csv(regions_path, delimiter=';')

# Списки наименований регионов
regions_cn = regions_df['Region name (Ch)'].tolist()
regions_en = regions_df['Region name (En)'].tolist()


def get_tables_from_the_page(pdf_file_name, page_number):
    """

    Получить все таблицы c конкретной страницы 
    
    Parameters
    ----------
    pdf_file_name : TYPE
        DESCRIPTION.
    page_number : TYPE
        DESCRIPTION.

    Returns
    -------
    tables : TYPE
        DESCRIPTION.

    """
    
    pdf_file_path = os.path.join(DATA_PATH, pdf_file_name)
    
    tables = tabula.read_pdf(pdf_file_path, pages=page_number, 
                             multiple_tables=True, encoding='utf-16')
    
    return tables


def get_tables_from_the_pages(pdf_file_name, page_numbers):
    
    all_table_rows = []
    all_tables = []
    
    for page_number in page_numbers:
        
        tables = get_tables_from_the_page(pdf_file_name, page_number)
        all_tables.append(tables)

        for table in tables:

            for _, row in table.iterrows():
                c0 = row[0]
                c1 = row[1]
                if c0 in regions_cn:
                    # конструируем массив ячеек в строке
                    # 1. пропускаем пустые ячейки
                    # если ячейка начинается с цифры и внутри есть пробел, то разбиваем ячейку
                    row_data = []
                    for c in row:
                        if pandas.isnull(c):
                            continue
                        if type(c) is str and c[0].isdigit() and c.find(' ') > 0:
                            c_arr = c.split(' ')
                            row_data += c_arr
                        else:
                            row_data.append(c)

                    all_table_rows.append(row_data)

    df = pandas.DataFrame(all_table_rows)

    return df


def get_data(pages_file_name):

    pages_file_path = os.path.join(DATA_PATH, pages_file_name)
    if not os.path.isfile(pages_file_path):
        print(f"Не найден файл {pages_file_path}")
        return None

    with open(pages_file_path, encoding='utf-8') as fp:
        pages_data = json.load(fp)

    df = pandas.DataFrame()

    for pdf_file_name, pages in pages_data.items():
        if pages is None:
            # Если в файле таблица не найдена, то файл не обрабатываем
            continue
        print(f"******** Получение данных таблицы из файла {pdf_file_name}")
        df1 = get_tables_from_the_pages(pdf_file_name, pages)
        nn1 = df1.shape[0]
        print(f"Получено строк: {nn1}")
        if nn1 == 0:
            continue

        # определяем год по имени файла
        numbers = re.findall(r'\d+', pdf_file_name)
        year = None if len(numbers) == 0 else numbers[0]
        # добавим столбец, в котором указан год
        df1['year'] = year

        df = pandas.concat([df, df1])

    return df


# Имя фала, в котором перечислены имена pdf фалов и номеров страниц с таблицей
PAGES_FILE_NAME = '3-5.json'
# Имя файла результата
RESULT_FILE_NAME = '3-5.xlsx'
df_all = get_data(PAGES_FILE_NAME)
result_file_path = os.path.join(DATA_PATH, RESULT_FILE_NAME)
df_all.to_excel(result_file_path)
print(f"Данные сохранили в файл {result_file_path}")
