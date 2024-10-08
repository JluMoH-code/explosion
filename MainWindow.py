from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QComboBox, QVBoxLayout, QHBoxLayout, QWidget)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
from DisplayUtils import DisplayUtils

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.points = []
        self.image = None
        self.scale_factor = 1
        
        self.setWindowTitle("Выбор реперных точек")

        # Главное окно будет содержать центральный виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Основной layout для всего окна
        main_layout = QHBoxLayout(central_widget)

        # Левая часть - отображение изображения
        self.image_label = QLabel(self)
        self.image_label.setText("Выберите изображение или видео")
        self.image_label.setAlignment(Qt.AlignCenter)

        # Правая часть - элементы управления
        right_layout = QVBoxLayout()
        right_layout.addStretch()

        # Кнопка для загрузки изображения
        self.load_image_btn = QPushButton("Загрузить изображение", self)
        self.load_image_btn.clicked.connect(self.load_image)
        right_layout.addWidget(self.load_image_btn, alignment=Qt.AlignCenter)
        
        # Подпись для комбобокса
        self.method_label = QLabel("Метод выделения точек:", self)
        self.method_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.method_label, alignment=Qt.AlignCenter)

        # Выпадающий список для выбора метода
        self.method_selector = QComboBox(self)
        self.method_selector.addItems(["Manual", "Template Matching"])
        right_layout.addWidget(self.method_selector, alignment=Qt.AlignCenter)

        # Кнопка для выбора точки
        self.select_point_btn = QPushButton("Выбрать точки", self)
        self.select_point_btn.clicked.connect(self.select_points)
        right_layout.addWidget(self.select_point_btn, alignment=Qt.AlignCenter)
        
        right_layout.addStretch()

        # Добавляем элементы в основной layout
        main_layout.addWidget(self.image_label, 2)
        main_layout.addLayout(right_layout, 1)

    def load_image(self):
        """
        Загрузка изображения через QFileDialog.
        """
        file_name = DisplayUtils.open_image_file()
        if file_name:
            self.image = cv2.imread(file_name)
            self.display_image(self.image)

    def draw_points(self):
        """
        Метод для отображения всех реперных точек на изображении.
        """
        if self.image is None:
            return
        
        display_image = self.image.copy()
        print(self.points)

        for point in self.points:
            x, y = point.local_coords
            cv2.circle(display_image, (x, y), radius=int(5 / self.scale_factor), color=(0, 0, 255), thickness=-1)  # Красная точка

        self.display_image(display_image)  # Обновляем QLabel

    def display_image(self, image):
        """
        Отображение изображения в QLabel с уменьшением до 1280x720, если изображение больше.
        """
        max_width = 1280
        max_height = 720

        # Получаем размеры изображения
        original_height, original_width, _ = image.shape

        # Пропорциональное масштабирование
        if original_width > max_width or original_height > max_height:
            # Рассчитываем коэффициент масштабирования
            self.scale_factor = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * self.scale_factor)
            new_height = int(original_height * self.scale_factor)
        else:
            # Если изображение меньше или равно, сохраняем его размеры и масштабирование 1:1
            new_width, new_height = original_width, original_height
            self.scale_factor = 1.0

        # Преобразуем изображение OpenCV в формат QImage
        bytes_per_line = 3 * original_width
        q_img = QImage(image.data, original_width, original_height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Создаём QPixmap и масштабируем его до новых размеров
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)

        # Отображаем изображение в QLabel
        self.image_label.setPixmap(scaled_pixmap)

    def select_points(self):
        """
        Логика для выбора точек.
        """
        method = self.method_selector.currentText()
        
        if self.image is not None:
            if method == "Manual":
                self.image_label.mousePressEvent = self.mouse_click
            
    def mouse_click(self, event):
        """
        Обработка клика на изображении для выбора точки.
        Открывает окно для ввода глобальных координат и отображает точку.
        """
        x_scaled = event.pos().x()
        y_scaled = event.pos().y()

        # Пересчитываем координаты обратно на оригинальные
        x_original = int(x_scaled / self.scale_factor)
        y_original = int(y_scaled / self.scale_factor)

        # Открываем окно для ввода глобальных координат (локальные координаты передаются)
        point = DisplayUtils.open_coords_input_window(local_coords=(x_original, y_original))
        if point:
            self.points.append(point)
            self.draw_points()
            
    @staticmethod
    def run():
        """
        Метод для инкапсуляции запуска приложения.
        """
        app = QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()