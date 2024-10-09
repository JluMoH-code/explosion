from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
from DisplayUtils import DisplayUtils
from ReferencePointsManager import ReferencePointsManager
from ReferencePointsSelector import AutoPointsSelector, TemplateMatchingSelector
from CoordinateConverter import CoordinateConverter
from Point import Point

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.points = []
        self.image = None
        self.scale_factor = 1
        self.selection_radius = 10
        self.ref_points_manager = ReferencePointsManager()
        self.converter = CoordinateConverter()
        self.target_point = None
        
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
        self.right_layout = QVBoxLayout()
        self.right_layout.addStretch()

        # Кнопка для загрузки изображения
        self.load_image_btn = QPushButton("Загрузить изображение", self)
        self.load_image_btn.clicked.connect(self.load_image)
        self.right_layout.addWidget(self.load_image_btn, alignment=Qt.AlignCenter)
        
        # Подпись для комбобокса
        self.method_label = QLabel("Метод выделения точек:", self)
        self.method_label.setAlignment(Qt.AlignCenter)
        self.right_layout.addWidget(self.method_label, alignment=Qt.AlignCenter)

        # Выпадающий список для выбора метода
        self.method_selector = QComboBox(self)
        self.method_selector.addItems(["Manual", "Template Matching"])
        self.right_layout.addWidget(self.method_selector, alignment=Qt.AlignCenter)

        # Кнопка для выбора точки
        self.select_point_btn = QPushButton("Выбрать опорные точки", self)
        self.select_point_btn.clicked.connect(self.select_points)
        self.right_layout.addWidget(self.select_point_btn, alignment=Qt.AlignCenter)
        
        self.points_count_label = QLabel(self)
        self.points_count_label.setText("Введено опорных точек: 0")
        self.right_layout.addWidget(self.points_count_label)
        
        # Кнопка для выбора искомой точки
        self.select_target_point_btn = QPushButton("Выбрать искомую точку", self)
        self.select_target_point_btn.clicked.connect(self.select_target_point)
        self.right_layout.addWidget(self.select_target_point_btn, alignment=Qt.AlignCenter)
        
        self.right_layout.addStretch()

        # Добавляем элементы в основной layout
        main_layout.addWidget(self.image_label, 2)
        main_layout.addLayout(self.right_layout, 1)

    def update_points_count(self):
        """
        Обновляет текст в QLabel с количеством введённых точек.
        """
        points_count = len(self.points)
        self.points_count_label.setText(f"Введено опорных точек: {points_count}")

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

    def end_select_points(self):
        """
        Логика для завершения выбора точек.
        """
        self.image_label.mousePressEvent = None
        
        if hasattr(self, 'finish_select_btn'):
            self.right_layout.removeWidget(self.finish_select_btn)
            self.finish_select_btn.deleteLater()  # Удаляем кнопку из интерфейса
            del self.finish_select_btn  # Удаляем атрибут из класса

    def select_points(self):
        """
        Логика для выбора точек.
        """
        method = self.method_selector.currentText()
        
        if self.image is not None:
            if method == "Manual":
                self.image_label.mousePressEvent = self.mouse_click
                
                # Создаём кнопку "Завершить выбор точек" (если она еще не была создана)
                if not hasattr(self, 'finish_select_btn'):
                    self.finish_select_btn = QPushButton("Завершить выбор точек", self)
                    self.finish_select_btn.clicked.connect(self.end_select_points)
                    self.right_layout.addWidget(self.finish_select_btn, alignment=Qt.AlignCenter)              
            elif method == "Auto":
                self.ref_points_manager.set_selector(AutoPointsSelector)
                self.ref_points_manager.select_point(self.image)
            elif method == "Template Matching":
                self.ref_points_manager.set_selector(TemplateMatchingSelector)
                
                # Добавить окошко выбора шаблона
                
                self.ref_points_manager.select_point(self.image, template)
                
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
        
        # Проверка, находится ли клик в пределах существующих точек
        nearest_point = self.find_nearest_point(x_original, y_original)
        if nearest_point:
            updated_point = DisplayUtils.open_coords_input_window(nearest_point, update=True)
            if updated_point:
                index = self.points.index(nearest_point)
                self.points[index] = updated_point
                self.draw_points()
                self.update_points_count()
            else:
                self.points.remove(nearest_point)  
                self.draw_points() 
                self.update_points_count()
            return

        # Открываем окно для ввода глобальных координат (локальные координаты передаются)
        point = Point(local_coords=(x_original, y_original))
        point = DisplayUtils.open_coords_input_window(point)
        
        if point:
            self.points.append(point)
            self.draw_points()
            self.update_points_count()
         
    def find_nearest_point(self, x, y):
        """
        Находит ближайшую точку к заданным координатам в пределах радиуса.
        """
        for point in self.points:
            px, py = point.local_coords
            # Проверка расстояния
            if ((px - x) ** 2 + (py - y) ** 2) <= ((self.selection_radius / self.scale_factor) ** 2):
                return point
        return None
                
    def select_target_point(self):
        """
        Логика для выбора искомой точки.
        """
        self.image_label.mousePressEvent = self.mouse_click_target_point
            
    def mouse_click_target_point(self, event):
        """
        Обработка клика на изображении для выбора искомой точки.
        Открывает окно для с локальными и глобальными координатами.
        """
        
        if self.image is None:
            return
        
        x_scaled = event.pos().x()
        y_scaled = event.pos().y()

        # Пересчитываем координаты обратно на оригинальные
        x_original = int(x_scaled / self.scale_factor)
        y_original = int(y_scaled / self.scale_factor)
        
        target_point = Point(local_coords=(x_original, y_original)) 
        
        try:     
            target_point = CoordinateConverter.convert_to_global(self.points, target_point)  
            # Открываем окно для отображение координат
            point = DisplayUtils.open_coords_input_window(target_point)
        except ValueError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(str(e))
            msg.setWindowTitle("Ошибка")
            
            high_precision_btn = msg.addButton("Всё равно считать", QMessageBox.ActionRole)
            adding_points_btn = msg.addButton("Добавить точки", QMessageBox.ActionRole)

            msg.exec_() 
            if msg.clickedButton() == high_precision_btn:
                try:
                    target_point = CoordinateConverter.simple_linear_transformation(self.points, target_point)  
                    # Открываем окно для отображение координат
                    point = DisplayUtils.open_coords_input_window(target_point)
                except ValueError as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(str(e))
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()   
            elif msg.clickedButton() == adding_points_btn:
                self.select_points()
            
    @staticmethod
    def run():
        """
        Метод для инкапсуляции запуска приложения.
        """
        app = QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()