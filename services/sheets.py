import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_CREDENTIALS_JSON, SPREADSHEET_NAME

# Настройка доступа
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_JSON, scope)
client = gspread.authorize(creds)

# Открываем таблицу по имени
spreadsheet = client.open(SPREADSHEET_NAME)

# Получаем нужные листы
menu_sheet = spreadsheet.worksheet("Menu")
orders_sheet = spreadsheet.worksheet("Orders")
users_sheet = spreadsheet.worksheet("Users")


# Сохраняем пользователя в таблицу Users
def save_user(telegram_id: int, fio: str, phone: str, company: str):
    users_sheet.append_row([telegram_id, fio, phone, company])


# Проверка, зарегистрирован ли пользователь
def is_user_registered(telegram_id: int) -> bool:
    records = users_sheet.get_all_records()
    return any(str(row.get("Telegram ID")) == str(telegram_id) for row in records)


def get_menu_by_type(meal_type: str, date: str):
    records = menu_sheet.get_all_records()
    return [row for row in records if row["Прием пищи"] == meal_type and row["Дата"] == date]
