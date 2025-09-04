import os
import requests
import json
import base64
import urllib.parse
from typing import Optional, Union, List, Dict, Any

class AKGPT:
    def __init__(self):
        """
        Инициализация клиента AKGPT
        API ключ уже встроен в библиотеку
        """
        self.api_url = "https://text.pollinations.ai/openai"
        self.api_key = "K9IvlvLqomg9BcEL"  # Встроенный API ключ
        
        # Список всех поддерживаемых моделей
        self.available_models = [
            "deepseek-reasoning",
            "gemini",
            "gpt-5-nano",
            "mistral",
            "nova-fast",
            "openai",
            "openai-audio",
            "openai-fast",
            "openai-large",
            "openai-reasoning",
            "qwen-coder",
            "roblox-rp",
            "bidara",
            "evil",
            "midijourney",
            "mirexa",
            "rtist",
            "sur",
            "unity"
        ]
        
        # Список поддерживаемых голосов для генерации речи
        self.available_voices = [
            "alloy", "echo", "fable", "onyx", "nova", "shimmer", 
            "coral", "verse", "ballad", "ash", "sage", "amuch", 
            "aster", "brook", "clover", "dan", "elan", "marilyn", 
            "meadow", "jazz", "rio", "megan-wetherall", "jade-hardy", 
            "megan-wetherall-2025-03-07"
        ]
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def query(self, 
              prompt: str, 
              model: str = "openai",
              system: Optional[str] = None,
              max_tokens: Optional[int] = None,
              temperature: Optional[float] = None,
              top_p: Optional[float] = None,
              presence_penalty: Optional[float] = None,
              frequency_penalty: Optional[float] = None,
              stream: bool = False) -> Optional[Union[str, Dict]]:
        """
        Отправка текстового запроса к API
        
        Args:
            prompt (str): Текстовый промпт
            model (str): Модель для использования
            system (str): Системный промпт
            max_tokens (int): Максимальное количество токенов
            temperature (float): Температура генерации
            top_p (float): Параметр top_p
            presence_penalty (float): Штраф за присутствие
            frequency_penalty (float): Штраф за частоту
            stream (bool): Потоковая передача
            
        Returns:
            Ответ от API или None в случае ошибки
        """
        if model not in self.available_models:
            print(f"Предупреждение: Модель '{model}' не в списке поддерживаемых моделей")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages
        }
        
        # Добавляем дополнительные параметры если они указаны
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if presence_penalty is not None:
            data["presence_penalty"] = presence_penalty
        if frequency_penalty is not None:
            data["frequency_penalty"] = frequency_penalty
        if stream:
            data["stream"] = True
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return None

    def query_with_image(self, 
                        prompt: str, 
                        image_base64: str,
                        model: str = "openai",
                        system: Optional[str] = None,
                        max_tokens: Optional[int] = None) -> Optional[Dict]:
        """
        Отправка запроса с изображением
        
        Args:
            prompt (str): Текстовый промпт
            image_base64 (str): Изображение в формате base64
            model (str): Модель для использования
            system (str): Системный промпт
            max_tokens (int): Максимальное количество токенов
            
        Returns:
            Ответ от API или None в случае ошибки
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        # Формируем сообщение с изображением
        content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            }
        ]
        
        messages.append({"role": "user", "content": content})
        
        data = {
            "model": model,
            "messages": messages
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе с изображением: {e}")
            return None

    def query_with_audio(self, 
                        prompt: str, 
                        audio_base64: str,
                        audio_format: str = "wav",
                        model: str = "openai-audio",
                        system: Optional[str] = None) -> Optional[Dict]:
        """
        Отправка запроса с аудио
        
        Args:
            prompt (str): Текстовый промпт
            audio_base64 (str): Аудио в формате base64
            audio_format (str): Формат аудио (wav, mp3, etc.)
            model (str): Модель для использования (рекомендуется openai-audio)
            system (str): Системный промпт
            
        Returns:
            Ответ от API или None в случае ошибки
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        # Формируем сообщение с аудио
        content = [
            {"type": "text", "text": prompt},
            {
                "type": "input_audio",
                "input_audio": {
                    "data": audio_base64,
                    "format": audio_format
                }
            }
        ]
        
        messages.append({"role": "user", "content": content})
        
        data = {
            "model": model,
            "messages": messages
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе с аудио: {e}")
            return None

    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Кодирование изображения в base64
        
        Args:
            image_path (str): Путь к файлу изображения
            
        Returns:
            Строка base64 или None в случае ошибки
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Ошибка при кодировании изображения: {e}")
            return None

    def encode_audio_to_base64(self, audio_path: str) -> Optional[str]:
        """
        Кодирование аудио в base64
        
        Args:
            audio_path (str): Путь к файлу аудио
            
        Returns:
            Строка base64 или None в случае ошибки
        """
        try:
            with open(audio_path, "rb") as audio_file:
                return base64.b64encode(audio_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Ошибка при кодировании аудио: {e}")
            return None

    def text_to_speech(self, 
                      text: str, 
                      voice: str = "nova",
                      model: str = "openai-audio") -> Optional[bytes]:
        """
        Генерация речи из текста
        
        Args:
            text (str): Текст для преобразования в речь
            voice (str): Голос для использования (по умолчанию "nova")
            model (str): Модель для использования (по умолчанию "openai-audio")
            
        Returns:
            Аудио данные в формате bytes или None в случае ошибки
        """
        if voice not in self.available_voices:
            print(f"Предупреждение: Голос '{voice}' не в списке поддерживаемых голосов")
        
        # Используем старый API endpoint для генерации речи
        speech_url = "https://text.pollinations.ai"
        encoded_text = urllib.parse.quote(text)
        url = f"{speech_url}/{encoded_text}"
        
        params = {
            "model": model,
            "voice": voice
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при генерации речи: {e}")
            return None

    def save_audio(self, audio_data: bytes, filename: str) -> bool:
        """
        Сохранение аудио данных в файл
        
        Args:
            audio_data (bytes): Аудио данные
            filename (str): Имя файла для сохранения
            
        Returns:
            True если сохранение успешно, False в случае ошибки
        """
        try:
            with open(filename, "wb") as audio_file:
                audio_file.write(audio_data)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении аудио: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """
        Получение списка доступных моделей
        
        Returns:
            Список названий моделей
        """
        return self.available_models.copy()

    def get_available_voices(self) -> List[str]:
        """
        Получение списка доступных голосов
        
        Returns:
            Список названий голосов
        """
        return self.available_voices.copy()

# Примеры использования
if __name__ == "__main__":
    # Инициализация клиента (токен уже встроен)
    client = AKGPT()

    print("\n=== ДЕМОНСТРАЦИЯ НОВЫХ ВОЗМОЖНОСТЕЙ AKGPT ===\n")

    # 1. Обычный текстовый запрос
    print("1. Обычный текстовый запрос:")
    result = client.query("Привет! Расскажи о себе.", model="openai")
    if result:
        print("Ответ:", result.get('choices', [{}])[0].get('message', {}).get('content', 'Нет ответа'))
    
    # 2. Запрос с системным промптом
    print("\n2. Запрос с системным промптом:")
    result_system = client.query(
        "Напиши короткое стихотворение о роботах", 
        model="mistral", 
        system="Ты талантливый поэт",
        max_tokens=150
    )
    if result_system:
        print("Ответ:", result_system.get('choices', [{}])[0].get('message', {}).get('content', 'Нет ответа'))

    # 3. Получение списка доступных моделей
    print("\n3. Доступные модели:")
    models = client.get_available_models()
    print("Всего моделей:", len(models))
    print("Первые 5 моделей:", models[:5])

    # 4. Пример работы с изображением (требует реальный файл)
    print("\n4. Пример работы с изображением:")
    print("Для тестирования с изображением используйте:")
    print("image_base64 = client.encode_image_to_base64('path/to/image.jpg')")
    print("result = client.query_with_image('Опиши это изображение', image_base64)")

    # 5. Пример работы с аудио (требует реальный файл)
    print("\n5. Пример работы с аудио:")
    print("Для тестирования с аудио используйте:")
    print("audio_base64 = client.encode_audio_to_base64('path/to/audio.wav')")
    print("result = client.query_with_audio('Расшифруй это аудио', audio_base64, 'wav')")

    # 6. Генерация речи из текста
    print("\n6. Генерация речи из текста:")
    print("Доступные голоса:", client.get_available_voices()[:5], "...")
    print("Пример использования:")
    print("audio_data = client.text_to_speech('Привет мир!', voice='nova')")
    print("client.save_audio(audio_data, 'speech.wav')")

    print("\n=== ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===")


