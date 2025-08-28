from google_sheets import append_student
from datetime import datetime


def process_lesson_message(teacher_name, message_text):
    """
    Обрабатывает сообщение о занятии от преподавателя
    
    Формат сообщения: "Фамилия Имя [класс] / примечания"
    Примеры:
    - "Петров Петр 5"
    - "Иванова Анна 7 / хорошо подготовилась"
    - "Сидоров Иван / пропустил занятие"
    """
    try:
        # Разделяем сообщение на основную часть и примечания
        if "/" in message_text:
            student_info, note = map(str.strip, message_text.split("/", 1))
        else:
            student_info, note = message_text.strip(), ""

        # Разбираем информацию об ученике
        parts = student_info.split()
        if len(parts) < 2:
            return "❌ Неверный формат. Нужно: Фамилия Имя [класс цифрой] / примечания\n\nПримеры:\n• Петров Петр 5\n• Иванова Анна 7 / хорошо подготовилась"

        # Извлекаем ФИО и класс
        student_name = " ".join(parts[:2])  # Фамилия Имя
        student_class = parts[2] if len(parts) > 2 else ""  # Класс (опционально)
        
        # Валидация класса (если указан)
        if student_class and not student_class.isdigit():
            return "❌ Класс должен быть указан цифрой (например: 5, 7, 11)"

        # Получаем текущую дату в формате DD.MM.YYYY
        date = datetime.now().strftime("%d.%m.%Y")

        # Добавляем запись в таблицу
        success = append_student(teacher_name, student_name, student_class, date, note)
        
        if success:
            # Формируем ответное сообщение
            response = f"✅ Запись добавлена:\n"
            response += f"👤 Ученик: {student_name}\n"
            if student_class:
                response += f"📚 Класс: {student_class}\n"
            response += f"📅 Дата: {date}\n"
            if note:
                response += f"📝 Примечание: {note}"
            
            return response
        else:
            return "❌ Ошибка при добавлении записи. Попробуйте еще раз."
            
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        return "❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз."


def validate_student_name(name):
    """Проверяет корректность имени ученика"""
    if not name or len(name.strip()) < 3:
        return False, "Имя ученика должно содержать минимум 3 символа"
    
    parts = name.split()
    if len(parts) < 2:
        return False, "Укажите Фамилию и Имя ученика"
    
    return True, ""


def validate_class(class_num):
    """Проверяет корректность номера класса"""
    if not class_num:
        return True, ""  # Класс необязателен
    
    if not class_num.isdigit():
        return False, "Класс должен быть указан цифрой"
    
    class_int = int(class_num)
    if class_int < 1 or class_int > 11:
        return False, "Класс должен быть от 1 до 11"
    
    return True, ""
