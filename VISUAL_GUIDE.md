# 🎨 Visual Guide

Визуальное руководство по работе Personal Assistant Bot.

## 📊 Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                      TELEGRAM USER                           │
│                    (Отправляет сообщение)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   TELEGRAM BOT API                           │
│              (Получает и отправляет сообщения)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      BOT LAYER                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Dispatcher (aiogram)                          │  │
│  │  - Polling обновлений                                 │  │
│  │  - Роутинг по типу сообщения                         │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Commands   │  │     Text     │  │    Voice     │
│   Handler    │  │   Handler    │  │   Handler    │
│              │  │              │  │              │
│ /start       │  │ Text msgs    │  │ Voice msgs   │
│ /help        │  │ /mode        │  │ /voice       │
│ /reset       │  │              │  │              │
│ /stats       │  │              │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │      Image Handler             │
        │                                │
        │  Photos, Documents             │
        └────────────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ROUTER LAYER                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Request Router                           │  │
│  │  - route_text_request()                              │  │
│  │  - route_voice_request()                             │  │
│  │  - route_image_request()                             │  │
│  │  - route_rag_request()                               │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│     STT      │  │     TTS      │  │   Vision     │
│   Service    │  │   Service    │  │   Service    │
│              │  │              │  │              │
│ Whisper API  │  │  TTS API     │  │ GPT-4 Vision │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │      OpenAI Client             │
        │                                │
        │  - GPT-4o                      │
        │  - Whisper                     │
        │  - TTS                         │
        │  - Vision                      │
        └────────────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPENAI API                                │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Поток обработки запросов

### Текстовое сообщение

```
User: "Привет, как дела?"
  │
  ▼
[Telegram API]
  │
  ▼
[Dispatcher] → Определяет тип: TEXT
  │
  ▼
[Text Handler] → handle_text_message()
  │
  ▼
[Router] → route_text_request()
  │
  ├─→ Получить историю из UserSession
  ├─→ Добавить сообщение в историю
  │
  ▼
[OpenAI Client] → generate_text_response()
  │
  ▼
[GPT-4o API]
  │
  ▼
Response: "Привет! Отлично, спасибо! Чем могу помочь?"
  │
  ▼
[Сохранить в историю]
  │
  ▼
[Отправить пользователю]
```

### Голосовое сообщение

```
User: [Голосовое сообщение .ogg]
  │
  ▼
[Telegram API] → Скачать файл
  │
  ▼
[Voice Handler] → handle_voice_message()
  │
  ▼
[Router] → route_voice_request()
  │
  ├─→ [STT Service]
  │     │
  │     ├─→ Конвертировать OGG → WAV
  │     │
  │     ▼
  │   [Whisper API] → Транскрибировать
  │     │
  │     ▼
  │   Text: "Какая погода в Москве?"
  │
  ├─→ [route_text_request()] → Обработать как текст
  │     │
  │     ▼
  │   [GPT-4o] → Сгенерировать ответ
  │     │
  │     ▼
  │   Response: "Для получения актуальной погоды..."
  │
  └─→ [TTS Service]
        │
        ▼
      [TTS API] → Синтезировать речь
        │
        ▼
      Audio file: response.mp3
        │
        ▼
      [Отправить пользователю]
        ├─→ Текст транскрипции
        ├─→ Текст ответа
        └─→ Голосовой ответ
```

### Анализ изображения

```
User: [Фото кота]
  │
  ▼
[Telegram API] → Получить URL фото
  │
  ▼
[Image Handler] → handle_photo_message()
  │
  ▼
[Router] → route_image_request()
  │
  ▼
[Vision Service] → analyze_image()
  │
  ├─→ Подготовить URL
  │
  ▼
[GPT-4 Vision API]
  │
  ▼
Analysis: "На изображении домашний кот..."
  │
  ▼
[Отправить пользователю]
```

### RAG запрос

```
User: "Найди информацию о проекте X"
  │
  ▼
[Text Handler]
  │
  ▼
[Router] → Режим = RAG
  │
  ▼
[RAG Query] → query_knowledge_base()
  │
  ├─→ [Vector Index]
  │     │
  │     ├─→ Создать эмбеддинг запроса
  │     │
  │     ▼
  │   [ChromaDB] → Поиск похожих документов
  │     │
  │     ▼
  │   Results: [doc1, doc2, doc3]
  │
  ├─→ Подготовить контекст из документов
  │
  ▼
[GPT-4o] → Сгенерировать ответ с контекстом
  │
  ▼
Response: "Согласно документам..."
  │
  ▼
[Отправить пользователю]
```

## 🎯 Режимы работы

```
┌─────────────────────────────────────────────────────────┐
│                    BOT MODES                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │  TEXT MODE   │  │  VOICE MODE  │                    │
│  │  (default)   │  │              │                    │
│  │              │  │              │                    │
│  │  Text → GPT  │  │  Voice → TTS │                    │
│  │  → Text      │  │  + Text      │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ VISION MODE  │  │   RAG MODE   │                    │
│  │              │  │              │                    │
│  │  Image →     │  │  Query →     │                    │
│  │  Analysis    │  │  KB Search   │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 📚 RAG Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                  DOCUMENT LOADING                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  PDF/TXT Files                                          │
│       │                                                  │
│       ▼                                                  │
│  [Document Loader]                                      │
│       │                                                  │
│       ├─→ PyPDFLoader (PDF)                            │
│       └─→ TextLoader (TXT)                             │
│       │                                                  │
│       ▼                                                  │
│  Raw Documents                                          │
│       │                                                  │
│       ▼                                                  │
│  [Text Splitter]                                        │
│       │                                                  │
│       ├─→ Chunk size: 1000                             │
│       └─→ Overlap: 200                                 │
│       │                                                  │
│       ▼                                                  │
│  Document Chunks                                        │
│                                                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   INDEXING                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Document Chunks                                        │
│       │                                                  │
│       ▼                                                  │
│  [OpenAI Embeddings]                                    │
│       │                                                  │
│       └─→ text-embedding-ada-002                       │
│       │                                                  │
│       ▼                                                  │
│  Vector Embeddings (1536 dimensions)                   │
│       │                                                  │
│       ▼                                                  │
│  [ChromaDB]                                             │
│       │                                                  │
│       └─→ Store vectors + metadata                     │
│                                                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    QUERYING                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  User Query: "Найди информацию о бюджете"              │
│       │                                                  │
│       ▼                                                  │
│  [Create Query Embedding]                               │
│       │                                                  │
│       ▼                                                  │
│  [Similarity Search in ChromaDB]                        │
│       │                                                  │
│       ├─→ Top K=3 results                              │
│       │                                                  │
│       ▼                                                  │
│  Relevant Chunks + Scores                               │
│       │                                                  │
│       ▼                                                  │
│  [Prepare Context]                                      │
│       │                                                  │
│       ├─→ Format chunks                                │
│       └─→ Add source info                              │
│       │                                                  │
│       ▼                                                  │
│  Context String                                         │
│       │                                                  │
│       ▼                                                  │
│  [GPT-4o with Context]                                  │
│       │                                                  │
│       └─→ System prompt + Context + Query              │
│       │                                                  │
│       ▼                                                  │
│  Contextual Response                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🎭 User Session Management

```
┌─────────────────────────────────────────────────────────┐
│                  USER SESSION                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  User ID: 12345                                         │
│  │                                                       │
│  ├─→ Conversation History                              │
│  │    [                                                 │
│  │      {"role": "user", "content": "Hello"},          │
│  │      {"role": "assistant", "content": "Hi!"},       │
│  │      ...                                             │
│  │    ]                                                 │
│  │                                                       │
│  ├─→ Current Mode: "text"                              │
│  │                                                       │
│  └─→ Voice Setting: "alloy"                            │
│                                                          │
│  Max History: 10 messages (20 total with responses)    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔊 Voice Processing

```
┌─────────────────────────────────────────────────────────┐
│              VOICE MESSAGE FLOW                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Input: voice.ogg (Telegram format)                    │
│       │                                                  │
│       ▼                                                  │
│  [pydub] Convert OGG → WAV                              │
│       │                                                  │
│       ▼                                                  │
│  voice.wav                                              │
│       │                                                  │
│       ▼                                                  │
│  [Whisper API] Transcribe                               │
│       │                                                  │
│       ▼                                                  │
│  Text: "Какая погода?"                                  │
│       │                                                  │
│       ▼                                                  │
│  [Process as text request]                              │
│       │                                                  │
│       ▼                                                  │
│  Response Text                                          │
│       │                                                  │
│       ▼                                                  │
│  [TTS API] Synthesize                                   │
│       │                                                  │
│       ├─→ Voice: alloy/echo/nova/...                   │
│       │                                                  │
│       ▼                                                  │
│  response.mp3                                           │
│       │                                                  │
│       ▼                                                  │
│  [Send to user]                                         │
│       ├─→ Transcription                                │
│       ├─→ Text response                                │
│       └─→ Voice response                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    DATA STORAGE                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  In-Memory (Python)                                     │
│  ├─→ User Sessions                                      │
│  ├─→ Conversation History                               │
│  └─→ Bot State                                          │
│                                                          │
│  File System                                            │
│  ├─→ data/documents/     (Source documents)            │
│  ├─→ data/*.ogg, *.wav   (Temp audio)                  │
│  └─→ bot.log             (Logs)                        │
│                                                          │
│  ChromaDB (Persistent)                                  │
│  └─→ data/chroma_db/     (Vector embeddings)           │
│                                                          │
│  External APIs                                          │
│  ├─→ Telegram Bot API                                  │
│  └─→ OpenAI API                                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                  BOT LIFECYCLE                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. STARTUP                                             │
│     ├─→ Load config from .env                          │
│     ├─→ Initialize OpenAI client                       │
│     ├─→ Create bot and dispatcher                      │
│     ├─→ Register handlers                              │
│     ├─→ Index documents (if any)                       │
│     └─→ Start polling                                  │
│                                                          │
│  2. RUNNING                                             │
│     ├─→ Receive updates                                │
│     ├─→ Route to handlers                              │
│     ├─→ Process requests                               │
│     ├─→ Call OpenAI APIs                               │
│     └─→ Send responses                                 │
│                                                          │
│  3. SHUTDOWN                                            │
│     ├─→ Stop polling                                   │
│     ├─→ Close sessions                                 │
│     ├─→ Cleanup temp files                             │
│     └─→ Save state (if needed)                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🎨 Command Flow

```
User sends: /start
     │
     ▼
[start.py] cmd_start()
     │
     ├─→ Initialize user session
     ├─→ Set default mode
     └─→ Send welcome message
     
User sends: /mode rag
     │
     ▼
[text.py] cmd_mode()
     │
     ├─→ Parse argument
     ├─→ Validate mode
     ├─→ Update user session
     └─→ Confirm change

User sends: /voice nova
     │
     ▼
[voice.py] cmd_voice()
     │
     ├─→ Parse argument
     ├─→ Validate voice
     ├─→ Update user session
     └─→ Confirm change
```

---

**Визуальное руководство помогает понять архитектуру! 🎨**

