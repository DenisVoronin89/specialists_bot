import asyncio
import re
import pytest

# pytest-asyncio >=0.23 auto mode, else use marker
pytestmark = pytest.mark.asyncio

from types import SimpleNamespace

# Импортируем тестируемые функции и константы
from bot import handle_message, start_command, FIO, PHONE, SUBJECT, CLASSES, get_fio, get_phone, get_subject, get_classes
from config import AUTHORIZED_CHAT_ID


class DummyMessage:
    def __init__(self, text=""):
        self.text = text
        self.sent_texts = []

    async def reply_text(self, text, reply_markup=None):
        self.sent_texts.append(text)


class DummyUser:
    def __init__(self, user_id=111, username="user", full_name="Teacher Full Name"):
        self.id = user_id
        self.username = username
        self.full_name = full_name


class DummyChat:
    def __init__(self, chat_id=AUTHORIZED_CHAT_ID):
        self.id = chat_id


class DummyUpdate:
    def __init__(self, user_id=111, chat_id=AUTHORIZED_CHAT_ID, text=""):
        self.effective_user = DummyUser(user_id=user_id)
        self.effective_chat = DummyChat(chat_id=chat_id)
        self.message = DummyMessage(text=text)


class DummyContext:
    def __init__(self):
        self.user_data = {}


@pytest.fixture
def dummy_context():
    return DummyContext()


async def _call(coro):
    return await coro


async def _handle(update, context):
    return await handle_message(update, context)


@pytest.mark.asyncio
async def test_registration_entry_triggers_fio_state(monkeypatch, dummy_context):
    """КРИТИЧНО: Проверяет запуск регистрации при первом сообщении"""
    import registration
    monkeypatch.setattr(registration, "is_registered", lambda _tid: False)

    upd = DummyUpdate(user_id=999, chat_id=AUTHORIZED_CHAT_ID, text="Любой текст")

    state = await _handle(upd, dummy_context)

    # Должно вернуть состояние FIO и отправить подсказку
    assert state == FIO
    assert len(upd.message.sent_texts) == 1
    assert "Введите ваше ФИО полностью" in upd.message.sent_texts[0]


@pytest.mark.asyncio
async def test_get_classes_validation_success(monkeypatch, dummy_context):
    """КРИТИЧНО: Проверяет завершение регистрации с выбором классов"""
    # Подготавливаем данные пользователя
    dummy_context.user_data["fio"] = "Тестовый Пользователь Bot"
    dummy_context.user_data["phone"] = "+79990000001"
    dummy_context.user_data["subject"] = "Математика"
    
    # Мокаем только register_teacher чтобы не создавать реальную запись
    import registration
    monkeypatch.setattr(registration, "register_teacher", lambda data: True)
    
    upd = DummyUpdate(text="средние")
    
    state = await get_classes(upd, dummy_context)
    
    assert state == -1  # ConversationHandler.END
    assert "Регистрация завершена" in upd.message.sent_texts[-1]
    assert dummy_context.user_data["classes"] == "средние"


@pytest.mark.asyncio
async def test_handle_message_registered_teacher_adds_lesson(monkeypatch, dummy_context):
    """КРИТИЧНО: Проверяет основную функцию - добавление занятия"""
    import registration
    import lessons

    # Мокаем регистрацию: пользователь зарегистрирован
    monkeypatch.setattr(registration, "is_registered", lambda _tid: True)
    monkeypatch.setattr(registration, "get_teacher_name_by_id", lambda _tid: "Тестовый Учитель")

    # Мокаем только функцию process_lesson_message, чтобы не обращаться к Google Sheets
    def fake_process_lesson_message(teacher_name, message_text):
        return "✅ Запись добавлена:\n👤 Ученик: Петров Петр\n📚 Класс: 5\n📅 Дата: 15.08.2024\n📝 Примечание: замечание"

    monkeypatch.setattr(lessons, "process_lesson_message", fake_process_lesson_message)

    # Сообщение от учителя
    upd = DummyUpdate(user_id=111, chat_id=AUTHORIZED_CHAT_ID, text="Петров Петр 5 / замечание")

    await _handle(upd, dummy_context)

    # Ожидаем подтверждение
    assert any("✅ Запись добавлена" in s for s in upd.message.sent_texts)
    assert any("Петров Петр" in s for s in upd.message.sent_texts)


@pytest.mark.asyncio
async def test_unauthorized_chat_ignored(monkeypatch, dummy_context):
    """КРИТИЧНО: Проверяет безопасность - игнорирование неавторизованных чатов"""
    import registration
    monkeypatch.setattr(registration, "is_registered", lambda _tid: True)

    # Чат не авторизован - используем другой ID
    upd = DummyUpdate(user_id=111, chat_id=99999, text="Петров Петр 5")

    res = await _handle(upd, dummy_context)

    # Ничего не отправили, функция вернула None
    assert res is None
    assert upd.message.sent_texts == []


@pytest.mark.asyncio
async def test_handle_message_error_handling(monkeypatch, dummy_context):
    """ВАЖНО: Проверяет обработку ошибок"""
    import registration
    import lessons

    monkeypatch.setattr(registration, "is_registered", lambda _tid: True)
    monkeypatch.setattr(registration, "get_teacher_name_by_id", lambda _tid: "Тестовый Учитель")

    # Мокаем исключение в process_lesson_message
    def fake_process_lesson_message(teacher_name, message_text):
        raise Exception("Тестовая ошибка")

    monkeypatch.setattr(lessons, "process_lesson_message", fake_process_lesson_message)

    upd = DummyUpdate(user_id=111, chat_id=AUTHORIZED_CHAT_ID, text="Петров Петр 5")

    await _handle(upd, dummy_context)

    # Ожидаем сообщение об ошибке
    assert any("Ошибка при обработке сообщения" in s for s in upd.message.sent_texts) 