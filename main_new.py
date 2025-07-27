#!/usr/bin/env python3
"""
Главный модуль приложения
"""
import sys
import time
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

from src.config.settings import *
from src.core import ImageProcessor, ProxyManager
from src.core.exceptions import *

# Импортируем старые модули (пока не переписали их)
import parser
import new_postimg
import table
import get_string


class ImageLoaderThread(QThread):
    """Поток для асинхронной загрузки изображений"""
    image_loaded = pyqtSignal(int, str)  # индекс, путь к файлу
    image_failed = pyqtSignal(int, str)  # индекс, ошибка
    progress_updated = pyqtSignal(int, str)  # прогресс, статус
    
    def __init__(self, urls, image_processor: ImageProcessor):
        super().__init__()
        self.urls = urls
        self.image_processor = image_processor
        self.running = True
        
    def run(self):
        for i, url in enumerate(self.urls):
            if not self.running:
                break
                
            self.progress_updated.emit(
                int((i / len(self.urls)) * 100), 
                f"Загрузка изображения {i+1}/{len(self.urls)}..."
            )
            
            try:
                # Загружаем изображение через новый процессор
                filename = self.image_processor.download_image(url, i)
                if filename:
                    self.image_loaded.emit(i, filename)
                else:
                    self.image_failed.emit(i, "Не удалось загрузить изображение")
            except Exception as e:
                self.image_failed.emit(i, str(e))
                
            # Небольшая задержка между загрузками
            time.sleep(DOWNLOAD_DELAY)
            
        self.progress_updated.emit(100, "Загрузка завершена!")
        
    def stop(self):
        self.running = False


class MainWindow(QtWidgets.QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализируем компоненты
        self.image_processor = ImageProcessor(TEMP_DIR)
        self.proxy_manager = ProxyManager()
        
        # Переменные состояния
        self.image_loader = None
        self.loaded_images = {}
        self.current_image_set = []
        self.host_img = []
        self.f_img = []
        self.inner = 4
        
        # Настройка UI
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Image Processing Application")
        self.setGeometry(0, 0, *WINDOW_SIZE)
        
        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем вкладки
        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.tab_widget.setGeometry(10, 0, 791, 241)
        
        # Вкладка прокси
        self.setup_proxy_tab()
        
        # Вкладка товаров
        self.setup_product_tab()
        
        # Статус бар
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Устанавливаем активную вкладку
        self.tab_widget.setCurrentIndex(1)
        
    def setup_proxy_tab(self):
        """Настройка вкладки прокси"""
        self.proxy_tab = QtWidgets.QWidget()
        
        # Текстовое поле для прокси
        self.proxy_text = QtWidgets.QTextEdit(self.proxy_tab)
        self.proxy_text.setGeometry(3, 30, 521, 181)
        
        # Лейбл
        self.proxy_label = QtWidgets.QLabel(self.proxy_tab)
        self.proxy_label.setGeometry(10, 10, 191, 16)
        self.proxy_label.setText("Введенные прокси:")
        
        self.tab_widget.addTab(self.proxy_tab, TAB_NAMES['proxy'])
        
    def setup_product_tab(self):
        """Настройка вкладки товаров"""
        self.product_tab = QtWidgets.QWidget()
        
        # Область изображений
        self.setup_image_area()
        
        # Панель управления
        self.setup_control_panel()
        
        # Прогресс и статус
        self.setup_progress_area()
        
        self.tab_widget.addTab(self.product_tab, TAB_NAMES['product'])
        
    def setup_image_area(self):
        """Настройка области изображений"""
        # Создаем 4 лейбла для изображений
        self.image_labels = []
        positions = [(10, 10), (170, 10), (330, 10), (490, 10)]
        
        for i, pos in enumerate(positions):
            label = QtWidgets.QLabel(self.product_tab)
            label.setGeometry(pos[0], pos[1], 151, 151)
            label.setStyleSheet("border: 1px solid gray;")
            self.image_labels.append(label)
            
        # Чекбоксы для выбора изображений
        self.image_checkboxes = []
        for i, pos in enumerate(positions):
            checkbox = QtWidgets.QCheckBox(self.product_tab)
            checkbox.setGeometry(pos[0], pos[1] + 150, 70, 17)
            self.image_checkboxes.append(checkbox)
            
    def setup_control_panel(self):
        """Настройка панели управления"""
        # URL поле
        self.url_label = QtWidgets.QLabel(self.product_tab)
        self.url_label.setGeometry(650, 0, 131, 16)
        self.url_label.setText("URL:")
        
        self.url_input = QtWidgets.QTextEdit(self.product_tab)
        self.url_input.setGeometry(650, 20, 131, 31)
        
        # Кнопки
        self.load_button = QtWidgets.QPushButton(self.product_tab)
        self.load_button.setGeometry(700, 70, 75, 23)
        self.load_button.setText("Загрузить")
        
        self.accept_button = QtWidgets.QPushButton(self.product_tab)
        self.accept_button.setGeometry(700, 180, 75, 23)
        self.accept_button.setText("Принять")
        
        # Навигация
        self.back_button = QtWidgets.QPushButton(self.product_tab)
        self.back_button.setGeometry(10, 180, 75, 23)
        self.back_button.setText("Назад")
        
        self.next_button = QtWidgets.QPushButton(self.product_tab)
        self.next_button.setGeometry(100, 180, 75, 23)
        self.next_button.setText("Далее")
        
        # Категории
        self.category_combo = QtWidgets.QComboBox(self.product_tab)
        self.category_combo.setGeometry(650, 40, 131, 21)
        self.category_combo.addItems(PRODUCT_CATEGORIES)
        
        # Выбор файла
        self.file_button = QtWidgets.QPushButton(self.product_tab)
        self.file_button.setGeometry(340, 180, 121, 21)
        self.file_button.setText("Выбрать файл...")
        self.file_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        # Скрытое поле для пути к файлу
        self.file_path_input = QtWidgets.QTextEdit(self.product_tab)
        self.file_path_input.setGeometry(340, 180, 121, 21)
        self.file_path_input.setVisible(False)
        
    def setup_progress_area(self):
        """Настройка области прогресса"""
        # Прогресс бар
        self.progress_bar = QtWidgets.QProgressBar(self.product_tab)
        self.progress_bar.setGeometry(650, 100, 131, 23)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        # Статус
        self.status_label = QtWidgets.QLabel(self.product_tab)
        self.status_label.setGeometry(650, 125, 131, 16)
        self.status_label.setText("Готов к работе")
        
        # Чекбокс прокси
        self.proxy_checkbox = QtWidgets.QCheckBox(self.product_tab)
        self.proxy_checkbox.setGeometry(650, 145, 131, 17)
        self.proxy_checkbox.setText("Использовать прокси")
        self.proxy_checkbox.setChecked(True)
        
    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.load_button.clicked.connect(self.start_processing)
        self.back_button.clicked.connect(self.navigate_back)
        self.next_button.clicked.connect(self.navigate_next)
        self.accept_button.clicked.connect(self.create_table)
        self.file_button.clicked.connect(self.choose_file)
        self.file_button.customContextMenuRequested.connect(self.show_file_context_menu)
        
        # Чекбоксы изображений
        for i, checkbox in enumerate(self.image_checkboxes):
            checkbox.clicked.connect(lambda checked, idx=i: self.choose_image(idx))
            
    def start_processing(self):
        """Начало обработки изображений"""
        url = self.url_input.toPlainText()
        if not url:
            self.update_status("Введите URL!")
            return
            
        # Сохраняем прокси
        proxy_text = self.proxy_text.toPlainText()
        self.proxy_manager.save_proxies(proxy_text.split('\n') if proxy_text else [])
        
        # Сбрасываем состояние
        self.reset_state()
        self.update_progress(0, "Начинаем загрузку...")
        
        try:
            # Парсим изображения
            self.update_progress(10, "Парсинг изображений...")
            self.host_img = parser.img_parser(url)
            
            # Загружаем изображения
            self.update_progress(30, "Загрузка изображений...")
            use_proxy = self.proxy_checkbox.isChecked()
            self.host_img = new_postimg.post_img(self.host_img, use_proxy)
            
            # Инициализируем массив выбора
            self.f_img = [0] * len(self.host_img)
            
            self.update_progress(100, "Готово!")
            self.navigate_next()
            
        except Exception as e:
            self.update_status(f"Ошибка: {str(e)}")
            
    def navigate_next(self):
        """Переход к следующей группе изображений"""
        if len(self.host_img) <= 4:
            return
            
        # Очищаем временные файлы
        self.image_processor.cleanup_temp_files()
        
        self.update_progress(0, "Навигация...")
        
        # Формируем новую группу изображений
        new_images = []
        i = 0
        
        while (self.inner < len(self.host_img)) and (i < 4):
            new_images.append(self.host_img[self.inner])
            
            # Устанавливаем чекбоксы
            if self.f_img[self.inner] != 0:
                self.image_checkboxes[i].setChecked(True)
            else:
                self.image_checkboxes[i].setChecked(False)
                
            self.inner += 1
            i += 1
            
        # Сбрасываем лишние чекбоксы
        for j in range(i, 4):
            self.image_checkboxes[j].setChecked(False)
            
        # Загружаем изображения
        self.load_images_async(new_images)
        
    def navigate_back(self):
        """Переход к предыдущей группе изображений"""
        if len(self.host_img) <= 4 or self.inner == 4:
            return
            
        # Очищаем временные файлы
        self.image_processor.cleanup_temp_files()
        
        self.update_progress(0, "Навигация назад...")
        
        # Вычисляем новую позицию
        if self.inner % 4 == 0:
            self.inner -= 8
        else:
            self.inner = self.inner - ((self.inner % 4) + 4)
            
        # Формируем группу изображений
        new_images = []
        i = 0
        
        while (self.inner >= 0) and (i < 4):
            new_images.append(self.host_img[self.inner])
            
            # Устанавливаем чекбоксы
            if self.f_img[self.inner] != 0:
                self.image_checkboxes[i].setChecked(True)
            else:
                self.image_checkboxes[i].setChecked(False)
                
            self.inner += 1
            i += 1
            
        # Сбрасываем лишние чекбоксы
        for j in range(i, 4):
            self.image_checkboxes[j].setChecked(False)
            
        # Загружаем изображения
        self.load_images_async(new_images)
        
    def load_images_async(self, urls):
        """Асинхронная загрузка изображений"""
        self.current_image_set = urls[:4]
        
        # Очищаем изображения
        for label in self.image_labels:
            label.setPixmap(QtGui.QPixmap())
            
        # Останавливаем предыдущий поток
        if self.image_loader and self.image_loader.isRunning():
            self.image_loader.stop()
            self.image_loader.wait()
            
        # Создаем новый поток
        self.image_loader = ImageLoaderThread(self.current_image_set, self.image_processor)
        
        # Подключаем сигналы
        self.image_loader.image_loaded.connect(self.on_image_loaded)
        self.image_loader.image_failed.connect(self.on_image_failed)
        self.image_loader.progress_updated.connect(self.on_progress_updated)
        
        # Запускаем загрузку
        self.image_loader.start()
        
    def on_image_loaded(self, index, filename):
        """Обработчик успешной загрузки изображения"""
        self.loaded_images[index] = filename
        
        pixmap = QtGui.QPixmap(filename)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(149, 149, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_labels[index].setPixmap(scaled_pixmap)
            
    def on_image_failed(self, index, error):
        """Обработчик ошибки загрузки изображения"""
        placeholder_pixmap = QtGui.QPixmap(149, 149)
        placeholder_pixmap.fill(QtGui.QColor(240, 240, 240))
        
        painter = QtGui.QPainter(placeholder_pixmap)
        painter.setPen(QtGui.QColor(100, 100, 100))
        painter.drawText(placeholder_pixmap.rect(), QtCore.Qt.AlignCenter, "Ошибка\nзагрузки")
        painter.end()
        
        self.image_labels[index].setPixmap(placeholder_pixmap)
        
    def on_progress_updated(self, progress, status):
        """Обработчик обновления прогресса"""
        self.update_progress(progress, status)
        
    def choose_image(self, index):
        """Выбор изображения"""
        if self.inner % 4 != 0:
            while self.inner % 4 != 0:
                self.inner += 1
                
        actual_index = self.inner - 4 + index
        if actual_index >= len(self.f_img):
            self.image_checkboxes[index].setChecked(False)
            return
            
        if self.image_checkboxes[index].isChecked():
            self.f_img[actual_index] = max(self.f_img) + 1
        else:
            self.f_img[actual_index] = 0
            
    def choose_file(self):
        """Выбор файла таблицы"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл таблицы",
            "",
            "Excel файлы (*.xlsx *.xls);;CSV файлы (*.csv);;Все файлы (*.*)"
        )
        
        if file_path:
            self.file_path_input.setPlainText(file_path)
            import os
            filename = os.path.basename(file_path)
            self.file_button.setText(f"📄 {filename}")
            self.update_status(f"Выбран файл: {filename}")
        else:
            self.update_status("Файл не выбран")
            
    def show_file_context_menu(self, position):
        """Контекстное меню для кнопки файла"""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu()
        reset_action = menu.addAction("Сбросить выбор")
        reset_action.triggered.connect(self.reset_file_choice)
        menu.exec_(self.file_button.mapToGlobal(position))
        
    def reset_file_choice(self):
        """Сброс выбранного файла"""
        self.file_path_input.setPlainText("")
        self.file_button.setText("Выбрать файл...")
        self.update_status("Файл сброшен")
        
    def create_table(self):
        """Создание таблицы"""
        table_path = self.file_path_input.toPlainText()
        if not table_path:
            self.update_status("Ошибка: выберите файл таблицы!")
            return
            
        if not Path(table_path).exists():
            self.update_status("Ошибка: файл не найден!")
            return
            
        if len(self.host_img) == 0:
            self.update_status("Ошибка: нет изображений для обработки!")
            return
            
        self.update_status("Создание таблицы...")
        self.update_progress(50, "Создание таблицы...")
        
        try:
            res = get_string.to_string(self.host_img, self.f_img)
            
            if not res:
                self.update_status("Ошибка: нет выбранных изображений!")
                return
                
            mas = [
                None,  # 1
                1,  # 2
                self.category_combo.currentText(),  # 3
                None,  # 4
                None,  # 5
                None,  # 6
                None,  # 7
                None,  # 8
                None,  # 9
                None,  # 10
                None,  # 11
                None,  # 12
                res,  # 13
                self.url_input.toPlainText()  # 14
            ]
            
            table.add_img(mas, table_path)
            self.update_progress(100, "Таблица успешно создана!")
            
        except Exception as e:
            self.update_status(f"Ошибка создания таблицы: {str(e)}")
            
    def reset_state(self):
        """Сброс состояния приложения"""
        self.host_img = []
        self.f_img = []
        self.inner = 4
        
        for checkbox in self.image_checkboxes:
            checkbox.setChecked(False)
            
    def update_progress(self, value, text):
        """Обновление прогресса"""
        self.progress_bar.setValue(value)
        self.status_label.setText(text)
        
    def update_status(self, text):
        """Обновление статуса"""
        self.status_label.setText(text)


def main():
    """Главная функция"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем приложение
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 