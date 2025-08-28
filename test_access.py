import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

creds = Credentials.from_service_account_file(
    os.getenv("GOOGLE_CREDENTIALS_JSON"),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)

# Открываем таблицу
try:
    sheet = client.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1
    print("✅ Таблица открыта! Пример данных из A1:", sheet.acell("A1").value)
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {str(e)}")