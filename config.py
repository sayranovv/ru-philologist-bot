import os
from pathlib import Path

from dotenv import load_dotenv

env_file = Path(__file__).parent / '.env'
load_dotenv(env_file)

TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
GIGACHAT_CREDENTIALS: str = os.getenv('GIGACHAT_CREDENTIALS', '')
DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./bot_database.db')
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
MAX_REQUESTS_PER_MINUTE: int = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '10'))
REQUEST_TIMEOUT_SECONDS: int = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '30'))

YANDEX_SPELLER_URL: str = 'https://speller.yandex.net/services/spellchecker.json/checkText'
OPENAI_API_URL: str = 'https://api.openai.com/v1/chat/completions'

MAX_MESSAGE_LENGTH: int = 1000
HISTORY_LIMIT: int = 10
