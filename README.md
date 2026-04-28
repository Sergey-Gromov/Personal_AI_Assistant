<div align="center">

# Personal AI Assistant

### Мультимодальный Telegram-бот с голосом, изображениями и RAG-базой знаний

<p>
  <a href="https://github.com/">
    <img src="https://img.shields.io/badge/GitHub-ready-black" alt="GitHub ready" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12-blue" alt="Python 3.12" />
  </a>
  <a href="https://pypi.org/project/pyTelegramBotAPI/">
    <img src="https://img.shields.io/badge/Telegram-pyTelegramBotAPI-2CA5E0" alt="pyTelegramBotAPI" />
  </a>
  <a href="https://platform.openai.com/docs/">
    <img src="https://img.shields.io/badge/OpenAI-GPT%2C%20Vision%2C%20Whisper-412991" alt="OpenAI" />
  </a>
  <a href="https://www.langchain.com/">
    <img src="https://img.shields.io/badge/RAG-LangChain%20%2B%20ChromaDB-success" alt="LangChain and ChromaDB" />
  </a>
  <img src="https://img.shields.io/badge/status-MVP-success" alt="Status MVP" />
</p>

<p><strong>Личный AI-помощник прямо в Telegram: отвечает текстом, понимает голос, анализирует изображения, генерирует картинки и ищет ответы в локальных документах.</strong></p>
<p>Проект подготовлен для публикации на GitHub: секреты вынесены в <code>.env.example</code>, локальные данные и артефакты исключены из репозитория, тесты запускаются через <code>pytest</code> и GitHub Actions.</p>

<p>
  <a href="#-что-реализовано">Что реализовано</a> •
  <a href="#-структура-проекта">Структура</a> •
  <a href="#-быстрый-старт">Быстрый старт</a> •
  <a href="#-как-это-работает">Как это работает</a> •
  <a href="#-подготовка-к-публикации-на-github">GitHub</a>
</p>

</div>

---

## ✨ Что реализовано

- Текстовый диалог с OpenAI-совместимым API.
- Голосовой режим: распознавание речи через Whisper и ответ голосом через TTS.
- Анализ изображений с помощью Vision-модели.
- Генерация изображений по текстовому описанию.
- RAG-режим: ответы на основе локальных документов из `data/documents/`.
- Настраиваемый OpenAI-совместимый endpoint через `OPENAI_API_BASE`.
- Поддержка локального SOCKS5-прокси через `SOCKS_PROXY_URL` для OpenAI, RAG embeddings, DALL-E и Telegram.
- Автоматическое индексирование документов при старте, если база еще не создана.
- Набор тестов и CI workflow для GitHub Actions.

## 🧩 Режимы бота

- `text` - обычный текстовый помощник.
- `voice` - обработка голосовых сообщений и генерация аудиоответа.
- `vision` - анализ изображений и документов.
- `rag` - ответы с учетом локальной базы знаний.

Режим по умолчанию задается переменной `BOT_MODE` в `.env`.

## 📁 Структура проекта

```text
.
├── bot.py                  # Инициализация Telegram-бота
├── main.py                 # Точка входа и запуск polling
├── config.py               # Настройки и переменные окружения
├── handlers/               # Telegram-команды и обработчики сообщений
├── services/               # OpenAI, STT, TTS, Vision, image generation, router
├── rag/                    # Загрузка документов, ChromaDB и RAG-запросы
├── utils/                  # Логирование, файлы, аудио, пользовательские сессии
├── data/documents/         # Локальные документы для RAG
├── docs/                   # Дополнительная документация
├── tests/                  # Pytest-тесты
├── .github/workflows/      # CI для GitHub Actions
├── .env.example            # Шаблон локальных переменных окружения
└── README.md
```

## 🚀 Быстрый старт

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

Для голосовых функций нужен `FFmpeg`:

```bash
sudo apt-get install ffmpeg
```

## ⚙️ Настройка `.env`

Создайте `.env` из шаблона и укажите свои ключи:

```bash
cp .env.example .env
```

Минимальная конфигурация:

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
BOT_MODE=rag
DEFAULT_VOICE=alloy
LOG_LEVEL=INFO
```

Основные переменные:

- `TELEGRAM_BOT_TOKEN` - токен Telegram-бота из BotFather.
- `OPENAI_API_KEY` - ключ OpenAI или ProxyAPI.
- `USE_PROXYAPI` - `true` для ProxyAPI, `false` для официального OpenAI API.
- `TELEGRAM_PROXY_URL` - необязательный HTTP/SOCKS proxy для Telegram.
- `TELEGRAM_REQUEST_TIMEOUT` - timeout запросов к Telegram API.
- `BOT_MODE` - стартовый режим: `text`, `voice`, `vision` или `rag`.
- `DB_PATH` - путь к локальному хранилищу embeddings.
- `LOG_LEVEL` - уровень логирования.

### Прокси через sing-box

Если OpenAI недоступен напрямую, поднимите локальный SOCKS5-прокси, например sing-box на `127.0.0.1:1080`, и добавьте в `.env`:

```env
SOCKS_PROXY_URL=socks5://127.0.0.1:1080
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080
```

Эти настройки используются для OpenAI SDK, RAG embeddings, DALL-E-запросов и, если не задан `TELEGRAM_PROXY_URL`, для Telegram Bot API.

На сервере без блокировок можно оставить proxy-переменные пустыми:

```env
SOCKS_PROXY_URL=
HTTP_PROXY=
HTTPS_PROXY=
```

## ▶️ Запуск

Основной запуск:

```bash
source venv/bin/activate
python main.py
```

После запуска найдите своего бота в Telegram и отправьте `/start`.

Полезные команды бота:

- `/start` - начать работу.
- `/help` - показать справку.
- `/mode` - сменить режим.
- `/voice` - выбрать голос.
- `/reset` - очистить историю текущего пользователя.
- `/stats` - посмотреть статистику базы знаний.

## 🧠 Как это работает

1. Пользователь отправляет сообщение, голос, изображение или документ в Telegram.
2. Обработчики из `handlers/` принимают событие и передают его в `services/router.py`.
3. Роутер выбирает сценарий: текстовый ответ, STT/TTS, Vision, генерация изображения или RAG.
4. Для RAG выполняется поиск по ChromaDB, затем найденный контекст передается в LLM.
5. Бот возвращает пользователю текст, голосовой файл или сгенерированное изображение.

## 📚 RAG-база знаний

Добавьте документы в `data/documents/`:

- `.txt`
- `.md`
- `.pdf`

При старте бот проверит документы и создаст локальный индекс в `data/chroma_db/`. Содержимое `data/documents/` и `data/chroma_db/` не публикуется в GitHub, чтобы случайно не раскрыть приватные материалы.

Подробнее: `RAG_GUIDE.md`.

## 🎨 Генерация изображений

Бот умеет определять запросы на генерацию изображений и отправлять их в DALL-E-совместимый API.

Примеры запросов:

```text
Нарисуй кота в космосе
Создай изображение футуристического города
Сгенерируй картинку продукта для рекламы
```

Подробнее:

- `README_IMAGE_GENERATION.md`
- `docs/IMAGE_GENERATION.md`
- `IMAGE_GENERATION_QUICKSTART.md`

## 🧪 Тесты

```bash
source venv/bin/activate
pytest
```

Покрыты:

- обработка текстовых запросов;
- определение намерения генерации изображения;
- RAG-загрузка и запросы к базе знаний;
- STT/TTS-обвязка;
- вспомогательные функции.

Текущий локальный результат проверки:

```text
50 passed, 2 skipped
```

## 🛠️ Технологии

- `Python 3.12`
- `pyTelegramBotAPI`
- `OpenAI Python SDK`
- `LangChain`
- `ChromaDB` / `langchain-chroma`
- `pydub`
- `FFmpeg`
- `aiohttp`
- `httpx` с SOCKS-поддержкой
- `pytest`
- `GitHub Actions`

## 🔒 Подготовка к публикации на GitHub

- В репозитории должен быть только `.env.example`, без реального `.env`.
- `.gitignore` исключает виртуальные окружения, логи, кеши, ChromaDB, локальные документы и временные файлы.
- Если реальные ключи уже попадали в рабочую папку, чат или историю git, перевыпустите их у провайдера.
- Перед коммитом проверьте список файлов:

```bash
git status --short
git add --dry-run .
```

Первичная публикация:

```bash
git add .
git commit -m "Prepare project for GitHub publication"
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

## 📖 Дополнительная документация

- `START_HERE.md` - подробный быстрый старт.
- `RAG_GUIDE.md` - настройка базы знаний.
- `PROXYAPI_SETUP.md` - настройка OpenAI-совместимого endpoint и SOCKS-прокси.
- `VISUAL_GUIDE.md` - визуальное описание проекта.
- `SUMMARY_CHANGES.md` - сводка изменений.

## ⚠️ Ограничения

- Для реальной работы нужны токен Telegram-бота и OpenAI/OpenAI-совместимый API ключ.
- Голосовые функции требуют установленный `FFmpeg`.
- Индекс RAG создается локально и не хранится в репозитории.
- Интеграционные тесты с реальным API пропущены по умолчанию, чтобы не тратить средства.

## 🎯 Назначение проекта

Проект подходит как учебный и портфолио-MVP для:

- персонального AI-помощника в Telegram;
- демонстрации мультимодальных возможностей LLM;
- работы с локальной базой знаний через RAG;
- примера безопасной подготовки Python-проекта к публикации на GitHub.

## 📄 Лицензия

Проект распространяется по лицензии MIT. См. `LICENSE`.
