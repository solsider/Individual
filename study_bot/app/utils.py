import asyncio
from aiogram.types import Message
from aiogram.enums import ChatAction

async def send_long(message: Message, text: str):
    for i in range(0, len(text), 3800):
        await message.answer(text[i:i + 3800])

async def typing_loop(bot, chat_id: int, stop_event: asyncio.Event):
    while not stop_event.is_set():
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=4.0)
        except asyncio.TimeoutError:
            pass

async def llm_answer(bot, message: Message, stop_event_factory, chat_func, prompt: str) -> str:
    stop = stop_event_factory()
    task = asyncio.create_task(typing_loop(bot, message.chat.id, stop))
    try:
        return await chat_func(prompt)
    finally:
        stop.set()
        await task
