"""
Конфигурация приложения
"""
import os
from pathlib import Path

# Пути к файлам
BASE_DIR = Path(__file__).parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
DATA_DIR = BASE_DIR / "data"

# Создаем директории если их нет
TEMP_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Настройки изображений
IMAGE_SIZE = (149, 149)
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']

# Настройки API
IMGUR_CLIENT_IDS = [
    '546c25a59c58ad7',
    '546c25a59c58ad8', 
    '546c25a59c58ad9'
]

# Настройки прокси
PROXY_FILE = BASE_DIR / "proxylist.txt"
DEFAULT_PROXY_TIMEOUT = 30

# Настройки UI
WINDOW_SIZE = (800, 250)
TAB_NAMES = {
    'proxy': 'Прокси',
    'product': 'Добавить товар'
}

# Категории товаров
PRODUCT_CATEGORIES = [
    'Разделы',
    'Брюки',
    'Верхняя одежда', 
    'Свитеры и толстовки',
    'Футболки и рубашки',
    'Сумки',
    'Аксессуары',
    'Обувь',
    'Нижнее белье'
]

# Настройки загрузки
DOWNLOAD_DELAY = 0.1  # секунды между загрузками
MAX_RETRIES = 3 