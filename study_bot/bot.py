import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.enums import ChatAction
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from llm import chat
from prompts import (
    SUMMARY_PROMPT, PLAN_PROMPT, EXPLAIN_PROMPT, QUIZ_PROMPT, SOLVE_PROMPT
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- Keyboard (buttons) ----------
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Конспект"), KeyboardButton(text="🧭 План")],
        [KeyboardButton(text="🧠 Объяснить"), KeyboardButton(text="❓ Тест")],
        [KeyboardButton(text="🧩 Решить задачу"), KeyboardButton(text="🍅 Таймер")],
        [KeyboardButton(text="ℹ️ Помощь")],
    ],
    resize_keyboard=True,
)

# ---------- FSM states ----------
class Flow(StatesGroup):
    waiting_summary = State()
    waiting_plan = State()
    waiting_explain = State()
    waiting_quiz = State()
    waiting_solve = State()


# ---------- helpers ----------
async def send_long(message: Message, text: str):
    # безопасно режем на куски (лимит Telegram ~4096)
    for i in range(0, len(text), 3800):
        await message.answer(text[i:i + 3800])


async def typing_loop(chat_id: int, stop_event: asyncio.Event):
    # поддерживаем "печатает..." пока не остановим
    while not stop_event.is_set():
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=4.0)
        except asyncio.TimeoutError:
            pass


async def llm_answer(message: Message, prompt: str) -> str:
    stop = asyncio.Event()
    task = asyncio.create_task(typing_loop(message.chat.id, stop))
    try:
        return await chat(prompt)
    finally:
        stop.set()
        await task


# ---------- commands ----------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я учебный бот.\n"
        "Выбирай действие кнопками 👇\n\n",

        reply_markup=main_kb
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Что я умею:\n"
        "📝 Конспект — /summary или кнопка «Конспект»\n"
        "🧭 План — /plan или кнопка «План»\n"
        "🧠 Объяснение — /explain или кнопка «Объяснить»\n"
        "❓ Тест — /quiz или кнопка «Тест»\n"
        "🧩 Решение задач — /solve или кнопка «Решить задачу»\n"
        "🍅 Таймер — /timer или кнопка «Таймер»\n\n"
        "Пример:\n"
        "1) Нажми «Конспект» → отправь лекцию\n"
        "2) Нажми «Решить задачу» → отправь условие"
    )


# ---------- Summary ----------
@dp.message(Command("summary"))
async def summary_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_summary)
    await message.answer("Пришли текст лекции одним сообщением или .txt файлом.")


@dp.message(Flow.waiting_summary, F.text)
async def summary_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = SUMMARY_PROMPT.format(content=message.text)
    out = await llm_answer(message, prompt)
    await send_long(message, out)


@dp.message(Flow.waiting_summary, F.document)
async def summary_file(message: Message, state: FSMContext):
    await state.clear()
    doc = message.document
    if not doc.file_name.lower().endswith(".txt"):
        await message.answer("Пока принимаю только .txt. Или вставь текст сообщением.")
        return

    file = await bot.get_file(doc.file_id)
    content = await bot.download_file(file.file_path)
    text = content.read().decode("utf-8", errors="ignore")[:20000]  # защита от огромных файлов

    prompt = SUMMARY_PROMPT.format(content=text)
    out = await llm_answer(message, prompt)
    await send_long(message, out)


# ---------- Plan ----------
@dp.message(Command("plan"))
async def plan_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_plan)
    await message.answer("Напиши тему/цель. Например: “Линейная алгебра, экзамен через 2 недели”")


@dp.message(Flow.waiting_plan, F.text)
async def plan_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = PLAN_PROMPT.format(topic=message.text.strip())
    out = await llm_answer(message, prompt)
    await send_long(message, out)


# ---------- Explain ----------
@dp.message(Command("explain"))
async def explain_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_explain)
    await message.answer("Что объяснить? Напиши тему одним сообщением.")


@dp.message(Flow.waiting_explain, F.text)
async def explain_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = EXPLAIN_PROMPT.format(topic=message.text.strip())
    out = await llm_answer(message, prompt)
    await send_long(message, out)


# ---------- Quiz ----------
@dp.message(Command("quiz"))
async def quiz_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_quiz)
    await message.answer("Напиши тему. Можно так: “Интегралы, 10 вопросов”")


@dp.message(Flow.waiting_quiz, F.text)
async def quiz_text(message: Message, state: FSMContext):
    await state.clear()
    text = message.text.strip()

    # простой парсер количества
    count = 10
    for token in text.split():
        if token.isdigit():
            count = max(3, min(30, int(token)))
            break

    prompt = QUIZ_PROMPT.format(topic=text, count=count)
    out = await llm_answer(message, prompt)
    await send_long(message, out)


# ---------- Solve ----------
@dp.message(Command("solve"))
async def solve_cmd(message: Message, state: FSMContext):
    await state.set_state(Flow.waiting_solve)
    await message.answer("Пришли условие задачи текстом.")


@dp.message(Flow.waiting_solve, F.text)
async def solve_text(message: Message, state: FSMContext):
    await state.clear()
    prompt = SOLVE_PROMPT.format(task=message.text)
    out = await llm_answer(message, prompt)
    await send_long(message, out)


# ---------- Timer ----------
@dp.message(Command("timer"))
async def timer_cmd(message: Message):
    await message.answer("🍅 Старт: 25 минут учебы. Потом будет 5 минут перерыв.")
    await asyncio.sleep(25 * 60)
    await message.answer("✅ 25 минут прошло! Перерыв 5 минут.")
    await asyncio.sleep(5 * 60)
    await message.answer("🔁 Перерыв закончился. Хочешь еще цикл — снова /timer")


# ---------- Buttons handlers ----------
@dp.message(F.text == "📝 Конспект")
async def btn_summary(message: Message, state: FSMContext):
    await summary_cmd(message, state)


@dp.message(F.text == "🧭 План")
async def btn_plan(message: Message, state: FSMContext):
    await plan_cmd(message, state)


@dp.message(F.text == "🧠 Объяснить")
async def btn_explain(message: Message, state: FSMContext):
    await explain_cmd(message, state)


@dp.message(F.text == "❓ Тест")
async def btn_quiz(message: Message, state: FSMContext):
    await quiz_cmd(message, state)


@dp.message(F.text == "🧩 Решить задачу")
async def btn_solve(message: Message, state: FSMContext):
    await solve_cmd(message, state)


@dp.message(F.text == "🍅 Таймер")
async def btn_timer(message: Message):
    await timer_cmd(message)


@dp.message(F.text == "ℹ️ Помощь")
async def btn_help(message: Message):
    await help_cmd(message)


# ---------- run ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
