# AKGPT - Python клиент для Pollinations.ai API

AKGPT - это мощная Python библиотека для взаимодействия с API от Pollinations.ai. Поддерживает работу с текстом, изображениями и аудио через различные AI модели.

## 🚀 Новые возможности v0.1.0

- ✅ Поддержка всех 19 моделей Pollinations.ai
- ✅ Встроенный API ключ (не требует настройки)
- ✅ Работа с изображениями (base64)
- ✅ Работа с аудио файлами (base64)
- ✅ Генерация речи из текста (24 голоса)
- ✅ Улучшенная типизация и документация
- ✅ Автоматическое кодирование файлов в base64

## 📦 Установка

```bash
pip install akgpt
```

## 🔑 Инициализация

```python
from akgpt import AKGPT

# Инициализация (API ключ уже встроен в библиотеку)
client = AKGPT()
```

## 📝 Текстовые запросы

### Базовый запрос

```python
result = client.query("Привет! Расскажи о себе.", model="openai")
if result:
    content = result['choices'][0]['message']['content']
    print(content)
```

### Запрос с системным промптом

```python
result = client.query(
    prompt="Напиши стихотворение о роботах",
    model="mistral",
    system="Ты талантливый поэт",
    max_tokens=150,
    temperature=0.7
)
```

### Получение списка моделей

```python
models = client.get_available_models()
print(f"Доступно моделей: {len(models)}")
print(models)
```

## 🖼️ Работа с изображениями

### Анализ изображения

```python
# Кодирование изображения в base64
image_base64 = client.encode_image_to_base64("path/to/image.jpg")

# Запрос с изображением
result = client.query_with_image(
    prompt="Опиши это изображение",
    image_base64=image_base64,
    model="openai",
    max_tokens=300
)

if result:
    description = result['choices'][0]['message']['content']
    print(description)
```

### Пример с системным промптом

```python
result = client.query_with_image(
    prompt="Что ты видишь на этом изображении?",
    image_base64=image_base64,
    model="openai",
    system="Ты эксперт по анализу изображений",
    max_tokens=200
)
```

## 🎵 Работа с аудио

### Транскрипция аудио

```python
# Кодирование аудио в base64
audio_base64 = client.encode_audio_to_base64("path/to/audio.wav")

# Запрос с аудио
result = client.query_with_audio(
    prompt="Расшифруй это аудио",
    audio_base64=audio_base64,
    audio_format="wav",
    model="openai-audio"
)

if result:
    transcription = result['choices'][0]['message']['content']
    print(transcription)
```

### Анализ аудио с системным промптом

```python
result = client.query_with_audio(
    prompt="Проанализируй эмоции в этом аудио",
    audio_base64=audio_base64,
    audio_format="wav",
    model="openai-audio",
    system="Ты эксперт по анализу эмоций в речи"
)
```

## 🎤 Генерация речи из текста

### Базовое преобразование текста в речь

```python
# Генерация речи с голосом по умолчанию (nova)
audio_data = client.text_to_speech("Привет! Это тестовая генерация речи.")

# Сохранение в файл
if audio_data:
    client.save_audio(audio_data, "speech.wav")
    print("Аудио файл сохранен!")
```

### Выбор голоса

```python
# Получение списка доступных голосов
voices = client.get_available_voices()
print(f"Доступно голосов: {len(voices)}")
print("Первые 5 голосов:", voices[:5])

# Генерация с выбранным голосом
audio_data = client.text_to_speech(
    text="Привет! Меня зовут Nova и я говорю этим голосом.",
    voice="nova"
)

# Сохранение
if audio_data:
    client.save_audio(audio_data, "nova_speech.wav")
```

### Примеры с разными голосами

```python
# Мужские голоса
audio_data = client.text_to_speech("Привет, я мужской голос", voice="onyx")
client.save_audio(audio_data, "male_voice.wav")

# Женские голоса  
audio_data = client.text_to_speech("Привет, я женский голос", voice="shimmer")
client.save_audio(audio_data, "female_voice.wav")

# Креативные голоса
audio_data = client.text_to_speech("Привет, я креативный голос", voice="coral")
client.save_audio(audio_data, "creative_voice.wav")
```

## 🤖 Поддерживаемые модели

Библиотека поддерживает все 19 моделей Pollinations.ai:

- **Текстовые модели**: `openai`, `mistral`, `gemini`, `nova-fast`, `openai-fast`, `openai-large`, `openai-reasoning`
- **Специализированные**: `deepseek-reasoning`, `qwen-coder`, `roblox-rp`
- **Креативные**: `bidara`, `evil`, `midijourney`, `mirexa`, `rtist`, `sur`, `unity`
- **Аудио**: `openai-audio`
- **Экспериментальные**: `gpt-5-nano`

## 🎤 Поддерживаемые голоса

Библиотека поддерживает 24 голоса для генерации речи:

- **Классические**: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- **Креативные**: `coral`, `verse`, `ballad`, `ash`, `sage`
- **Специальные**: `amuch`, `aster`, `brook`, `clover`, `dan`, `elan`, `marilyn`, `meadow`, `jazz`, `rio`
- **Персональные**: `megan-wetherall`, `jade-hardy`, `megan-wetherall-2025-03-07`

## 📋 Параметры методов

### `query()` - Текстовые запросы

- `prompt` (str): Текстовый промпт
- `model` (str): Модель для использования (по умолчанию "openai")
- `system` (str): Системный промпт
- `max_tokens` (int): Максимальное количество токенов
- `temperature` (float): Температура генерации (0.0-2.0)
- `top_p` (float): Параметр top_p (0.0-1.0)
- `presence_penalty` (float): Штраф за присутствие (-2.0 до 2.0)
- `frequency_penalty` (float): Штраф за частоту (-2.0 до 2.0)
- `stream` (bool): Потоковая передача

### `query_with_image()` - Запросы с изображениями

- `prompt` (str): Текстовый промпт
- `image_base64` (str): Изображение в base64
- `model` (str): Модель (по умолчанию "openai")
- `system` (str): Системный промпт
- `max_tokens` (int): Максимальное количество токенов

### `query_with_audio()` - Запросы с аудио

- `prompt` (str): Текстовый промпт
- `audio_base64` (str): Аудио в base64
- `audio_format` (str): Формат аудио (по умолчанию "wav")
- `model` (str): Модель (по умолчанию "openai-audio")
- `system` (str): Системный промпт

### `text_to_speech()` - Генерация речи

- `text` (str): Текст для преобразования в речь
- `voice` (str): Голос (по умолчанию "nova")
- `model` (str): Модель (по умолчанию "openai-audio")

### `save_audio()` - Сохранение аудио

- `audio_data` (bytes): Аудио данные
- `filename` (str): Имя файла для сохранения

## 🔧 Вспомогательные методы

### Кодирование файлов

```python
# Кодирование изображения
image_base64 = client.encode_image_to_base64("image.jpg")

# Кодирование аудио
audio_base64 = client.encode_audio_to_base64("audio.wav")
```

### Получение информации

```python
# Список доступных моделей
models = client.get_available_models()

# Список доступных голосов
voices = client.get_available_voices()

# Проверка API ключа
print(f"API ключ: {client.api_key[:10]}...")
```

## 📚 Полный пример использования

```python
from akgpt import AKGPT
import json

# Инициализация
client = AKGPT()

# 1. Текстовый запрос
print("=== ТЕКСТОВЫЙ ЗАПРОС ===")
result = client.query("Расскажи анекдот", model="mistral")
if result:
    print(result['choices'][0]['message']['content'])

# 2. Работа с изображением
print("\n=== АНАЛИЗ ИЗОБРАЖЕНИЯ ===")
image_base64 = client.encode_image_to_base64("photo.jpg")
if image_base64:
    result = client.query_with_image(
        "Опиши это изображение",
        image_base64,
        model="openai"
    )
    if result:
        print(result['choices'][0]['message']['content'])

# 3. Работа с аудио
print("\n=== ТРАНСКРИПЦИЯ АУДИО ===")
audio_base64 = client.encode_audio_to_base64("recording.wav")
if audio_base64:
    result = client.query_with_audio(
        "Расшифруй это аудио",
        audio_base64,
        model="openai-audio"
    )
    if result:
        print(result['choices'][0]['message']['content'])

# 4. Генерация речи
print("\n=== ГЕНЕРАЦИЯ РЕЧИ ===")
voices = client.get_available_voices()
print(f"Доступно голосов: {len(voices)}")
audio_data = client.text_to_speech("Привет! Это тестовая генерация речи.", voice="nova")
if audio_data:
    client.save_audio(audio_data, "test_speech.wav")
    print("Аудио файл сохранен!")

# 5. Информация о моделях
print("\n=== ДОСТУПНЫЕ МОДЕЛИ ===")
models = client.get_available_models()
print(f"Всего моделей: {len(models)}")
for i, model in enumerate(models[:5], 1):
    print(f"{i}. {model}")
```

## ⚠️ Важные замечания

1. **API ключ**: Встроен в библиотеку, дополнительная настройка не требуется
2. **Форматы файлов**: Поддерживаются стандартные форматы изображений (JPEG, PNG) и аудио (WAV, MP3)
3. **Размер файлов**: Следите за ограничениями API на размер файлов
4. **Модели**: Некоторые модели могут быть недоступны или иметь ограничения

## 🐛 Обработка ошибок

```python
result = client.query("Тестовый запрос")
if result is None:
    print("Произошла ошибка при запросе к API")
else:
    print("Запрос выполнен успешно")
```

## 📄 Лицензия

Эта библиотека распространяется под лицензией MIT. Подробности см. в файле `LICENSE`.

## 🔄 История версий

- **v0.1.0**: Добавлена поддержка изображений, аудио, генерации речи и всех моделей Pollinations.ai
- **v0.0.2**: Базовая функциональность для текстовых запросов