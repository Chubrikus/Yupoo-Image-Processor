from PIL import Image
import cloudscraper
import requests
import io


def to_img(url):
    # Проверяем, что URL не пустой
    if not url or url.strip() == "":
        print("Ошибка: получен пустой URL")
        return None
    
    # Создаем scraper с правильными заголовками для Yupoo
    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False
        }
    )
    
    # Добавляем заголовки для обхода защиты
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.yupoo.com/',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    # Сначала пробуем cloudscraper
    try:
        print(f"Загружаем изображение через cloudscraper: {url}")
        response = scraper.get(url, headers=headers, timeout=30)
        
        # Проверяем статус ответа
        if response.status_code != 200:
            print(f"Ошибка cloudscraper: статус {response.status_code}")
            raise Exception("Cloudscraper failed")
            
        # Проверяем, что это действительно изображение
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"Получен неверный тип контента: {content_type}")
            raise Exception("Invalid content type")
            
        jpg_data = response.content
        
        # Проверяем размер данных
        if len(jpg_data) < 1000:  # Меньше 1KB - вероятно не изображение
            print(f"Получены слишком маленькие данные: {len(jpg_data)} байт")
            raise Exception("Data too small")
            
        pil_image = Image.open(io.BytesIO(jpg_data))
        
        # Сохраняем изображение в оригинальном размере
        # Масштабирование будет происходить в интерфейсе
        rgb_im = pil_image.convert("RGB")
        rgb_im.save('res.jpg')
        
        print(f"Изображение успешно загружено через cloudscraper: {pil_image.size}")
        return pil_image
        
    except Exception as e:
        print(f"Ошибка cloudscraper: {e}")
        
        # Пробуем обычный requests как резервный вариант
        try:
            print(f"Пробуем через requests: {url}")
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"Ошибка requests: статус {response.status_code}")
                return None
                
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"Requests: неверный тип контента: {content_type}")
                return None
                
            jpg_data = response.content
            if len(jpg_data) < 1000:
                print(f"Requests: слишком маленькие данные: {len(jpg_data)} байт")
                return None
                
            pil_image = Image.open(io.BytesIO(jpg_data))
            
            # Сохраняем изображение в оригинальном размере
            # Масштабирование будет происходить в интерфейсе
            rgb_im = pil_image.convert("RGB")
            rgb_im.save('res.jpg')
            
            print(f"Изображение успешно загружено через requests: {pil_image.size}")
            return pil_image
            
        except Exception as e2:
            print(f"Ошибка requests: {e2}")
            return None