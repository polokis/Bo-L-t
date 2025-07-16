import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import re
from typing import Dict, List, Optional
import trafilatura

logger = logging.getLogger(__name__)

class RTanksPlayerScraper:
    """Scraper for RTanks Online player statistics and leaderboards"""
    
    def __init__(self):
        self.base_url = "https://ratings.ranked-rtanks.online"
        self.session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
        return self.session
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page and return its content"""
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"HTTP {response.status} when fetching {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _extract_rank_from_image(self, img_src: str) -> str:
        """Extract rank name from image URL"""
        # Image URLs are like: https://i.imgur.com/a3UCeT5.png
        # We need to map these to rank names based on the pattern seen in the data
        rank_mappings = {
            'a3UCeT5.png': 'Warrant Officer 5',  # Уорэнт-офицер 5
            'O6Tb9li.png': 'Colonel',             # Полковник
            'rCN2gJm.png': 'Lieutenant Colonel',  # Подполковник
            'R69LmLt.png': 'Major',               # Майор
            'Ljy2jDX.png': 'Captain',             # Капитан
            'lTXxLVJ.png': 'First Lieutenant',    # Первый лейтенант
            'iTyjOt3.png': 'Second Lieutenant',   # Второй лейтенант
            'BIr8vRX.png': 'Warrant Officer 4',  # Уорэнт-офицер 4
            'sppjRis.png': 'Warrant Officer 3',  # Уорэнт-офицер 3
            'LATOpxZ.png': 'Warrant Officer 2',  # Уорэнт-офицер 2
            'ekbJYyf.png': 'Warrant Officer 1',  # Уорэнт-офицер 1
            'GzJRzgz.png': 'Master Sergeant',    # Мастер-сержант
            'pxzNyxi.png': 'Sergeant First Class', # Старший сержант
            'UWup9qJ.png': 'Staff Sergeant',     # Штаб-сержант
            'dSE90bT.png': 'Sergeant',           # Сержант
            'paF1myt.png': 'Corporal',           # Капрал
            'wPZnaG0.png': 'Lance Corporal',     # Младший капрал
            'Or6Ajto.png': 'Private First Class', # Рядовой первого класса
            'AYAs02w.png': 'Private',            # Рядовой
            'M4GBQIq.png': 'Recruit',            # Новобранец
            'Q2YgFQ1.png': 'Legend',             # Легенда
            'rO3Hs5f.png': 'Generalissimo',      # Генералиссимус
            'OQEHkm7.png': 'General',            # Генерал
            'BNZpCPo.png': 'Lieutenant General', # Генерал-лейтенант
            'eQXJOZE.png': 'Major General',      # Генерал-майор
            'Sluzy': 'Brigadier General'         # Бригадный генерал
        }
        
        # Extract filename from URL
        if 'imgur.com' in img_src:
            filename = img_src.split('/')[-1]
            return rank_mappings.get(filename, 'Unknown Rank')
        
        return 'Unknown Rank'
    
    async def get_player_stats(self, nickname: str) -> Optional[Dict]:
        """Get player statistics by nickname"""
        try:
            # Construct player profile URL
            player_url = f"{self.base_url}/user/{nickname}"
            
            # Fetch player page
            html_content = await self._fetch_page(player_url)
            if not html_content:
                return None
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract player data
            player_data = {
                'nickname': nickname,
                'rank': 'Unknown',
                'experience': 0,
                'kills': 0,
                'deaths': 0,
                'kd_ratio': 0.0,
                'premium': False,
                'goldboxes': 0,
                'crystals_rank': 'N/A',
                'efficiency_rank': 'N/A',
                'experience_rank': 'N/A',
                'kills_rank': 'N/A',
                'equipment': ''
            }
            
            # Extract rank from image or text
            rank_img = soup.find('img', src=re.compile(r'imgur\.com'))
            if rank_img:
                player_data['rank'] = self._extract_rank_from_image(rank_img['src'])
            
            # Always try to extract rank from text since image method may not work
            # Look for any font element with gray color (more flexible approach)
            gray_fonts = soup.find_all('font', attrs={'style': lambda x: x and 'gray' in x.lower()})
            for font in gray_fonts:
                rank_text = font.get_text(strip=True)
                if rank_text and 2 < len(rank_text) < 30:  # Reasonable rank name length
                    player_data['rank'] = rank_text
                    break
            
            # Extract experience from XP bar and table
            exp_found = False
            
            # Method 1: Extract from XP progress bar (.text_xp class)
            xp_element = soup.find('div', class_='text_xp')
            if xp_element:
                xp_text = xp_element.get_text(strip=True)
                # Extract the first number from "2 106 / 3 700" format
                exp_match = re.search(r'(\d{1,3}(?:\s\d{3})*)', xp_text)
                if exp_match:
                    player_data['experience'] = int(exp_match.group(1).replace(' ', ''))
                    exp_found = True
            
            # Method 2: Look for "По опыту" (By experience) in ratings table
            if not exp_found:
                for table in soup.find_all('table'):
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:  # Need 3 columns: category, rank, value
                            category = cells[0].get_text(strip=True).lower()
                            value = cells[2].get_text(strip=True)
                            
                            if 'по опыту' in category or 'опыт' in category:
                                # Extract number from experience value
                                exp_match = re.search(r'(\d{1,3}(?:\s\d{3})*)', value)
                                if exp_match:
                                    player_data['experience'] = int(exp_match.group(1).replace(' ', ''))
                                    exp_found = True
                                    break
                    if exp_found:
                        break
            
            # Extract kills, deaths, and K/D ratio from tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'уничтожил' in key or 'kills' in key:
                            player_data['kills'] = int(re.sub(r'[^\d]', '', value) or 0)
                        elif 'подбит' in key or 'deaths' in key:
                            player_data['deaths'] = int(re.sub(r'[^\d]', '', value) or 0)
                        elif 'у/п' in key or 'k/d' in key or 'эффективность' in key:
                            try:
                                player_data['kd_ratio'] = float(value.replace(',', '.'))
                            except:
                                pass
                        elif 'премиум' in key or 'premium' in key:
                            player_data['premium'] = 'да' in value.lower() or 'yes' in value.lower()
                        elif 'золот' in key or 'gold' in key:
                            player_data['goldboxes'] = int(re.sub(r'[^\d]', '', value) or 0)
            
            # Extract ranking positions from ratings table
            # Find the table with "Места в текущих рейтингах" (Current rankings)
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:  # category, rank, value
                        category = cells[0].get_text(strip=True).lower()
                        rank = cells[1].get_text(strip=True).replace('#', '')
                        
                        if 'по опыту' in category:
                            player_data['experience_rank'] = rank if rank != '0' else 'N/A'
                        elif 'голдоловов' in category or 'золот' in category:
                            # This is goldboxes, we can skip rank but get the value
                            pass
                        elif 'по киллам' in category:
                            player_data['kills_rank'] = rank if rank != '0' else 'N/A'
                        elif 'по эффективности' in category:
                            player_data['efficiency_rank'] = rank if rank != '0' else 'N/A'
            
            # Extract current equipment information
            equipment_sections = soup.find_all('div', class_=re.compile(r'equipment|loadout'))
            if equipment_sections:
                equipment_text = ""
                for section in equipment_sections:
                    equipment_text += section.get_text(strip=True) + " "
                player_data['equipment'] = equipment_text.strip()
            
            return player_data
            
        except Exception as e:
            logger.error(f"Error parsing player data for {nickname}: {e}")
            return None
    
    async def get_leaderboard(self, category: str) -> Optional[List[Dict]]:
        """Get leaderboard data for specified category"""
        try:
            # Map category to the appropriate section on the main page
            if category == 'experience':
                # Main page shows experience leaderboard by default
                url = self.base_url
            elif category == 'crystals':
                # Crystal leaderboard is also on main page
                url = self.base_url
            else:
                # For other categories, we'll parse what's available
                url = self.base_url
            
            html_content = await self._fetch_page(url)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find leaderboard tables
            leaderboard_data = []
            
            # Look for the main leaderboard table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        try:
                            # Extract position, player info, and value
                            position = cells[0].get_text(strip=True)
                            
                            # Player cell contains image and name
                            player_cell = cells[1]
                            player_link = player_cell.find('a')
                            if player_link:
                                nickname = player_link.get_text(strip=True)
                                
                                # Extract rank from image
                                rank_img = player_cell.find('img')
                                rank = 'Unknown'
                                if rank_img and 'src' in rank_img.attrs:
                                    rank = self._extract_rank_from_image(rank_img['src'])
                                
                                # Extract value (experience, crystals, etc.)
                                value_text = cells[2].get_text(strip=True)
                                try:
                                    value = int(value_text.replace(' ', '').replace(',', ''))
                                except:
                                    value = value_text
                                
                                leaderboard_data.append({
                                    'position': position,
                                    'nickname': nickname,
                                    'rank': rank,
                                    'value': value
                                })
                        
                        except Exception as e:
                            logger.debug(f"Error parsing leaderboard row: {e}")
                            continue
            
            # Filter by category if needed
            if category == 'crystals':
                # Try to find the crystals section specifically
                crystal_section = soup.find(text=re.compile(r'кристалл'))
                if crystal_section:
                    # Find the table after the crystals header
                    crystal_table = crystal_section.find_parent().find_next('table')
                    if crystal_table:
                        leaderboard_data = []  # Reset and use crystal-specific data
                        rows = crystal_table.find_all('tr')
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                try:
                                    position = cells[0].get_text(strip=True)
                                    player_cell = cells[1]
                                    player_link = player_cell.find('a')
                                    if player_link:
                                        nickname = player_link.get_text(strip=True)
                                        rank_img = player_cell.find('img')
                                        rank = 'Unknown'
                                        if rank_img and 'src' in rank_img.attrs:
                                            rank = self._extract_rank_from_image(rank_img['src'])
                                        
                                        value_text = cells[2].get_text(strip=True)
                                        try:
                                            value = int(value_text.replace(' ', '').replace(',', ''))
                                        except:
                                            value = value_text
                                        
                                        leaderboard_data.append({
                                            'position': position,
                                            'nickname': nickname,
                                            'rank': rank,
                                            'value': value
                                        })
                                except:
                                    continue
            
            return leaderboard_data[:100]  # Return top 100
            
        except Exception as e:
            logger.error(f"Error fetching {category} leaderboard: {e}")
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
