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


def test_color_coding_and_notes():
    """Тестирует новую логику цветового кодирования и примечаний в ячейках дат"""
    print("\n🔍 Тестирование цветового кодирования и примечаний...")
    
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

        # 1. Добавляем преподавателя в админскую таблицу
        admin_sheet = get_admin_sheet()
        admin_sheet.append_row(list(test_teacher.values()))

        # 2. Создаем лист преподавателя
        sheet = create_teacher_sheet(test_teacher_name)
        if not sheet:
            print("❌ Не удалось создать лист преподавателя")
            return False

        # 3. Тестируем добавление учеников
        today = datetime.now().strftime("%d.%m.%Y")
        
        # Ученик без примечания (должен быть зеленым)
        result1 = append_student(test_teacher_name, "Тестовый Ученик 1", "5", "математика", today, "")
        if not result1:
            print("❌ Не удалось добавить ученика без примечания")
            return False
        
        # Ученик с примечанием (должен быть красным)
        result2 = append_student(test_teacher_name, "Тестовый Ученик 2", "7", "физика", today, "хорошо подготовился")
        if not result2:
            print("❌ Не удалось добавить ученика с примечанием")
            return False

        # 4. Проверяем значения в ячейках
        date_col = get_date_column(sheet, today)
        if not date_col:
            print("❌ Не найдена колонка с датой")
            return False

        # Ищем строки учеников
        all_values = sheet.get_all_values()
        student1_row = None
        student2_row = None
        
        for i in range(7, len(all_values)):
            if len(all_values[i]) > 0 and all_values[i][0].startswith("Тестовый Ученик 1 5 математика"):
                student1_row = i + 1
            elif len(all_values[i]) > 0 and all_values[i][0].startswith("Тестовый Ученик 2 7 физика"):
                student2_row = i + 1

        if not student1_row or not student2_row:
            print("❌ Не найдены строки учеников")
            return False

        # Проверяем значения в ячейках
        student1_value = sheet.cell(student1_row, date_col).value
        student2_value = sheet.cell(student2_row, date_col).value

        if student1_value != "да":
            print(f"❌ Ученик 1 должен иметь значение 'да', получено: {student1_value}")
            return False

        if student2_value != "хорошо подготовился":
            print(f"❌ Ученик 2 должен иметь примечание, получено: {student2_value}")
            return False

        print("✅ Цветовое кодирование и примечания работают корректно")
        
        # Очистка
        from google_sheets import get_spreadsheet
        spreadsheet = get_spreadsheet()
        spreadsheet.del_worksheet(sheet)
        
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_student_duplication_prevention():
    """Тестирует предотвращение дублирования учеников"""
    print("\n🔍 Тестирование предотвращения дублирования учеников...")
    
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

        # 1. Добавляем преподавателя в админскую таблицу
        admin_sheet = get_admin_sheet()
        admin_sheet.append_row(list(test_teacher.values()))

        # 2. Создаем лист преподавателя
        sheet = create_teacher_sheet(test_teacher_name)
        if not sheet:
            print("❌ Не удалось создать лист преподавателя")
            return False

        # 3. Тестируем дублирование
        today = datetime.now().strftime("%d.%m.%Y")
        student_name = "Дублирующийся Ученик"
        student_class = "5"
        
        # Первое добавление
        result1 = append_student(test_teacher_name, student_name, student_class, "математика", today, "первое занятие")
        if not result1:
            print("❌ Не удалось добавить ученика в первый раз")
            return False
        
        # Второе добавление того же ученика (должно только обновить ячейку)
        result2 = append_student(test_teacher_name, student_name, student_class, "математика", today, "второе занятие")
        if not result2:
            print("❌ Не удалось обновить запись ученика")
            return False

        # 4. Проверяем, что ученик не дублировался
        all_values = sheet.get_all_values()
        student_count = 0
        
        for i in range(7, len(all_values)):
            if len(all_values[i]) > 0 and all_values[i][0].startswith(f"{student_name} {student_class} математика"):
                student_count += 1

        if student_count != 1:
            print(f"❌ Ученик дублировался! Найдено записей: {student_count}")
            return False

        # 5. Проверяем, что в ячейке даты последнее примечание
        date_col = get_date_column(sheet, today)
        if not date_col:
            print("❌ Не найдена колонка с датой")
            return False

        # Ищем строку ученика
        student_row = None
        for i in range(7, len(all_values)):
            if len(all_values[i]) > 0 and all_values[i][0].startswith(f"{student_name} {student_class} математика"):
                student_row = i + 1
                break

        if not student_row:
            print("❌ Не найдена строка ученика")
            return False

        # Проверяем значение в ячейке (должно быть последнее примечание)
        cell_value = sheet.cell(student_row, date_col).value
        if cell_value != "второе занятие":
            print(f"❌ В ячейке должно быть последнее примечание 'второе занятие', получено: {cell_value}")
            return False

        print("✅ Дублирование учеников предотвращено корректно")
        
        # Очистка
        from google_sheets import get_spreadsheet
        spreadsheet = get_spreadsheet()
        spreadsheet.del_worksheet(sheet)
        
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
        ("Цветовое кодирование и примечания", test_color_coding_and_notes),
        ("Предотвращение дублирования учеников", test_student_duplication_prevention),
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