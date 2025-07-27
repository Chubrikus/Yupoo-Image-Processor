"""
Пользовательские исключения приложения
"""

class ImageDownloadError(Exception):
    """Ошибка загрузки изображения"""
    pass

class ProxyError(Exception):
    """Ошибка работы с прокси"""
    pass

class APIError(Exception):
    """Ошибка API"""
    pass

class FileNotFoundError(Exception):
    """Файл не найден"""
    pass

class ValidationError(Exception):
    """Ошибка валидации данных"""
    pass 