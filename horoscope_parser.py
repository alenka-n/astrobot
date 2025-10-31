import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from config import FALLBACK_HOROSCOPES, ZODIAC_URL_MAP
from translator import translator  # Импортируем переводчик

class HoroscopeParser:
    def __init__(self):
        self.cache = {}
    
    async def get_daily_horoscope(self, zodiac_sign, translate=True):
        """Получение гороскопа из интернета с возможностью перевода"""
        cache_key = f"{zodiac_sign}_{datetime.now().strftime('%Y%m%d')}"
        
        # Проверяем кэш
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Пробуем разные источники
        horoscope = await self.try_horoscope_api(zodiac_sign)
        if not horoscope:
            horoscope = await self.try_astroneo_site(zodiac_sign)
        
        # Если ничего не получилось, используем резервный
        if not horoscope:
            horoscope = FALLBACK_HOROSCOPES.get(zodiac_sign, "Сегодня звезды благоволят к вам! ✨")
            return horoscope
        
        # Проверяем язык и переводим если нужно
        if translate:
            language = await translator.detect_language(horoscope)
            if language == 'en':
                horoscope = await translator.translate_to_russian(horoscope)
        
        # Сохраняем в кэш
        self.cache[cache_key] = horoscope
        return horoscope
    
    async def try_horoscope_api(self, zodiac_sign):
        """Пробуем получить гороскоп через API"""
        try:
            eng_sign = ZODIAC_URL_MAP.get(zodiac_sign)
            if not eng_sign:
                return None
                
            url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={eng_sign}&day=TODAY"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        horoscope = data.get('data', {}).get('horoscope_data', '')
                        if horoscope and len(horoscope) > 20:
                            return horoscope
        except Exception as e:
            print(f"API Error: {e}")
        
        return None
    
    async def try_astroneo_site(self, zodiac_sign):
        """Пробуем парсить сайт astroneo.ru"""
        try:
            eng_sign = ZODIAC_URL_MAP.get(zodiac_sign)
            if not eng_sign:
                return None
                
            url = f"https://www.astroneo.ru/horoscope/daily/{eng_sign}/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Ищем текст гороскопа
                        content = soup.find('div', class_='horoscope-text')
                        if content:
                            text = content.get_text().strip()
                            if text and len(text) > 50:
                                return text
        except Exception as e:
            print(f"Site parsing error: {e}")
        
        return None
    
    def clear_cache(self, zodiac_sign=None):
        """Очистка кэша"""
        if zodiac_sign:
            # Удаляем только для конкретного знака
            keys_to_delete = [key for key in self.cache.keys() if key.startswith(zodiac_sign)]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            # Очищаем весь кэш
            self.cache.clear()

# Создаем глобальный экземпляр парсера
horoscope_parser = HoroscopeParser()