# Настройка OpenAI API и SOCKS-прокси

Проект использует OpenAI-совместимый API. Endpoint и прокси настраиваются через `.env`, без правок Python-кода.

## Основная схема

- `OPENAI_API_KEY` - ключ OpenAI или OpenAI-совместимого провайдера.
- `OPENAI_API_BASE` - базовый URL API, например `https://api.openai.com/v1`.
- `SOCKS_PROXY_URL` - локальный SOCKS5-прокси, например sing-box на `127.0.0.1:1080`.
- `HTTP_PROXY` / `HTTPS_PROXY` - стандартные переменные окружения для библиотек, которые читают proxy из окружения.
- `TELEGRAM_PROXY_URL` - отдельный proxy для Telegram, если он нужен. Если не задан, Telegram использует `SOCKS_PROXY_URL`.

## Direct OpenAI без прокси

Подходит для VPS в странах, где OpenAI и Telegram доступны напрямую.

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

SOCKS_PROXY_URL=
HTTP_PROXY=
HTTPS_PROXY=

TELEGRAM_REQUEST_TIMEOUT=90
```

После изменения `.env` перезапустите бота:

```bash
python main.py
```

## OpenAI через локальный SOCKS5

Если OpenAI недоступен напрямую, поднимите локальный SOCKS5-прокси, например sing-box на `127.0.0.1:1080`, и укажите:

```env
OPENAI_API_BASE=https://api.openai.com/v1

SOCKS_PROXY_URL=socks5://127.0.0.1:1080
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080
```

Эта настройка используется для:

- текстовых запросов через OpenAI SDK;
- Vision, Whisper и TTS через OpenAI SDK;
- RAG embeddings через `langchain-openai`;
- DALL-E-запросов и скачивания изображений через `aiohttp`;
- Telegram Bot API, если `TELEGRAM_PROXY_URL` не задан отдельно.

## Telegram напрямую, OpenAI через прокси

По умолчанию `TELEGRAM_PROXY_URL` берется из `SOCKS_PROXY_URL`, поэтому при включенном `SOCKS_PROXY_URL` Telegram тоже пойдет через тот же локальный прокси.

Если нужен режим "OpenAI через прокси, Telegram напрямую", текущую конфигурацию нужно доработать отдельным флагом или отдельной переменной для OpenAI-only proxy.

Практичный вариант для большинства случаев - оставить Telegram через тот же локальный SOCKS5:

```env
SOCKS_PROXY_URL=socks5://127.0.0.1:1080
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080
```

## OpenAI-совместимый провайдер

Если используется ProxyAPI или другой OpenAI-совместимый провайдер, меняются только ключ и `OPENAI_API_BASE`:

```env
OPENAI_API_KEY=your-provider-api-key-here
OPENAI_API_BASE=https://provider.example.com/openai/v1
```

Для ProxyAPI укажите base URL из документации провайдера. Старый флаг `USE_PROXYAPI` больше не используется.

## Зависимости для SOCKS

Для работы SOCKS-прокси нужны зависимости из `requirements.txt`:

```text
httpx[socks]>=0.27.0
PySocks>=1.7.1
aiohttp-socks>=0.10.1
```

Установить или обновить зависимости:

```bash
python -m pip install -r requirements.txt
```

Зачем нужны эти пакеты:

- `httpx[socks]` - SOCKS-поддержка для OpenAI SDK и embeddings.
- `PySocks` - SOCKS-поддержка для `requests`, которую использует `tiktoken` при загрузке tokenizer cache.
- `aiohttp-socks` - SOCKS-поддержка для Telegram transport и DALL-E `aiohttp` запросов.

## Проверка

Проверить импорт OpenAI-клиента:

```bash
python -c "from services.openai_client import openai_client; print('OpenAI client OK')"
```

Проверить RAG-поиск:

```bash
python - <<'PY'
from rag.index import vector_index
results = vector_index.similarity_search_with_score("test", k=1)
print(f"RAG search OK, results={len(results)}")
PY
```

Ожидаемые логи при включенном прокси:

```text
OpenAI client initialized with base URL: https://api.openai.com/v1
OpenAI proxy enabled
```

## Частые ошибки

### Using SOCKS proxy, but the 'socksio' package is not installed

Установите зависимости с SOCKS extras:

```bash
python -m pip install "httpx[socks]"
```

### Missing dependencies for SOCKS support

Обычно это означает, что `requests` пытается идти через SOCKS, но не установлен `PySocks`:

```bash
python -m pip install PySocks
```

### Connection timeout

Проверьте, что sing-box запущен и слушает нужный порт:

```bash
ss -ltnp | grep 1080
```

Также убедитесь, что URL в `.env` совпадает с портом sing-box:

```env
SOCKS_PROXY_URL=socks5://127.0.0.1:1080
```

## Переключение между режимами

После любого изменения `.env` перезапустите бота:

```bash
python main.py
```

Код менять не нужно: все токены, endpoint и proxy читаются из переменных окружения.
