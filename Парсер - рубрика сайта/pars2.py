import os
from bs4 import BeautifulSoup
import requests
import time

class HtmlLinkParser:
    def __init__(self):
        self.input_file = "C:/Users/Mi/Desktop/Парсер - рубрика сайта (ПЕРЕПИСАТЬ)/saved_resource.html"
        self.links_file = "C:/Users/Mi/Desktop/Парсер - рубрика сайта (ПЕРЕПИСАТЬ)/site_links.txt"
        self.content_file = "C:/Users/Mi/Desktop/Парсер - рубрика сайта (ПЕРЕПИСАТЬ)/sites_content.txt"
        
    def extract_links_from_html(self):
        """Парсит HTML файл и находит все ссылки возле 'Перейти на сайт'"""
        if not os.path.exists(self.input_file):
            print(f"❌ Файл {self.input_file} не найден!")
            return []
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            # Ищем все элементы с текстом "Перейти на сайт"
            site_buttons = soup.find_all(string=lambda text: text and 'перейти на сайт' in text.lower())
            
            for button in site_buttons:
                # Ищем ближайшую ссыску (родительский <a> или соседний элемент)
                link_element = button.find_parent('a')
                if link_element and link_element.get('href'):
                    href = link_element.get('href')
                    links.append({
                        'url': href,
                        'button_text': button.strip(),
                        'element': str(link_element)[:100] + '...'  # для отладки
                    })
                    continue
                
                # Если не нашли родительскую ссылку, ищем соседнюю
                parent = button.parent
                if parent:
                    # Ищем ссылку в том же блоке
                    nearby_links = parent.find_all('a')
                    for link in nearby_links:
                        if link.get('href'):
                            links.append({
                                'url': link.get('href'),
                                'button_text': button.strip(),
                                'element': str(link)[:100] + '...'
                            })
                            break
            
            # Альтернативный поиск: ищем по классам кнопок
            if not links:
                button_elements = soup.find_all(['a', 'button'], class_=lambda x: x and any(word in str(x).lower() for word in ['button', 'btn', 'site', 'link']))
                for element in button_elements:
                    if element.get('href') and any(word in element.get_text().lower() for word in ['перейти', 'сайт', 'visit', 'go']):
                        links.append({
                            'url': element.get('href'),
                            'button_text': element.get_text(strip=True),
                            'element': str(element)[:100] + '...'
                        })
            
            print(f"✅ Найдено ссылок: {len(links)}")
            return links
            
        except Exception as e:
            print(f"❌ Ошибка парсинга HTML: {e}")
            return []
    
    def save_links_to_file(self, links):
        """Сохраняет найденные ссылки в файл"""
        with open(self.links_file, 'w', encoding='utf-8') as f:
            f.write("СПИСОК ССЫЛОК ИЗ HTML:\n")
            f.write("=" * 50 + "\n\n")
            
            for i, link in enumerate(links, 1):
                f.write(f"{i}. {link['url']}\n")
                f.write(f"   Текст кнопки: {link['button_text']}\n")
                f.write(f"   Элемент: {link['element']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"💾 Ссылки сохранены в {self.links_file}")
    
    def visit_sites_and_save_content(self, links):
        """Переходит по всем ссылкам и сохраняет контент"""
        if not links:
            print("❌ Нет ссылок для обработки")
            return
        
        print("🌐 Начинаю обход сайтов...")
        
        with open(self.content_file, 'w', encoding='utf-8') as f:
            f.write("КОНТЕНТ САЙТОВ:\n")
            f.write("=" * 50 + "\n\n")
            
            for i, link in enumerate(links, 1):
                try:
                    print(f"📡 Перехожу на сайт {i}/{len(links)}: {link['url']}")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(link['url'], headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    # Парсим контент
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Удаляем скрипты и стили
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Получаем чистый текст
                    text_content = soup.get_text()
                    clean_text = ' '.join(text_content.split()[:200])  # Первые 200 слов
                    
                    # Сохраняем в файл
                    f.write(f"САЙТ {i}: {link['url']}\n")
                    f.write(f"Кнопка: {link['button_text']}\n")
                    f.write(f"Контент: {clean_text}...\n")
                    f.write("=" * 50 + "\n\n")
                    
                    print(f"✅ Сайт {i} сохранен")
                    
                    # Пауза между запросами
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Ошибка при обработке {link['url']}: {e}")
                    f.write(f"САЙТ {i}: {link['url']}\n")
                    f.write(f"ОШИБКА: {e}\n")
                    f.write("=" * 50 + "\n\n")
    
    def run(self):
        """Запускает весь процесс"""
        print("=" * 50)
        print("🕷️  ПАРСЕР САЙТОВ ИЗ HTML")
        print("=" * 50)
        
        # Шаг 1: Парсим HTML и находим ссылки
        print("🔍 Парсим zalupa.html...")
        links = self.extract_links_from_html()
        
        if not links:
            print("❌ Не найдено ссылок 'Перейти на сайт'")
            return
        
        # Шаг 2: Сохраняем ссылки в файл
        self.save_links_to_file(links)
        
        # Шаг 3: Переходим по ссылкам и сохраняем контент
        self.visit_sites_and_save_content(links)
        
        print("=" * 50)
        print("✅ ВСЁ ЗАВЕРШЕНО!")
        print(f"📄 Ссылки: {self.links_file}")
        print(f"📄 Контент: {self.content_file}")
        print("=" * 50)

# Запуск программы
if __name__ == "__main__":
    try:
        parser = HtmlLinkParser()
        parser.run()
    except Exception as e:
        print(f"💥 Ошибка: {e}")