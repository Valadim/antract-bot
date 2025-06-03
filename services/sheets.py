import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from config import GOOGLE_CREDENTIALS_JSON, SPREADSHEET_NAME

# Авторизация
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_JSON, scopes=scope)
client = gspread.authorize(creds)

# Таблица
spreadsheet = client.open(SPREADSHEET_NAME)

# Листы
users_sheet = spreadsheet.worksheet("Users")
menu_sheet = spreadsheet.worksheet("Menu")
orders_sheet = spreadsheet.worksheet("Orders")

# --- Пользователь ---

def is_user_registered(telegram_id):
    ids = users_sheet.col_values(1)
    return str(telegram_id) in ids

def save_user(telegram_id, fio, phone, company):
    users_sheet.append_row([str(telegram_id), fio, phone, company])

def get_user_by_id(telegram_id):
    all_users = users_sheet.get_all_records()
    for user in all_users:
        if str(user["Telegram ID"]) == str(telegram_id):
            return user
    return None

# --- Меню ---

def get_menu_by_type(meal_type, date):
    records = menu_sheet.get_all_records()
    result = []
    for row in records:
        if row["Тип"].strip().lower() == meal_type.strip().lower() and row["Дата"] == date:
            result.append(row)
    return result

# --- Заказы ---

def save_order(order_data: list):
    """
    Пример данных:
    order_data = [
        "2025-06-03",     # дата заказа
        "05.06.2025",     # дата доставки
        "Иванов Иван",    # ФИО
        "+79991234567",   # телефон
        "Акситех",        # компания
        "Обед",           # приём пищи
        "Плов, Салат",    # блюда
        "Без лука",       # комментарий
        "20:35"           # время
    ]
    """
    orders_sheet.append_row(order_data)
