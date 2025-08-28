import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID"))

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")  # путь к JSON с сервис-аккаунтом
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
TEMPLATE_SHEET_NAME = "Шаблон"
ADMIN_SHEET_NAME = "Преподаватели"

# Настройки для работы с таблицами
MAX_ROWS = 1000
MAX_COLS = 50

# Форматы дат
DATE_FORMAT = "%d.%m.%Y"
DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
