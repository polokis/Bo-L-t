from googletrans import Translator
import logging
from typing import Dict, Optional
import asyncio
import functools

logger = logging.getLogger(__name__)

class RTanksTranslator:
    """Translator for RTanks Online Russian content to English"""
    
    def __init__(self):
        self.translator = Translator()
        self.cache = {}
        
        # Pre-defined translations for common terms
        self.rank_translations = {
            'новобранец': 'recruit',
            'рядовой': 'private',
            'рядовой первого класса': 'private first class',
            'младший капрал': 'lance corporal',
            'капрал': 'corporal',
            'сержант': 'sergeant',
            'штаб-сержант': 'staff sergeant',
            'старший сержант': 'sergeant first class',
            'мастер-сержант': 'master sergeant',
            'уорэнт-офицер 1': 'warrant officer 1',
            'уорэнт-офицер 2': 'warrant officer 2',
            'уорэнт-офицер 3': 'warrant officer 3',
            'уорэнт-офицер 4': 'warrant officer 4',
            'уорэнт-офицер 5': 'warrant officer 5',
            'второй лейтенант': 'second lieutenant',
            'первый лейтенант': 'first lieutenant',
            'капитан': 'captain',
            'майор': 'major',
            'подполковник': 'lieutenant colonel',
            'полковник': 'colonel',
            'бригадный генерал': 'brigadier general',
            'генерал-майор': 'major general',
            'генерал-лейтенант': 'lieutenant general',
            'генерал': 'general',
            'генералиссимус': 'generalissimo',
            'легенда': 'legend'
        }
        
        self.common_translations = {
            'уничтожил': 'destroyed',
            'подбит': 'destroyed',
            'группа': 'group',
            'игрок': 'player',
            'премиум': 'premium',
            'да': 'yes',
            'нет': 'no',
            'поймано золотых ящиков': 'gold boxes caught',
            'опыт': 'experience',
            'кристаллы': 'crystals',
            'эффективность': 'efficiency',
            'рейтинг': 'rating',
            'место': 'rank',
            'киллы': 'kills',
            'смерти': 'deaths',
            'установленный': 'equipped',
            'стоимость': 'cost'
        }
    
    def translate_rank(self, rank_text: str) -> str:
        """Translate rank name from Russian to English"""
        if not rank_text:
            return 'Unknown Rank'
        
        # Normalize the text
        normalized = rank_text.lower().strip()
        
        # Check pre-defined translations first
        if normalized in self.rank_translations:
            return self.rank_translations[normalized].title()
        
        # If it's already in English, return as-is
        if all(ord(char) < 128 for char in rank_text):
            return rank_text.title()
        
        # Try Google Translate
        try:
            translated = self._translate_text_sync(rank_text)
            return translated.title() if translated else rank_text
        except Exception as e:
            logger.warning(f"Failed to translate rank '{rank_text}': {e}")
            return rank_text
    
    def translate_text(self, text: str) -> str:
        """Translate general text from Russian to English"""
        if not text:
            return ''
        
        # Check cache first
        if text in self.cache:
            return self.cache[text]
        
        # If it's already in English, return as-is
        if all(ord(char) < 128 for char in text if char.isalpha()):
            self.cache[text] = text
            return text
        
        # Check for common translations
        normalized = text.lower().strip()
        if normalized in self.common_translations:
            result = self.common_translations[normalized]
            self.cache[text] = result
            return result
        
        # Use Google Translate
        try:
            translated = self._translate_text_sync(text)
            if translated:
                self.cache[text] = translated
                return translated
        except Exception as e:
            logger.warning(f"Failed to translate text '{text}': {e}")
        
        # Return original if translation fails
        return text
    
    def _translate_text_sync(self, text: str) -> Optional[str]:
        """Synchronous translation using Google Translate"""
        try:
            # Detect language first
            detection = self.translator.detect(text)
            
            # Only translate if it's Russian
            if detection.lang == 'ru':
                result = self.translator.translate(text, src='ru', dest='en')
                return result.text
            else:
                return text
                
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    async def translate_text_async(self, text: str) -> str:
        """Asynchronous wrapper for text translation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            functools.partial(self.translate_text, text)
        )
    
    def translate_equipment(self, equipment_data: Dict) -> Dict:
        """Translate equipment/loadout information"""
        translated = {}
        
        for key, value in equipment_data.items():
            # Translate key
            translated_key = self.translate_text(key)
            
            # Translate value if it's a string
            if isinstance(value, str):
                translated_value = self.translate_text(value)
            else:
                translated_value = value
            
            translated[translated_key] = translated_value
        
        return translated
    
    def get_weapon_translation(self, weapon_name: str) -> str:
        """Get English translation for weapon names"""
        weapon_translations = {
            'смоки': 'smoky',
            'рикошет': 'ricochet', 
            'молот': 'hammer',
            'гром': 'thunder',
            'шафт': 'shaft',
            'твинс': 'twins',
            'фриз': 'freeze',
            'изида': 'isida'
        }
        
        normalized = weapon_name.lower().strip()
        return weapon_translations.get(normalized, weapon_name).title()
    
    def get_hull_translation(self, hull_name: str) -> str:
        """Get English translation for hull names"""
        hull_translations = {
            'хантер': 'hunter',
            'васп': 'wasp',
            'викинг': 'viking',
            'диктатор': 'dictator',
            'хорнет': 'hornet'
        }
        
        normalized = hull_name.lower().strip()
        return hull_translations.get(normalized, hull_name).title()
