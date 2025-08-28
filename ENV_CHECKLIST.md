# 📋 Чек-лист переменных окружения (.env)

## ✅ Необходимые переменные:

```env
# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN=your_telegram_bot_token_here

# Chat ID закрытого чата преподавателей (получить через get_chat_id.py)
AUTHORIZED_CHAT_ID=123456789

# Путь к JSON файлу сервис-аккаунта Google
GOOGLE_CREDENTIALS_JSON=path/to/your/service-account.json

# ID Google Таблицы (из URL)
SPREADSHEET_ID=1cfa8gVNvf7q_xrGVPf6odC3_RNxrpUjRpG7xogbGrWU
```

## 🔍 Проверка переменных:

### 1. BOT_TOKEN
- ✅ Получить у @BotFather в Telegram
- ✅ Формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- ✅ Должен начинаться с цифр и содержать двоеточие

### 2. AUTHORIZED_CHAT_ID
- ✅ Получить через `python get_chat_id.py`
- ✅ Отправить сообщение в нужный чат
- ✅ Скопировать Chat ID из консоли
- ✅ Должен быть числом (без кавычек)

### 3. GOOGLE_CREDENTIALS_JSON
- ✅ Путь к JSON файлу сервис-аккаунта
- ✅ Может быть абсолютным или относительным
- ✅ Примеры:
  - `./teacher-bot.json`
  - `/Users/user/credentials/service-account.json`

### 4. SPREADSHEET_ID
- ✅ ID из URL Google Таблицы
- ✅ Формат: длинная строка букв и цифр
- ✅ Из URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

## 🧪 Проверка настроек:

Запустите тест для проверки всех переменных:
```bash
python test_bot.py
```

## ❌ Частые ошибки:

1. **Неправильный Chat ID:**
   - Используйте `get_chat_id.py` для получения
   - Не путайте с ID пользователя

2. **Неправильный путь к JSON:**
   - Проверьте, что файл существует
   - Используйте правильные слеши для ОС

3. **Неправильный Spreadsheet ID:**
   - Скопируйте из URL таблицы
   - Убедитесь, что сервис-аккаунт имеет доступ

4. **Неправильный Bot Token:**
   - Получите новый у @BotFather если сомневаетесь
   - Проверьте формат токена 