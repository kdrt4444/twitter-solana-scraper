import asyncio
import re
import requests
from selenium import webdriver
from random import randint
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tg_bot import send_message
import time
import pytesseract
import cv2
import numpy as np
import pickle
import xpath
from swapper import swap
import platform
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень по умолчанию: INFO и выше
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Динамическое определение путей
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = "Tesseract-OCR/tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")


def find_solana_addresses(text):
    pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
    addresses = re.findall(pattern, text)
    if addresses:
        return addresses[0]
    return None

async def main(twitter_user, amount=0.001):
    logger.info(f"Запуск мониторинга для пользователя: {twitter_user} с суммой: {amount}")
    text = ""
    try:
        driver = webdriver.Chrome(options=chrome_options)
        logger.debug("WebDriver успешно инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации WebDriver: {e}")
        return

    driver.get(f"https://x.com/{twitter_user}")
    try:
        with open("twitter_cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        logger.info("Куки успешно загружены")
    except FileNotFoundError:
        logger.warning("Файл twitter_cookies.pkl не найден")

    while True:
        driver.refresh()
        logger.debug("Страница обновлена")
        try:
            new_text = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath.text_xpath))
            ).text
            logger.debug("Текст твита успешно получен")
        except Exception as e:
            logger.error(f"Ошибка при получении текста: {e}")
            new_text = None

        try:
            img_element = driver.find_element(By.XPATH, xpath.img_xpath)
            img_url = img_element.get_attribute("src")
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                text_img = pytesseract.image_to_string(gray, lang="eng")
                if new_text is None:
                    new_text = ""
                new_text += f"\nТекст с изображения:\n{text_img}"
                logger.debug("Текст с изображения успешно извлечен")
        except NoSuchElementException:
            logger.debug("Изображение не найдено на странице")
        except Exception as e:
            logger.warning(f"Ошибка при обработке изображения: {e}")

        if text != new_text and new_text is not None:
            text = new_text
            message = f"Найден новый твит, текст твита:\n{text}"
            logger.info(f"Обнаружен новый твит: {text[:50]}...")  # Укорачиваем для читаемости
            address = find_solana_addresses(text)
            if address is not None:
                logger.info(f"Найден Solana адрес: {address}")
                try:
                    await send_message(message + f"\nНайден solana address: {address}")
                    success = await swap(address=address, amount=amount)
                    if success:
                        logger.info(f"Swap выполнен для адреса: {address}")
                        break
                    else:
                        logger.warning(f"Swap не удался для адреса: {address}")
                except Exception as e:
                    logger.error(f"Ошибка при выполнении операций: {e}")
            else:
                try:
                    await send_message(message)
                    logger.debug("Сообщение отправлено без адреса")
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения: {e}")

        time.sleep(randint(45, 60))
    driver.quit()
    logger.info("Завершение работы")

if __name__ == "__main__":
    twitter_user = sys.argv[1] if len(sys.argv) > 1 else "elonmusk"
    amount = float(sys.argv[2]) if len(sys.argv) > 2 else 0.56
    asyncio.run(main(twitter_user, amount))
