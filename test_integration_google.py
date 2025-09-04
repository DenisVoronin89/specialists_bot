#!/usr/bin/env python3
"""
Интеграционный тест работы с реальными Google Sheets.
ТРЕБУЕТ корректных переменных в .env и доступа сервис-аккаунта к таблице.

Шаги:
1) Добавляет тестового преподавателя в лист "Преподаватели" (строка 4, если пусто)
2) Создает вкладку преподавателя по шаблону
3) Добавляет запись занятия (ученик, дата, примечание)
4) Проверяет значения в ячейках
5) Удаляет тестовую вкладку и строку из "Преподаватели"
"""

import os
from dotenv import load_dotenv
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

from google_sheets import (
    get_spreadsheet,
    get_admin_sheet,
    create_teacher_sheet,
    get_teacher_sheet,
    append_student,
    get_date_column
)

TEST_TEACHER = {
    "ФИО": "Тестовый Преподаватель QA",
    "Телефон": "+79990000000",
    "Telegram ID": 999000111,
    "Username": "qa_teacher",
    "Предмет": "Математика",
    "Классы": "средние, старшие",
}


def ensure_admin_row(sheet, teacher):
    values = sheet.get_all_values()
    
    # Находим первую пустую строку начиная с 4-й
    insert_row_index = 4
    for i in range(3, len(values)):  # Начинаем с индекса 3 (4-я строка)
        if len(values[i]) == 0 or not values[i][0].strip():  # Если строка пустая
            insert_row_index = i + 1  # gspread использует 1-based индексы
            break
    else:
        # Если все строки заполнены, добавляем в конец
        insert_row_index = len(values) + 1
    
    row = [
        teacher["ФИО"],
        teacher["Телефон"],
        teacher["Telegram ID"],
        teacher["Username"],
        teacher["Предмет"],
        teacher["Классы"],
        datetime.now().strftime("%d.%m.%Y"),
    ]
    
    # Используем insert_row только если нужно вставить в середину, иначе append_row
    if insert_row_index <= len(values):
        sheet.insert_row(row, index=insert_row_index)
    else:
        sheet.append_row(row)
    
    return insert_row_index


def main():
    load_dotenv()

    # Шаг 1: Добавляем преподавателя в админ-лист
    admin = get_admin_sheet()
    admin_row = ensure_admin_row(admin, TEST_TEACHER)
    print(f"✅ Добавлена строка преподавателя в 'Преподаватели': {admin_row}")

    # Шаг 2: Создаем вкладку преподавателя
    sheet = create_teacher_sheet(TEST_TEACHER["ФИО"])
    if not sheet:
        raise SystemExit("Не удалось создать вкладку преподавателя")
    print(f"✅ Создан лист преподавателя: {sheet.title}")

    # Шаг 3: Добавляем записи учеников (тестируем новую логику)
    today = datetime.now().strftime("%d.%m.%Y")
    
    # Тест 1: Ученик без примечания (должен быть зеленым)
    ok1 = append_student(TEST_TEACHER["ФИО"], "Петров Петр", "5", "математика", today, note="")
    if not ok1:
        raise SystemExit("Не удалось добавить запись ученика без примечания")
    print("✅ Запись ученика без примечания добавлена (зеленый)")
    
    # Тест 2: Ученик с примечанием (должен быть красным)
    ok2 = append_student(TEST_TEACHER["ФИО"], "Иванова Анна", "7", "физика", today, note="интеграционный тест")
    if not ok2:
        raise SystemExit("Не удалось добавить запись ученика с примечанием")
    print("✅ Запись ученика с примечанием добавлена (красный)")

    # Шаг 4: Проверяем значения на листе преподавателя
    sheet = get_teacher_sheet(TEST_TEACHER["ФИО"])  # получить свежий объект

    # Проверка шапки: B2 = ФИО, B3 = Телефон (по текущему шаблону)
    fio_cell = sheet.acell("B2").value
    phone_cell = sheet.acell("B3").value
    assert fio_cell == TEST_TEACHER["ФИО"], f"Ожидалось ФИО в B2: {TEST_TEACHER['ФИО']}, получено: {fio_cell}"
    assert phone_cell == TEST_TEACHER["Телефон"], f"Ожидался телефон в B3: {TEST_TEACHER['Телефон']}, получено: {phone_cell}"

    # Проверка отметок по дате
    date_col = get_date_column(sheet, today)
    assert date_col, f"Не найдена колонка для даты {today}"

    # Проверяем ученика без примечания (Петров Петр)
    all_values = sheet.get_all_values()
    petrov_row = None
    ivanova_row = None
    
    for i in range(7, len(all_values)):
        if len(all_values[i]) > 0 and all_values[i][0].startswith("Петров Петр 5 математика"):
            petrov_row = i + 1
        elif len(all_values[i]) > 0 and all_values[i][0].startswith("Иванова Анна 7 физика"):
            ivanova_row = i + 1
    
    assert petrov_row, "Не найдена строка ученика Петров Петр"
    assert ivanova_row, "Не найдена строка ученика Иванова Анна"

    # Проверяем Петрова (без примечания - должно быть "да")
    petrov_mark = sheet.cell(petrov_row, date_col).value
    assert petrov_mark == "да", f"Отметка Петрова должна быть 'да', получено: {petrov_mark}"

    # Проверяем Иванову (с примечанием - должно быть само примечание)
    ivanova_mark = sheet.cell(ivanova_row, date_col).value
    assert ivanova_mark == "интеграционный тест", f"Отметка Ивановой должна быть примечанием, получено: {ivanova_mark}"

    print("✅ Проверка листа преподавателя прошла успешно")

    # Шаг 5: Очистка — удалим вкладку и строку в админ-листе
    ss = get_spreadsheet()
    ws = get_teacher_sheet(TEST_TEACHER["ФИО"])
    if ws:
        ss.del_worksheet(ws)
        print("🧹 Удален лист преподавателя")

    admin.delete_rows(admin_row)
    print("🧹 Удалена строка преподавателя из 'Преподаватели'")

    print("🎉 Интеграционный тест завершен успешно")


if __name__ == "__main__":
    main() 