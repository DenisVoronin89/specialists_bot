#!/usr/bin/env python3
"""
Тестовый файл для проверки функциональности бота
Запускать только для отладки!
"""

import os
from dotenv import load_dotenv
from registration import is_registered, get_teacher_name_by_id
from google_sheets import get_admin_sheet, get_teacher_sheet, create_teacher_sheet

def test_config():
    """Проверяет загрузку конфигурации"""
    load_dotenv()
    
    required_vars = [
        'BOT_TOKEN',
        'AUTHORIZED_CHAT_ID', 
        'GOOGLE_CREDENTIALS_JSON',
        'SPREADSHEET_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return False
    
    print("✅ Конфигурация загружена успешно")
    return True

def test_google_sheets_connection():
    """Проверяет подключение к Google Sheets"""
    try:
        admin_sheet = get_admin_sheet()
        print("✅ Подключение к Google Sheets успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к Google Sheets: {e}")
        return False

def test_admin_sheet_structure():
    """Проверяет структуру админской таблицы"""
    try:
        sheet = get_admin_sheet()
        headers = sheet.row_values(3)
        required_headers = ["ФИО", "Номер телефона", "Телеграмм id", "Username", "Предмет", "Классы", "Дата регистрации"]
        
        missing_headers = []
        for header in required_headers:
            if header not in headers:
                missing_headers.append(header)
        
        if missing_headers:
            print(f"❌ В таблице 'Преподаватели' отсутствуют колонки: {', '.join(missing_headers)}")
            return False
        
        print("✅ Структура админской таблицы корректна")
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки структуры таблицы: {e}")
        return False

def test_template_sheet():
    """Проверяет наличие шаблонного листа"""
    try:
        from config import TEMPLATE_SHEET_NAME
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.getenv("GOOGLE_CREDENTIALS_JSON"), scope
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))
        
        try:
            template = spreadsheet.worksheet(TEMPLATE_SHEET_NAME)
            print("✅ Шаблонный лист найден")
            return True
        except gspread.exceptions.WorksheetNotFound:
            print(f"❌ Лист '{TEMPLATE_SHEET_NAME}' не найден в таблице")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки шаблонного листа: {e}")
        return False

def test_bot_logic():
    """Тестирует логику бота (без реального запуска)"""
    try:
        from bot import start_registration, get_fio, get_phone, get_subject, get_classes
        from lessons import process_lesson_message
        
        # Тестируем обработку сообщений о занятиях
        test_message = "Петров Петр 5 математика / хорошо подготовился"
        result = process_lesson_message("Тестовый Преподаватель", test_message)
        
        # Проверяем, что парсинг работает (даже если преподаватель не найден)
        if "❌ Неверный формат" not in result:
            print("✅ Логика обработки занятий работает корректно")
            return True
        else:
            print(f"❌ Ошибка в логике обработки занятий: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования логики бота: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Запуск тестов функциональности бота...\n")
    
    tests = [
        ("Конфигурация", test_config),
        ("Подключение к Google Sheets", test_google_sheets_connection),
        ("Структура админской таблицы", test_admin_sheet_structure),
        ("Шаблонный лист", test_template_sheet),
        ("Логика бота", test_bot_logic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔍 Тест: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Бот готов к работе.")
    else:
        print("⚠️  Некоторые тесты не пройдены. Проверьте настройки.")

if __name__ == "__main__":
    main() 