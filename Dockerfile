# Базовый образ с Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    libtesseract-dev \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
CMD ["ping", "google.com"]

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Устанавливаем переменные окружения для Tesseract
ENV TESSERACT_PATH=/usr/bin/tesseract

# Команда для запуска
CMD ["python", "main.py"]