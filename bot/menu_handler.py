from aiogram import types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.sheets import get_menu_by_type, save_order, get_user_by_id
from bot import dp


class MenuOrder(StatesGroup):
    select_date = State()
    select_meal = State()
    select_dishes = State()
    comment = State()


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

    builder = InlineKeyboardBuilder()
    for dish in dishes:
        builder.button(
            text=f"{dish['Название блюда']} ({dish['Цена']}₽)",
            callback_data=f"dish:{dish['Название блюда']}"
        )
    builder.button(text="✅ Готово", callback_data="done")
    builder.adjust(1)

    await state.update_data(selected_dishes=[])
    await callback.message.edit_text("🍽 Выберите блюда:", reply_markup=builder.as_markup())
    await state.set_state(MenuOrder.select_dishes)


@dp.callback_query(F.data.startswith("dish:"))
async def select_dish(callback: CallbackQuery, state: FSMContext):
    dish = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = data.get("selected_dishes", [])
    if dish not in selected:
        selected.append(dish)
        await state.update_data(selected_dishes=selected)
    await callback.answer(f"Добавлено: {dish}")


@dp.callback_query(F.data == "done")
async def done_selecting(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("selected_dishes"):
        await callback.answer("⚠️ Выберите хотя бы одно блюдо.", show_alert=True)
        return
    await callback.message.edit_text("✍️ Есть ли комментарий к заказу? (Напишите или отправьте «-»)")
    await state.set_state(MenuOrder.comment)


@dp.message(MenuOrder.comment)
async def receive_comment(message: types.Message, state: FSMContext):
    comment = message.text.strip()
    data = await state.get_data()
    user = get_user_by_id(message.from_user.id)

    now = datetime.now()
    save_order([
        now.strftime("%d.%m.%Y"),         # дата заказа
        data["date"],                     # дата доставки
        user.get("ФИО", "—"),
        user.get("Телефон", "—"),
        user.get("Компания", "—"),
        data["meal"],
        ", ".join(data["selected_dishes"]),
        comment if comment != "-" else "",
        now.strftime("%H:%M")
    ])

    await message.answer("✅ Ваш заказ принят и записан.")
    await state.clear()


def register_handlers():
    pass
