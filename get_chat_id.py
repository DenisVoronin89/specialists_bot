import os
import asyncio
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хэндлер для всех сообщений
@dp.message()
async def get_chat_id(message: types.Message):
    print("Chat ID:", message.chat.id)
    await message.answer("Chat ID logged in console.")

async def main():
    try:
        print("Bot started. Send any message in the group to get the Chat ID.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
