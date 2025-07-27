"""
Модуль для работы с прокси
"""
from pathlib import Path
from typing import List, Optional
import requests

from ..config.settings import PROXY_FILE, DEFAULT_PROXY_TIMEOUT
from .exceptions import ProxyError


class ProxyManager:
    """Класс для управления прокси-серверами"""
    
    def __init__(self, proxy_file: Path = None):
        self.proxy_file = proxy_file or PROXY_FILE
        self.proxies = []
        self.current_index = 0
        
    def load_proxies(self) -> List[str]:
        """Загружает список прокси из файла"""
        try:
            if not self.proxy_file.exists():
                return []
                
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                proxies = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Добавляем протокол если его нет
                        if not line.startswith('http'):
                            line = f"http://{line}"
                        proxies.append(line)
                
            self.proxies = proxies
            return proxies
            
        except Exception as e:
            raise ProxyError(f"Ошибка загрузки прокси: {e}")
    
    def save_proxies(self, proxy_list: List[str]) -> None:
        """Сохраняет список прокси в файл"""
        try:
            with open(self.proxy_file, 'w', encoding='utf-8') as f:
                for proxy in proxy_list:
                    f.write(f"{proxy}\n")
            
            self.proxies = proxy_list
            
        except Exception as e:
            raise ProxyError(f"Ошибка сохранения прокси: {e}")
    
    def get_next_proxy(self) -> Optional[str]:
        """Возвращает следующий прокси из списка"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def test_proxy(self, proxy: str) -> bool:
        """Тестирует прокси-сервер"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=DEFAULT_PROXY_TIMEOUT
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def test_all_proxies(self) -> List[str]:
        """Тестирует все прокси и возвращает рабочие"""
        working_proxies = []
        
        for proxy in self.proxies:
            if self.test_proxy(proxy):
                working_proxies.append(proxy)
                print(f"Прокси {proxy} работает")
            else:
                print(f"Прокси {proxy} не работает")
        
        return working_proxies
    
    def get_proxy_dict(self, proxy: str) -> dict:
        """Возвращает словарь прокси для requests"""
        return {
            'http': proxy,
            'https': proxy
        }
    
    def reset_index(self) -> None:
        """Сбрасывает индекс текущего прокси"""
        self.current_index = 0
    
    def get_proxy_count(self) -> int:
        """Возвращает количество прокси"""
        return len(self.proxies)
    
    def is_empty(self) -> bool:
        """Проверяет, пуст ли список прокси"""
        return len(self.proxies) == 0 