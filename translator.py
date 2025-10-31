import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

class Translator:
    def __init__(self):
        self.cache = {}
    
    async def translate_to_russian(self, text):
        """Перевод текста на русский язык с кэшированием"""
        if not text or len(text.strip()) < 10:
            return text
            
        # Проверяем кэш
        cache_key = hash(text)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Пробуем разные сервисы перевода
        translated = await self.try_libretranslate(text)
        if not translated:
            translated = await self.try_mymemory(text)
        
        # Если перевод не удался, возвращаем оригинал
        if not translated:
            translated = text
        
        # Сохраняем в кэш
        self.cache[cache_key] = translated
        return translated
    
    async def try_libretranslate(self, text):
        """Пробуем LibreTranslate API"""
        try:
            url = "https://libretranslate.com/translate"
            data = {
                "q": text,
                "source": "en",
                "target": "ru",
                "format": "text"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('translatedText', '')
        except Exception as e:
            logger.debug(f"LibreTranslate error: {e}")
        
        return None
    
    async def try_mymemory(self, text):
        """Пробуем MyMemory Translation API"""
        try:
            url = f"https://api.mymemory.translated.net/get"
            params = {
                "q": text,
                "langpair": "en|ru"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        translation = result.get('responseData', {}).get('translatedText', '')
                        if translation and translation != text:
                            return translation
        except Exception as e:
            logger.debug(f"MyMemory error: {e}")
        
        return None
    
    async def detect_language(self, text):
        """Определение языка текста"""
        if not text:
            return 'ru'
        
        # Простая эвристика для определения русского текста
        russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        text_lower = text.lower()
        
        russian_count = sum(1 for char in text_lower if char in russian_chars)
        total_letters = sum(1 for char in text_lower if char.isalpha())
        
        if total_letters == 0:
            return 'en'
        
        russian_ratio = russian_count / total_letters
        return 'ru' if russian_ratio > 0.3 else 'en'

# Глобальный экземпляр переводчика
translator = Translator()