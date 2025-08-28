#!/usr/bin/env python3
"""
Скрипт для проверки корректности .env файла
"""

import os
import re
from dotenv import load_dotenv

def check_bot_token(token):
    """Проверяет формат Bot Token"""
    if not token:
        return False, "Токен отсутствует"
    
    # Формат: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    if not re.match(pattern, token):
        return False, "Неверный формат токена"
    
    return True, "✅ Корректный Bot Token"

def check_chat_id(chat_id_str):
    """Проверяет Chat ID"""
    if not chat_id_str:
        return False, "Chat ID отсутствует"
    
    try:
        chat_id = int(chat_id_str)
        if chat_id == 0:
            return False, "Chat ID не может быть нулем"
        return True, f"✅ Корректный Chat ID: {chat_id}"
    except ValueError:
        return False, "Chat ID должен быть числом"

def check_credentials_path(path):
    """Проверяет путь к файлу сервис-аккаунта"""
    if not path:
        return False, "Путь к файлу сервис-аккаунта отсутствует"
    
    if not os.path.exists(path):
        return False, f"Файл не найден: {path}"
    
    if not path.endswith('.json'):
        return False, "Файл должен иметь расширение .json"
    
    return True, f"✅ Файл сервис-аккаунта найден: {path}"

def check_spreadsheet_id(spreadsheet_id):
    """Проверяет ID таблицы"""
    if not spreadsheet_id:
        return False, "ID таблицы отсутствует"
    
    # ID таблицы обычно длинная строка букв и цифр
    if len(spreadsheet_id) < 20:
        return False, "ID таблицы слишком короткий"
    
    return True, f"✅ ID таблицы: {spreadsheet_id}"

def main():
    """Основная функция проверки"""
    print("🔍 Проверка .env файла...\n")
    
    # Загружаем .env
    load_dotenv()
    
    # Список проверок
    checks = [
        ("BOT_TOKEN", check_bot_token),
        ("AUTHORIZED_CHAT_ID", check_chat_id),
        ("GOOGLE_CREDENTIALS_JSON", check_credentials_path),
        ("SPREADSHEET_ID", check_spreadsheet_id),
    ]
    
    all_passed = True
    
    for var_name, check_func in checks:
        print(f"📋 Проверка {var_name}:")
        value = os.getenv(var_name)
        
        if value is None:
            print(f"❌ Переменная {var_name} не найдена в .env файле")
            all_passed = False
        else:
            is_valid, message = check_func(value)
            print(f"   {message}")
            if not is_valid:
                all_passed = False
        
        print()
    
    # Итоговый результат
    if all_passed:
        print("🎉 Все переменные окружения корректны!")
        print("✅ Бот готов к запуску")
    else:
        print("❌ Обнаружены ошибки в .env файле")
        print("📝 Исправьте ошибки и запустите проверку снова")
    
    return all_passed

if __name__ == "__main__":
    main() 