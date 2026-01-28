import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states import Flow
from app.keyboards import main_kb, cancel_kb
from app.utils import send_long, llm_answer

from llm import chat
from prompts import SUMMARY_PROMPT, PLAN_PROMPT, EXPLAIN_PROMPT, QUIZ_PROMPT, SOLVE_PROMPT

router = Router()

def _stop_event():
    return asyncio.Event()

# ----- входы в режимы (команды) -----
@router.message(Command("summary"))
async def summary_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_summary)
    await message.answer("Пришли текст лекции одним сообщением или .txt файлом.", reply_markup=cancel_kb)

@router.message(Command("plan"))
async def plan_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_plan)
    await message.answer("Напиши тему/цель. Например: “Линейная алгебра, экзамен через 2 недели”", reply_markup=cancel_kb)

@router.message(Command("explain"))
async def explain_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_explain)
    await message.answer("Что объяснить? Напиши тему одним сообщением.", reply_markup=cancel_kb)

@router.message(Command("quiz"))
async def quiz_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_quiz)
    await message.answer("Напиши тему. Можно так: “Интегралы, 10 вопросов”", reply_markup=cancel_kb)

@router.message(Command("solve"))
async def solve_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_solve)
    await message.answer("Пришли условие задачи текстом.", reply_markup=cancel_kb)

# ----- обработка ввода по состояниям -----
@router.message(Flow.waiting_summary, F.text)
async def summary_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = SUMMARY_PROMPT.format(content=message.text)
    out = await llm_answer(message.bot, message, _stop_event, chat, prompt)
    await send_long(message, out)
    await message.answer("Готово ✅ Что дальше?", reply_markup=main_kb)

@router.message(Flow.waiting_summary, F.document)
async def summary_file(message: Message, state: FSMContext):
    await state.clear()
    doc = message.document
    if not doc.file_name.lower().endswith(".txt"):
        await message.answer("Пока принимаю только .txt. Или вставь текст сообщением.", reply_markup=cancel_kb)
        return

    file = await message.bot.get_file(doc.file_id)
    content = await message.bot.download_file(file.file_path)
    text = content.read().decode("utf-8", errors="ignore")[:20000]

    prompt = SUMMARY_PROMPT.format(content=text)
    out = await llm_answer(message.bot, message, _stop_event, chat, prompt)
    await send_long(message, out)
    await message.answer("Готово ✅ Что дальше?", reply_markup=main_kb)

@router.message(Flow.waiting_plan, F.text)
async def plan_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = PLAN_PROMPT.format(topic=message.text.strip())
    out = await llm_answer(message.bot, message, _stop_event, chat, prompt)
    await send_long(message, out)
    await message.answer("Готово ✅ Что дальше?", reply_markup=main_kb)

@router.message(Flow.waiting_explain, F.text)
async def explain_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = EXPLAIN_PROMPT.format(topic=message.text.strip())
    out = await llm_answer(message.bot, message, _stop_event, chat, prompt)
    await send_long(message, out)
    await message.answer("Готово ✅ Что дальше?", reply_markup=main_kb)

@router.message(Flow.waiting_quiz, F.text)
async def quiz_text(message: Message, state: FSMContext):
    await state.clear()
    text = message.text.strip()
    count = 10
    for token in text.split():
        if token.isdigit():
            count = max(3, min(30, int(token)))
            break
    prompt = QUIZ_PROMPT.format(topic=text, count=count)
    out = await llm_answer(message.bot, message, _stop_event, chat, prompt)
    await send_long(message, out)
    await message.answer("Готово ✅ Что дальше?", reply_markup=main_kb)

@router.message(Flow.waiting_solve, F.text)
async def solve_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = SOLVE_PROMPT.format(task=message.text)
    out = await llm_answer(message.bot, message, _stop_event, chat, prompt)
    await send_long(message, out)
    await message.answer("Готово ✅ Что дальше?", reply_markup=main_kb)

# ----- кнопки меню (важно: сбрасываем state перед переходом) -----
@router.message(F.text == "📝 Конспект")
async def btn_summary(message: Message, state: FSMContext):
    await state.clear()
    await summary_cmd(message, state)

@router.message(F.text == "🧭 План")
async def btn_plan(message: Message, state: FSMContext):
    await state.clear()
    await plan_cmd(message, state)

@router.message(F.text == "🧠 Объяснить")
async def btn_explain(message: Message, state: FSMContext):
    await state.clear()
    await explain_cmd(message, state)

@router.message(F.text == "❓ Тест")
async def btn_quiz(message: Message, state: FSMContext):
    await state.clear()
    await quiz_cmd(message, state)

@router.message(F.text == "🧩 Решить задачу")
async def btn_solve(message: Message, state: FSMContext):
    await state.clear()
    await solve_cmd(message, state)
