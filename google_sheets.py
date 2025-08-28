import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from config import GOOGLE_CREDENTIALS_JSON, SPREADSHEET_ID, TEMPLATE_SHEET_NAME

def get_client():
    """Получает клиент для работы с Google Sheets"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_JSON, scopes=scope)
    return gspread.authorize(creds)

def get_spreadsheet():
    """Получает объект таблицы"""
    client = get_client()
    return client.open_by_key(SPREADSHEET_ID)


def get_admin_sheet():
    """Получает лист с данными преподавателей"""
    spreadsheet = get_spreadsheet()
    return spreadsheet.worksheet("Преподаватели")


def get_teacher_sheet(teacher_name):
    """Получает лист преподавателя по имени"""
    try:
        spreadsheet = get_spreadsheet()
        return spreadsheet.worksheet(teacher_name)
    except gspread.exceptions.WorksheetNotFound:
        return None


def create_teacher_sheet(teacher_name):
    """Создаёт новый лист преподавателя ТОЧНО как шаблон"""
    try:
        spreadsheet = get_spreadsheet()
        template = spreadsheet.worksheet(TEMPLATE_SHEET_NAME)

        # Получаем данные преподавателя
        teacher_info = get_teacher_info(teacher_name)
        if not teacher_info:
            print(f"Преподаватель {teacher_name} не найден в таблице")
            return None

        # Индекс для вставки в самый конец (справа)
        rightmost_index = len(spreadsheet.worksheets())

        # Создаём новый лист копированием шаблона — вставляем справа
        new_sheet = spreadsheet.duplicate_sheet(
            source_sheet_id=template.id,
            new_sheet_name=teacher_name,
            insert_sheet_index=rightmost_index
        )

        # Обновляем данные преподавателя (в шаблоне B2=ФИО, B3=Телефон)
        new_sheet.update('B2', [[teacher_info['ФИО']]])
        new_sheet.update('B3', [[teacher_info['Телефон']]])

        return new_sheet

    except Exception as e:
        print(f"Ошибка создания листа для {teacher_name}: {str(e)}")
        return None


def get_date_column(sheet, target_date):
    """Находит колонку для указанной даты. Даты находятся в 7-й строке (индекс 6)."""
    try:
        all_values = sheet.get_all_values()
        if len(all_values) < 7:
            print("Недостаточно строк для поиска дат (ожидается минимум 7)")
            return None
        date_row = all_values[6]  # 7-я строка
        for col_idx, cell_value in enumerate(date_row):
            if cell_value == target_date:
                return col_idx + 1
        # Доп. попытка распарсить даты формата DD.MM.YYYY
        try:
            target_dt = datetime.strptime(target_date, "%d.%m.%Y")
        except Exception:
            target_dt = None
        if target_dt:
            for col_idx, cell_value in enumerate(date_row):
                try:
                    if cell_value and "." in cell_value:
                        cell_dt = datetime.strptime(cell_value, "%d.%m.%Y")
                        if cell_dt == target_dt:
                            return col_idx + 1
                except Exception:
                    continue
        print(f"Дата {target_date} не найдена в строке дат")
        return None
    except Exception as e:
        print(f"Ошибка при поиске колонки даты: {e}")
        return None


def find_student_row(sheet, student_name):
    """Находит строку с учеником или возвращает None. Ученики начинаются с 8-й строки (индекс 7)."""
    try:
        all_values = sheet.get_all_values()
        for i, row in enumerate(all_values):
            if i < 7:  # до 8-й строки включительно
                continue
            if len(row) > 0 and row[0] == student_name:
                return i + 1
        return None
    except Exception as e:
        print(f"Ошибка при поиске ученика: {e}")
        return None


def append_student(teacher_name, student_name, student_class, date, note=""):
    """Добавляет или обновляет запись о занятии ученика"""
    try:
        sheet = get_teacher_sheet(teacher_name)
        if not sheet:
            sheet = create_teacher_sheet(teacher_name)
            if not sheet:
                return False
        
        # Находим колонку для даты
        date_col = get_date_column(sheet, date)
        if not date_col:
            return False
        
        # Ищем существующую запись ученика
        student_row = find_student_row(sheet, student_name)
        
        if student_row:
            # Обновляем существующую запись - ставим "да" в нужную колонку
            sheet.update_cell(student_row, date_col, "да")
            if note:
                # Обновляем примечания (колонка F)
                sheet.update_cell(student_row, 6, note)
        else:
            # Добавляем новую запись
            # Находим первую пустую строку начиная с 8-й строки (ученики)
            all_values = sheet.get_all_values()
            new_row_num = 8
            for i, row in enumerate(all_values):
                if i < 7:
                    continue
                if len(row) == 0 or not row[0]:
                    new_row_num = i + 1
                    break
                new_row_num = i + 2
            
            # Создаем новую строку
            new_row = [""] * sheet.col_count
            new_row[0] = f"{student_name} {student_class}" if student_class else student_name  # ФИО и класс в A
            new_row[date_col - 1] = "да"  # Отметка о занятии
            
            if note:
                new_row[5] = note  # Примечания в колонке F (индекс 5)
            
            # Добавляем строку
            sheet.update(f"A{new_row_num}", [new_row])
        
        return True
        
    except Exception as e:
        print(f"Ошибка при добавлении ученика: {e}")
        return False


def get_teacher_info(teacher_name):
    """Получает информацию о преподавателе из админской таблицы"""
    try:
        admin_sheet = get_admin_sheet()
        
        # Получаем все значения таблицы
        all_values = admin_sheet.get_all_values()
        
        # Проверяем, что таблица не пустая
        if len(all_values) < 4:
            print(f"Таблица преподавателей пуста или неполная (строк: {len(all_values)})")
            return None
        
        # Ожидаемые заголовки в 3-й строке (индекс 2)
        headers = ["ФИО", "Телефон", "Telegram ID", "Username", "Предмет", "Классы", "Дата регистрации"]
        
        # Начинаем чтение данных с 4-й строки (индекс 3)
        for i in range(3, len(all_values)):
            row = all_values[i]
            if len(row) == 0 or not row[0].strip():  # Пропускаем пустые строки
                continue
                
            fio = row[0].strip() if len(row) > 0 else ""
            if fio and fio.lower() == teacher_name.strip().lower():
                return {
                    "ФИО": fio,
                    "Телефон": row[1] if len(row) > 1 else "",
                    "Telegram ID": row[2] if len(row) > 2 else "",
                    "Username": row[3] if len(row) > 3 else "",
                    "Предмет": row[4] if len(row) > 4 else "",
                    "Классы": row[5] if len(row) > 5 else "",
                    "Дата регистрации": row[6] if len(row) > 6 else "",
                }

        print(f"Преподаватель {teacher_name} не найден в таблице")
        return None
    except Exception as e:
        print(f"Критическая ошибка в get_teacher_info: {str(e)}")
        return None
