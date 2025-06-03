import os
from dotenv import load_dotenv

# Загрузить переменные из .env
load_dotenv()

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
COMPANY_NAME = os.getenv("COMPANY_NAME")

# ID администраторов в виде списка целых чисел
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(',')))
