### README.md (на русском)


# Twitter Solana Scraper

Это бот на Python, который отслеживает новые твиты указанного пользователя в Twitter (X), извлекает адреса кошельков Solana из текста твитов или изображений, отправляет уведомления в Telegram и выполняет обмен токенов на блокчейне Solana с помощью Jupiter SDK. Бот работает в Docker-контейнере для удобного запуска и масштабирования.

## Возможности
- Отслеживает твиты указанного пользователя Twitter в реальном времени.
- Извлекает адреса кошельков Solana из текста твитов или изображений с помощью OCR (Tesseract).
- Отправляет уведомления в Telegram с текстом твита и найденными адресами.
- Выполняет обмен токенов на Solana через Jupiter SDK.
- Ведёт логи всех действий для отладки и мониторинга.
- Работает в Docker-контейнере с автоматическим перезапуском.

## Требования
- **Python 3.12**: Используется для разработки и работы.
- **Docker**: Нужен для сборки и запуска контейнера.
- **Telegram-бот**: Создайте бота через [@BotFather](https://t.me/BotFather), чтобы получить `TG_TOKEN`.
- **Кошелёк Solana**: Приватный ключ для выполнения обмена.
- **Куки Twitter**: Файл `twitter_cookies.pkl` для авторизованного доступа к Twitter (X).

## Установка

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/yourusername/twitter-solana-scraper.git
cd twitter-solana-scraper
```

### 2. Настройте переменные окружения
Создайте файл `.env` в корне проекта, скопировав шаблон из `.env.example`:
```bash
cp .env.example .env
```
Отредактируйте `.env`, указав свои значения:
```
TG_TOKEN=ваш_токен_бота_telegram
TG_ID=ваш_id_чата_telegram
PRIVATE_KEY=ваш_приватный_ключ_solana
SOLANA_URL=https://api.mainnet-beta.solana.com
```
- `TG_TOKEN`: Получите у @BotFather.
- `TG_ID`: Узнайте через @userinfobot.
- `PRIVATE_KEY`: Приватный ключ вашего кошелька Solana.

### 3. Подготовьте куки Twitter
- Войдите в Twitter (X) в браузере, экспортируйте куки в файл `twitter_cookies.pkl` с помощью инструмента, например, [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg).
- Поместите `twitter_cookies.pkl` в корень проекта.

### 4. Соберите Docker-образ
```bash
docker build -t twitter-solana-scraper:latest .
```

### 5. Запустите контейнер локально
```bash
docker run -it --env-file .env twitter-solana-scraper:latest python main.py "имя_пользователя_twitter" "сумма_обмена"
```
- Замените `имя_пользователя_twitter` на имя пользователя.
- Замените `сумма_обмена` на сумму для обмена в SOL.

## Развертывание на сервере

### 1. Сохраните Docker-образ
```bash
docker save -o twitter-solana-scraper.tar twitter-solana-scraper:latest
```

### 2. Скопируйте на сервер
```bash
scp twitter-solana-scraper.tar root@ip_сервера:/root/
scp .env root@ip_сервера:/root/
```

### 3. Загрузите и запустите на сервере
Подключитесь к серверу:
```bash
ssh root@ip_сервера
```
Загрузите образ:
```bash
docker load -i /root/twitter-solana-scraper.tar
```
Запустите контейнер:
```bash
docker run -d --restart unless-stopped --env-file /root/.env twitter-solana-scraper:latest python main.py "имя_пользователя_twitter" "сумма_обмена"
```

### 4. Проверьте логи
```bash
docker ps  # Найдите CONTAINER_ID
docker logs <container_id>
```

## Структура проекта
```
twitter-solana-scraper/
├── main.py           # Главный скрипт для мониторинга и обработки твитов
├── swapper.py        # Логика обмена на Solana через Jupiter SDK
├── tg_bot.py         # Отправка уведомлений в Telegram
├── xpath.py          # XPath-селекторы для парсинга Twitter
├── twitter_cookies.pkl  # Куки для авторизации в Twitter
├── Dockerfile        # Конфигурация Docker
├── requirements.txt  # Зависимости Python
├── .env             # Переменные окружения (не добавляется в Git)
├── .env.example     # Шаблон переменных окружения
└── README.md        # Этот файл
```

## Зависимости
Полный список в `requirements.txt`. Основные зависимости:
- `selenium`: Для парсинга веб-страниц.
- `pytesseract`: Для распознавания текста на изображениях.
- `python-telegram-bot`: Для уведомлений в Telegram.
- `jupiter-python-sdk`: Для обмена токенов на Solana.
- `solana` и `solders`: Для работы с блокчейном Solana.

## Логирование
Бот записывает все действия (INFO, WARNING, ERROR) в консоль. Чтобы сохранить логи в файл:
1. Обновите `main.py`, добавив запись в `/app/logs/app.log`.
2. Запустите с томом:
```bash
docker run -d --env-file .env -v /root/logs:/app/logs twitter-solana-scraper:latest python main.py "имя_пользователя_twitter" "сумма_обмена"
```

## Устранение неполадок
- **Тайм-аут Telegram:** Увеличьте `connect_timeout` и `read_timeout` в `tg_bot.py` или проверьте интернет-соединение.
- **Предупреждения Selenium:** Игнорируйте или отключите телеметрию с помощью `os.environ["SELENIUM_DISABLE_TELEMETRY"] = "true"`.
- **Ошибки обмена:** Проверьте `PRIVATE_KEY` и `SOLANA_URL` в `.env`.
