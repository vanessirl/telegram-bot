import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import ChatJoinRequest
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramServerError

BOT_TOKEN = "8936267028:AAH74MO6J3ig0DcuKK1azT7Tn60HdNeB--I"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.chat_join_request()
async def approve_request(request: ChatJoinRequest):
    while True:
        try:
            await request.approve()
            print(f"Заявка одобрена для {request.from_user.id}")
            break
        except TelegramRetryAfter as e:
            print(f"Флуд-контроль. Ждем {e.timeout} сек.")
            await asyncio.sleep(e.timeout)
        except TelegramBadRequest as e:
            print(f"Ошибка запроса (пропускаем): {e}")
            break
        except TelegramServerError as e:
            print(f"Сбой серверов Telegram (503/500). Повтор через 3 сек...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Другая ошибка (пропускаем): {e}")
            break

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    # Простой HTTP-сервер для ублажения Render
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("Удаляем активный вебхук и запускаем бота...")
    await bot.delete_webhook(drop_pending_updates=True)

    print("Бот успешно запущен и ожидает заявки!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
