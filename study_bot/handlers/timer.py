import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards import main_kb

router = Router()

@router.message(Command("timer"))
async def timer_cmd(message: Message):
    await message.answer("🍅 Старт: 25 минут учебы. Потом будет 5 минут перерыв.")
    await asyncio.sleep(25 * 60)
    await message.answer("✅ 25 минут прошло! Перерыв 5 минут.")
    await asyncio.sleep(5 * 60)
    await message.answer("🔁 Перерыв закончился. Что дальше?", reply_markup=main_kb)

@router.message(F.text == "🍅 Таймер")
async def btn_timer(message: Message, state: FSMContext):
    await state.clear()
    await timer_cmd(message)
