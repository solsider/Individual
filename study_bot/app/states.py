from aiogram.fsm.state import State, StatesGroup

class Flow(StatesGroup):
    waiting_summary = State()
    waiting_plan = State()
    waiting_explain = State()
    waiting_quiz = State()
    waiting_solve = State()
