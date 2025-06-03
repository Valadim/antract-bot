import asyncio
import logging
from aiogram import Bot, types
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, COMPANY_NAME
from services.sheets import save_user, is_user_registered
from bot import dp
from bot.menu_handler import register_handlers as register_menu

# Настройка логгера
logging.basicConfig(level=logging.INFO)

# Создание бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# Состояния FSM для регистрации
class Registration(StatesGroup):
    fio = State()
    phone = State()


# Хендлер команды /start
@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    if is_user_registered(telegram_id):
        await message.answer("✅ Вы уже зарегистрированы.")
        return

    await message.answer("👤 Введите ваше <b>ФИО</b> (например, Иванов Иван):")
    await state.set_state(Registration.fio)


# FSM обработка ввода ФИО и телефона
@dp.message()
async def registration_flow(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == Registration.fio.state:
        await state.update_data(fio=message.text)

        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("📞 Отправьте номер телефона или введите вручную:", reply_markup=kb)
        await state.set_state(Registration.phone)

    elif current_state == Registration.phone.state:
        phone = message.contact.phone_number if message.contact else message.text.strip()
        data = await state.get_data()
        save_user(message.from_user.id, data["fio"], phone, COMPANY_NAME)

        await message.answer(
            f"✅ Спасибо, {data['fio']}!\nВы успешно зарегистрированы.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()


# Запуск бота
async def main():
    register_menu()
    print(f"✅ Бот запущен под компанией: {COMPANY_NAME}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
