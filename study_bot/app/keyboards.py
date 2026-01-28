from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Конспект"), KeyboardButton(text="🧭 План")],
        [KeyboardButton(text="🧠 Объяснить"), KeyboardButton(text="❓ Тест")],
        [KeyboardButton(text="🧩 Решить задачу"), KeyboardButton(text="🍅 Таймер")],
        [KeyboardButton(text="ℹ️ Помощь")],
    ],
    resize_keyboard=True,
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Главное меню"), KeyboardButton(text="❌ Отмена")],
    ],
    resize_keyboard=True,
)
