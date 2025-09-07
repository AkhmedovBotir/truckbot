import os
from typing import List

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8212230200:AAE61LLTlS86f2gUOaQ4-cDCKMn6u8t6MEw')

# Admin configuration - Add your Telegram user ID here
ADMIN_IDS: List[int] = [6237238997]  # Replace with actual admin user IDs

# Database configuration
DATABASE_PATH = 'bot_database.db'

# API URLs
CBU_API_URL = 'https://cbu.uz/uz/arkhiv-kursov-valyut/json/all/'

# Default settings
DEFAULT_CURRENCY = 'USD'
DEFAULT_SEND_TIME = '09:00'
DEFAULT_TEMPLATE = """💱 **Valyuta kursi yangilanishi**

Valyuta: {currency_name} ({currency_code})
Kurs: {rate} so'm
Sana: {date}

📊 O'zbekiston Respublikasi Markaziy Banki
"""