# Генерация изображений с DALL-E 3 🎨

> **Ваш Telegram бот теперь умеет создавать изображения!**

## Быстрый старт ⚡

### 1. Установите зависимости

```bash
pip install aiohttp>=3.9.0
```

### 2. Используйте бота

Просто напишите:
```
Нарисуй кота в космосе
```

Или используйте команду:
```
/image красный автомобиль на дороге
```

## Примеры 💡

```
👤 Нарисуй закат на пляже
🤖 [Отправляет красивое изображение]

👤 Создай футуристический город
🤖 [Отправляет изображение города]

👤 Сгенерируй дракона
🤖 [Отправляет изображение дракона]
```

## Особенности ✨

- ✅ **Автоматическое определение** - ИИ понимает когда нужно создать изображение
- ✅ **Улучшение промптов** - GPT автоматически улучшает описание
- ✅ **DALL-E 3** - генерация изображений высокого качества
- ✅ **Русский и English** - поддержка двух языков
- ✅ **Простота использования** - просто опишите что хотите

## Ключевые слова 🔑

Бот понимает:
- **Нарисуй** / Draw
- **Создай изображение** / Create image
- **Сгенерируй картинку** / Generate picture
- **Покажи как выглядит** / Show me what
- **Визуализируй** / Visualize

## Стоимость 💰

- Standard 1024×1024: **$0.040** за изображение
- HD 1024×1024: **$0.080** за изображение

⚠️ Проверьте баланс на [platform.openai.com](https://platform.openai.com)

## Документация 📚

- 📖 [Быстрый старт](IMAGE_GENERATION_QUICKSTART.md) - начните здесь
- 📘 [Полная документация](docs/IMAGE_GENERATION.md) - все детали
- 🎬 [Демонстрация](IMAGE_GENERATION_DEMO.md) - примеры и сценарии
- 📋 [Changelog](CHANGELOG_IMAGE_GENERATION.md) - что нового
- 🛠️ [Настройка](SETUP_IMAGE_GENERATION.txt) - инструкция по установке

## Примеры кода 💻

```python
from services.image_generation import generate_image

# Генерация изображения
result = await generate_image(
    prompt="A cat in space",
    size="1024x1024",
    quality="standard"
)

print(result['image_path'])
```

Больше примеров: [examples/image_generation_examples.py](examples/image_generation_examples.py)

## Архитектура 🏗️

```
Пользователь
    ↓
handlers/text.py (обработка сообщений)
    ↓
services/router.py (маршрутизация)
    ↓
services/image_generation.py
    ├── detect_image_generation_intent() - определение намерения
    ├── generate_image() - генерация через DALL-E 3
    └── download_image() - загрузка результата
    ↓
Telegram (отправка изображения)
```

## Файлы 📁

### Новые:
- `services/image_generation.py` - основной сервис
- `docs/IMAGE_GENERATION.md` - документация
- `examples/image_generation_examples.py` - примеры
- `tests/test_image_generation.py` - тесты

### Обновленные:
- `services/router.py` - добавлен роутинг
- `handlers/text.py` - добавлена команда /image
- `config.py` - добавлены параметры DALL-E
- `requirements.txt` - добавлен aiohttp

## Тестирование 🧪

```bash
# Запуск тестов
pytest tests/test_image_generation.py

# Запуск примеров
python examples/image_generation_examples.py
```

## Настройка ⚙️

В `config.py`:

```python
DALLE_DEFAULT_SIZE = "1024x1024"  # 1024x1024, 1024x1792, 1792x1024
DALLE_DEFAULT_QUALITY = "standard"  # standard, hd
DALLE_DEFAULT_STYLE = "vivid"  # vivid, natural
```

## Troubleshooting 🔧

### Ошибка: "Quota exceeded"
→ Пополните баланс на platform.openai.com

### Ошибка: "Content policy violation"
→ Перефразируйте запрос (избегайте запрещенного контента)

### Ошибка: "Module aiohttp not found"
→ `pip install aiohttp>=3.9.0`

## Советы 💡

✅ **Будьте конкретны**: "красный спортивный автомобиль" лучше "машина"

✅ **Указывайте стиль**: "в стиле акварели", "фотореалистично"

✅ **Добавьте детали**: освещение, настроение, цвета

✅ **Используйте референсы**: "в стиле Ван Гога"

## Поддержка 🤝

Нашли проблему? Есть вопросы?

1. Проверьте [документацию](docs/IMAGE_GENERATION.md)
2. Посмотрите [примеры](examples/image_generation_examples.py)
3. Проверьте [troubleshooting](IMAGE_GENERATION_DEMO.md#-troubleshooting)

## Лицензия 📄

Согласно основной лицензии проекта

---

**Создавайте потрясающие изображения с вашим ИИ-ботом! 🚀**


