from telegram import Bot
from telegram.request import HTTPXRequest
from dotenv import load_dotenv
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_ID")
request = HTTPXRequest(connect_timeout=10, read_timeout=10)
bot = Bot(token=TOKEN, request=request)

async def send_message(text, retries=3, delay=5):
    logger.info(f"Отправка сообщения: {text[:50]}...")
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text)
            logger.debug("Сообщение успешно отправлено")
            return
        except Exception as e:
            logger.warning(f"Попытка {attempt + 1}/{retries} не удалась: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error(f"Все попытки отправки сообщения провалились: {e}")
                raise