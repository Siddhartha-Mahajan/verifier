import os
from dotenv import load_dotenv

load_dotenv()


URL_DATABASE = os.getenv("URL_DATABASE")
SERVICE_PORT = os.getenv("SERVICE_PORT")
SERVICE_REFRESH = os.getenv("SERVICE_REFRESH")
SERVICE_WORKERS = os.getenv("SERVICE_WORKERS")
SERVICE_HOST = os.getenv("SERVICE_HOST")
ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS")
RATE_LIMIT_PER_SECOND = os.getenv("RATE_LIMIT_PER_SECOND")
RATE_LIMIT_PER_MINUTE = os.getenv("RATE_LIMIT_PER_MINUTE")
RATE_LIMIT_PER_HOUR = os.getenv("RATE_LIMIT_PER_HOUR")
RATE_LIMIT_PER_DAY = os.getenv("RATE_LIMIT_PER_DAY")
API_VERSION = os.getenv("API_VERSION")
# Password gate for internal leaderboard endpoint.
LEADERBOARD_PASSWORD = os.getenv("LEADERBOARD_PASSWORD", "lossfunk123")