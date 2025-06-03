from aiogram import types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.sheets import get_menu_by_type
from bot import dp  # <-- импортируем dp отсюда


class MenuOrder(StatesGroup):
    select_date = State()
    select_meal = State()
    show_dishes = State()


def get_date_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(7):
        day = datetime.today() + timedelta(days=i)
        builder.button(
            text=day.strftime("%d.%m.%Y"),
            callback_data=f"date:{day.strftime('%d.%m.%Y')}"
        )
    builder.adjust(2)
    return builder.as_markup()


def get_meal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍳 Завтрак", callback_data="meal:Завтрак")],
        [InlineKeyboardButton(text="🥣 Обед", callback_data="meal:Обед")],
        [InlineKeyboardButton(text="🍽 Ужин", callback_data="meal:Ужин")],
    ])


@dp.message(Command("menu"))
async def menu_start(message: types.Message, state: FSMContext):
    await message.answer("📅 На какой день хотите сделать заказ?", reply_markup=get_date_keyboard())
    await state.set_state(MenuOrder.select_date)


@dp.callback_query(F.data.startswith("date:"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split(":", 1)[1]
    await state.update_data(date=date)
    await callback.message.edit_text(
        f"✅ Дата выбрана: {date}\nТеперь выберите приём пищи:",
        reply_markup=get_meal_keyboard()
    )
    await state.set_state(MenuOrder.select_meal)


@dp.callback_query(F.data.startswith("meal:"))
async def select_meal(callback: CallbackQuery, state: FSMContext):
    meal = callback.data.split(":", 1)[1]
    data = await state.get_data()
    date = data["date"]
    await state.update_data(meal=meal)

    dishes = get_menu_by_type(meal_type=meal, date=date)
    if not dishes:
        await callback.message.edit_text(f"😔 На {meal.lower()} {date} меню пока нет.")
        await state.clear()
        return

    text = f"📋 <b>Меню на {meal.lower()} {date}:</b>\n\n"
    for dish in dishes:
        text += f"• {dish['Название блюда']} — {dish['Цена']} ₽\n"

    await callback.message.edit_text(text)
    await state.clear()


# 👇 функция для регистрации (чтобы импортировать в main.py)
def register_handlers():
    # всё уже зарегистрировано через декораторы — просто заглушка
    pass
