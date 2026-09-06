import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time
import random
import os
from pathlib import Path

class GoogleSoundHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.base_dir = Path("C:/google_sounds")
        self.base_dir.mkdir(exist_ok=True)
        
    def google_search(self, query):
        """Гуглит запрос и возвращает ссылки"""
        print(f"🔍 Гуглю: {query}")
        
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            response = self.session.get(url)
            
            # Ищем все ссылки в результатах
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href.startswith('/url?q='):
                    # Вытаскиваем настоящий URL
                    real_url = href.split('/url?q=')[1].split('&')[0]
                    links.append(urllib.parse.unquote(real_url))
            
            return links
            
        except Exception as e:
            print(f"❌ Гугл сломался: {e}")
            return []
    
    def extract_mp3_links(self, url):
        """Заходит на сайт и ищет MP3 ссылки"""
        try:
            print(f"🎯 Ищу MP3 на: {url}")
            response = self.session.get(url, timeout=10)
            
            # Ищем все MP3 ссылки в коде страницы
            mp3_links = re.findall(r'https?://[^\s"\']+\.mp3', response.text)
            
            # Также ищем в href ссылках
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.mp3'):
                    if href.startswith('http'):
                        mp3_links.append(href)
                    else:
                        # Относительная ссылка - делаем абсолютной
                        base_url = '/'.join(url.split('/')[:3])
                        mp3_links.append(base_url + href)
            
            return list(set(mp3_links))  # Убираем дубли
            
        except Exception as e:
            print(f"❌ Не удалось спарсить {url}: {e}")
            return []
    
    def download_mp3(self, mp3_url, source):
        """Качает MP3 файл"""
        try:
            filename = f"{source}_{int(time.time())}.mp3"
            filepath = self.base_dir / filename
            
            print(f"⬇️ Качаю: {mp3_url}")
            
            response = self.session.get(mp3_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Проверяем что файл не пустой
                if os.path.getsize(filepath) > 1000:  # больше 1KB
                    print(f"✅ Скачан: {filename}")
                    return True
                else:
                    os.remove(filepath)
                    print(f"🗑️ Файл пустой")
                    return False
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False
    
    def hunt_sounds(self):
        """Главная функция охоты"""
        print("🚀 ЗАПУСКАЮ АВТОМАТИЧЕСКУЮ ОХОТУ!")
        print("⚡ Гуглю, ищу MP3, качаю...")
        
        # Запросы для поиска
        search_queries = [
            'car engine sound mp3',
            'engine noise mp3 download', 
            'motor sound effect mp3',
            'автомобиль звук двигателя mp3',
            'звук мотора машины mp3',
            'car acceleration sound mp3',
            'engine start sound mp3',
            'vehicle sounds mp3'
        ]
        
        total_downloaded = 0
        
        for query in search_queries:
            print(f"\n🎯 Поисковый запрос: {query}")
            print("-" * 50)
            
            # Гуглим запрос
            search_results = self.google_search(query)
            
            for result_url in search_results[:5]:  # Первые 5 результатов
                # Пропускаем рекламу и всякую хуйню
                if any(bad in result_url for bad in ['google.com', 'youtube.com', 'facebook.com']):
                    continue
                
                # Ищем MP3 на странице
                mp3_links = self.extract_mp3_links(result_url)
                
                for mp3_url in mp3_links[:3]:  # Первые 3 MP3
                    if self.download_mp3(mp3_url, "google"):
                        total_downloaded += 1
                    
                    # Пауза чтобы не забанили
                    time.sleep(random.uniform(2, 4))
            
            # Пауза между запросами
            time.sleep(random.uniform(3, 6))
        
        print(f"\n🎉 ОХОТА ЗАВЕРШЕНА!")
        print(f"📥 Скачано файлов: {total_downloaded}")
        print(f"📁 Папка: {self.base_dir}")

# 🚀 ЗАПУСК
if __name__ == "__main__":
    hunter = GoogleSoundHunter()
    
    print("🔥 GOOGLE MP3 HUNTER")
    print("💡 Парсер сам гуглит, сам находит MP3, сам качает!")
    print("⚠️  Это займет 15-30 минут...")
    
    input("Нажми Enter чтобы начать...")
    
    hunter.hunt_sounds()