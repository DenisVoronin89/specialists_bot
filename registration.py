from google_sheets import get_admin_sheet, create_teacher_sheet
from datetime import datetime

def is_registered(telegram_id):
    """Проверяет, зарегистрирован ли преподаватель"""
    sheet = get_admin_sheet()
    all_values = sheet.get_all_values()
    
    # Начинаем чтение данных с 4-й строки (индекс 3)
    for i in range(3, len(all_values)):
        row = all_values[i]
        if len(row) > 2 and str(row[2]).strip() == str(telegram_id).strip():
            return True
    return False

def get_teacher_name_by_id(telegram_id):
    """Получает ФИО преподавателя по Telegram ID"""
    sheet = get_admin_sheet()
    all_values = sheet.get_all_values()
    
    # Начинаем чтение данных с 4-й строки (индекс 3)
    for i in range(3, len(all_values)):
        row = all_values[i]
        if len(row) > 2 and str(row[2]).strip() == str(telegram_id).strip():
            return row[0].strip() if len(row) > 0 else None
    return None
 
def register_teacher(data: dict):
    """
    Регистрирует нового преподавателя
    
    data = {
        "ФИО": "Иванов Иван Иванович",
        "Телефон": "+79991234567",
        "Telegram ID": 12345678,
        "Username": "ivanov",
        "Предмет": "Математика",
        "Классы": "начальные, средние",
    }
    """
    sheet = get_admin_sheet()
    data["Дата регистрации"] = datetime.now().strftime("%d.%m.%Y")
    
    # Добавляем запись в таблицу преподавателей. Данные начинаются с 4-й строки.
    values = [data.get("ФИО", ""), data.get("Номер телефона", ""), data.get("Телеграмм id", ""), data.get("Username", ""), data.get("Предмет", ""), data.get("Классы", ""), data.get("Дата регистрации", "")]
    existing = sheet.get_all_values()
    
    # Находим первую пустую строку начиная с 4-й
    insert_row_index = 4
    for i in range(3, len(existing)):  # Начинаем с индекса 3 (4-я строка)
        if len(existing[i]) == 0 or not existing[i][0].strip():  # Если строка пустая
            insert_row_index = i + 1  # gspread использует 1-based индексы
            break
    else:
        # Если все строки заполнены, добавляем в конец
        insert_row_index = len(existing) + 1
    
    # Используем insert_row только если нужно вставить в середину, иначе append_row
    if insert_row_index <= len(existing):
        sheet.insert_row(values, index=insert_row_index)
    else:
        sheet.append_row(values)
    
    # Создаем персональную вкладку преподавателя
    create_teacher_sheet(data["ФИО"])
    
    return True
