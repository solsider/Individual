from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards import main_kb

router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Выбирай действие кнопками 👇\n"
        "Команды тоже работают: /help /plan /summary /timer /explain /quiz /solve",
        reply_markup=main_kb
    )

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Что я умею:\n"
        "📝 Конспект\n"
        "🧭 План\n"
        "🧠 Объяснение\n"
        "❓ Тест\n"
        "🧩 Решение задач\n"
        "🍅 Таймер\n\n"
        "Нажимай кнопки внизу 👇"
    )

@router.message(F.text.in_({"⬅️ Главное меню", "❌ Отмена"}))
async def cancel_any(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ок, вернулись в меню 👇", reply_markup=main_kb)
