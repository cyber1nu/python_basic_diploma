import os
from dotenv import load_dotenv, find_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')


if not find_dotenv(dotenv_path):
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
