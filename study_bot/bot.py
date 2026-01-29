import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import routers  

async def main():
    while True:
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()

        for r in routers:
            dp.include_router(r)

        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Polling crashed: {e}. Restarting in 5s...")
            try:
                await bot.session.close()
            except Exception:
                pass
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
