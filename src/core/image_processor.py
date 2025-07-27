"""
Модуль для обработки изображений
"""
import os
import time
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import cloudscraper
import requests
import io

from ..config.settings import IMAGE_SIZE, SUPPORTED_FORMATS, DEFAULT_PROXY_TIMEOUT
from .exceptions import ImageDownloadError


class ImageProcessor:
    """Класс для обработки и загрузки изображений"""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.scraper = self._create_scraper()
        
    def _create_scraper(self) -> cloudscraper.CloudScraper:
        """Создает настроенный scraper"""
        return cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False
            }
        )
    
    def _get_headers(self) -> dict:
        """Возвращает заголовки для запросов"""
        return {
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
    
    def download_image(self, url: str, index: int) -> Optional[str]:
        """
        Загружает изображение по URL
        
        Args:
            url: URL изображения
            index: Индекс изображения для именования файла
            
        Returns:
            Путь к сохраненному файлу или None при ошибке
        """
        if not url or url.strip() == "":
            raise ImageDownloadError("Получен пустой URL")
        
        filename = self.temp_dir / f"res_{index}.jpg"
        
        # Пробуем cloudscraper
        try:
            return self._download_with_scraper(url, filename)
        except Exception as e:
            print(f"Ошибка cloudscraper: {e}")
            
            # Пробуем обычный requests
            try:
                return self._download_with_requests(url, filename)
            except Exception as e2:
                print(f"Ошибка requests: {e2}")
                return None
    
    def _download_with_scraper(self, url: str, filename: Path) -> str:
        """Загрузка через cloudscraper"""
        print(f"Загружаем изображение через cloudscraper: {url}")
        
        response = self.scraper.get(url, headers=self._get_headers(), timeout=DEFAULT_PROXY_TIMEOUT)
        
        if response.status_code != 200:
            raise ImageDownloadError(f"Ошибка cloudscraper: статус {response.status_code}")
        
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise ImageDownloadError(f"Получен неверный тип контента: {content_type}")
        
        image_data = response.content
        if len(image_data) < 1000:
            raise ImageDownloadError(f"Получены слишком маленькие данные: {len(image_data)} байт")
        
        self._save_image(image_data, filename)
        print(f"Изображение успешно загружено через cloudscraper")
        return str(filename)
    
    def _download_with_requests(self, url: str, filename: Path) -> str:
        """Загрузка через requests"""
        print(f"Пробуем через requests: {url}")
        
        session = requests.Session()
        session.headers.update(self._get_headers())
        
        response = session.get(url, timeout=DEFAULT_PROXY_TIMEOUT)
        
        if response.status_code != 200:
            raise ImageDownloadError(f"Ошибка requests: статус {response.status_code}")
        
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise ImageDownloadError(f"Requests: неверный тип контента: {content_type}")
        
        image_data = response.content
        if len(image_data) < 1000:
            raise ImageDownloadError(f"Requests: слишком маленькие данные: {len(image_data)} байт")
        
        self._save_image(image_data, filename)
        print(f"Изображение успешно загружено через requests")
        return str(filename)
    
    def _save_image(self, image_data: bytes, filename: Path) -> None:
        """Сохраняет изображение в файл"""
        pil_image = Image.open(io.BytesIO(image_data))
        rgb_image = pil_image.convert("RGB")
        rgb_image.save(filename)
    
    def cleanup_temp_files(self) -> None:
        """Очищает временные файлы"""
        for file_path in self.temp_dir.glob("res_*.jpg"):
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Ошибка удаления файла {file_path}: {e}")
    
    def get_image_count(self) -> int:
        """Возвращает количество временных файлов"""
        return len(list(self.temp_dir.glob("res_*.jpg"))) 