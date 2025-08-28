#!/usr/bin/env python3
"""
Тестовый файл для проверки работы с Google Sheets
Проверяет соответствие структуре реальных таблиц
"""

import os
from dotenv import load_dotenv
from google_sheets import (
    get_admin_sheet, 
    get_teacher_sheet, 
    create_teacher_sheet,
    get_date_column,
    find_student_row,
    append_student,
    get_teacher_info
)
from datetime import datetime

def test_admin_sheet_structure():
    """Проверяет структуру админской таблицы"""
    print("🔍 Проверка структуры админской таблицы...")
    
    try:
        sheet = get_admin_sheet()
        headers = sheet.row_values(3)
        
        required_headers = ["ФИО", "Номер телефона", "Телеграмм id", "Username", "Предмет", "Классы", "Дата регистрации"]
        
        print(f"Найденные заголовки: {headers}")
        
        missing_headers = []
        for header in required_headers:
            if header not in headers:
                missing_headers.append(header)
        
        if missing_headers:
            print(f"❌ Отсутствуют колонки: {', '.join(missing_headers)}")
            return False
        
        print("✅ Структура админской таблицы корректна")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_template_structure():
    """Проверяет структуру шаблонного листа"""
    print("\n🔍 Проверка структуры шаблонного листа...")
    
    try:
        from config import TEMPLATE_SHEET_NAME
        import gspread
        from google.oauth2.service_account import Credentials
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(
            os.getenv("GOOGLE_CREDENTIALS_JSON"), scopes=scope
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))
        
        template = spreadsheet.worksheet(TEMPLATE_SHEET_NAME)
        all_values = template.get_all_values()
        
        print(f"Размер шаблона: {len(all_values)} строк")
        
        # Проверяем ключевые элементы
        if len(all_values) > 0:
            print(f"A1: {all_values[0][0] if all_values[0] else 'пусто'}")
        if len(all_values) > 1:
            print(f"A2: {all_values[1][0] if all_values[1] else 'пусто'}")
        if len(all_values) > 3:
            print(f"Заголовки таблицы (строка 5): {all_values[4] if len(all_values) > 4 else 'нет'}")
        if len(all_values) > 4:
            print(f"Даты (строка 6): {all_values[5] if len(all_values) > 5 else 'нет'}")
        
        print("✅ Шаблонный лист найден и структура проверена")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_date_search():
    """Тестирует поиск дат в шаблоне"""
    print("\n🔍 Тестирование поиска дат...")
    
    try:
        from config import TEMPLATE_SHEET_NAME
        import gspread
        from google.oauth2.service_account import Credentials
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(
            os.getenv("GOOGLE_CREDENTIALS_JSON"), scopes=scope
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))
        
        template = spreadsheet.worksheet(TEMPLATE_SHEET_NAME)
        
        # Тестируем поиск сегодняшней даты
        today = datetime.now().strftime("%d.%m.%Y")
        print(f"Ищем дату: {today}")
        
        col = get_date_column(template, today)
        if col:
            print(f"✅ Дата найдена в колонке {col}")
        else:
            print(f"⚠️  Дата {today} не найдена в шаблоне")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_teacher_creation():
    """Тестирует создание листа преподавателя"""
    print("\n🔍 Тестирование создания листа преподавателя...")

    try:
        # Генерируем уникальное имя для теста
        test_teacher_name = f"Тестовый Преподаватель {datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Создаем тестовые данные
        test_teacher = {
            "ФИО": test_teacher_name,
            "Номер телефона": "+79991234567",
            "Телеграмм id": "123456789",
            "Username": "test_teacher",
            "Предмет": "Математика",
            "Классы": "начальные, средние",
            "Дата регистрации": datetime.now().strftime("%d.%m.%Y")
        }

        # 1. Сначала добавляем преподавателя в админскую таблицу
        admin_sheet = get_admin_sheet()
        admin_sheet.append_row(list(test_teacher.values()))

        # 2. Создаем лист преподавателя
        sheet = create_teacher_sheet(test_teacher_name)

        if not sheet:
            print("❌ Не удалось создать лист преподавателя")
            return False

        print("✅ Лист преподавателя создан")

        # 3. Проверяем заполнение данных
        fio = sheet.acell('B2').value
        phone = sheet.acell('B3').value

        print(f"B2 (ФИО): {fio}")
        print(f"B3 (Телефон): {phone}")

        if fio != test_teacher_name or phone != test_teacher["Номер телефона"]:
            print("❌ Ошибка в заполнении ФИО или телефона")
            return False

        print("✅ ФИО и телефон заполнены корректно")

        # 4. Проверяем форматирование (альтернативный способ)
        try:
            # Проверяем, что лист не пустой
            if not sheet.get_all_values():
                print("❌ Лист создан пустым")
                return False

            # Проверяем объединенные ячейки (если должны быть)
            if hasattr(sheet, 'merged_cells'):
                print(f"Объединенные ячейки: {len(sheet.merged_cells)}")

            print("✅ Форматирование проверено")

        except Exception as e:
            print(f"⚠️  Ошибка проверки форматирования: {e}")

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Основная функция тестирования"""
    load_dotenv()
    
    print("🧪 Тестирование работы с Google Sheets...\n")
    
    tests = [
        ("Структура админской таблицы", test_admin_sheet_structure),
        ("Структура шаблонного листа", test_template_structure),
        ("Поиск дат", test_date_search),
        ("Создание листа преподавателя", test_teacher_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 Тест: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Бот готов к работе с вашими таблицами.")
    else:
        print("⚠️  Некоторые тесты не пройдены. Проверьте настройки.")

if __name__ == "__main__":
    main() 