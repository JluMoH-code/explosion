from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from Point import Point
import os
import json
from datetime import datetime
import numpy as np

class AnalyticsWindow(QDialog):
    def __init__(self, ref_points, target_point):
        super().__init__()
        self.setWindowTitle("Аналитика")
        self.ref_points = ref_points
        self.target_point = target_point
        self.ref_target_point = Point(self.target_point.local_coords)
        self.width_pixel = self.calculate_width_pixel()
        self.deviation = 0

        self.pixel_length_label = QLabel("Длина одного пикселя:", self)
        self.pixel_length_input = QLineEdit(self)
        self.pixel_length_input.setText(f"{self.width_pixel:.4f}")
        self.pixel_length_input.setDisabled(True)

        self.local_input = QLabel("Локальные координаты", self)

        # Поля для отображения локальных координат (заблокированные)
        self.local_x_input = QLineEdit(self)
        self.local_x_input.setText(str(self.target_point.local_coords[0]))
        self.local_x_input.setDisabled(True)  # Заблокировано для изменения

        self.local_y_input = QLineEdit(self)
        self.local_y_input.setText(str(self.target_point.local_coords[1]))
        self.local_y_input.setDisabled(True)  # Заблокировано для изменения

        self.global_input = QLabel("Посчитанные координаты", self)
        
        # Поля для отображения глобальных координат (заблокированные)
        self.coord_x_input = QLineEdit(self)
        self.coord_x_input.setText(str(self.target_point.global_coords[0]))
        self.coord_x_input.setDisabled(True)  # Заблокировано для изменения

        self.coord_y_input = QLineEdit(self)
        self.coord_y_input.setText(str(self.target_point.global_coords[1]))
        self.coord_y_input.setDisabled(True)  # Заблокировано для изменения

        self.global_ref_input = QLabel("Известные координаты", self)
        
        # Поля для ввода известных глобальных координат
        self.coord_ref_x_input = QLineEdit(self)
        self.coord_ref_x_input.setPlaceholderText("Известная координата X")
        self.coord_ref_x_input.textChanged.connect(lambda: self.reset_color(self.coord_x_input))

        self.coord_ref_y_input = QLineEdit(self)
        self.coord_ref_y_input.setPlaceholderText("Известная координата Y")
        self.coord_ref_y_input.textChanged.connect(lambda: self.reset_color(self.coord_y_input))

        self.analys_point_btn = QPushButton("Анализировать", self)
        self.analys_point_btn.clicked.connect(self.analys)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.pixel_length_label)
        layout.addWidget(self.pixel_length_input)
        layout.addWidget(self.local_input)
        layout.addWidget(self.local_x_input)
        layout.addWidget(self.local_y_input)
        layout.addWidget(self.global_input)
        layout.addWidget(self.coord_x_input)
        layout.addWidget(self.coord_y_input)
        layout.addWidget(self.global_ref_input)
        layout.addWidget(self.coord_ref_x_input)
        layout.addWidget(self.coord_ref_y_input)
        layout.addWidget(self.analys_point_btn)
            
        self.setLayout(layout)

    def accept_coords(self):
        """
        Подтверждение ввода координат (глобальных и локальных).
        """
        x, y = 0, 0
        x_text = self.coord_ref_x_input.text()
        y_text = self.coord_ref_y_input.text()
        has_errors = False
            
        try:
            x = float(self.coord_x_input.text())
        except ValueError:
            self.coord_ref_x_input.setText("")
            self.coord_ref_x_input.setPlaceholderText("Координата должна быть числом!")
            self.coord_ref_x_input.setStyleSheet('color: red')
            has_errors = True
            
        try:
            y = float(self.coord_ref_y_input.text())
        except ValueError:
            self.coord_ref_y_input.setText("")
            self.coord_ref_y_input.setPlaceholderText("Координата должна быть числом!")   
            self.coord_ref_y_input.setStyleSheet('color: red')
            has_errors = True
            
        if x_text == "":
            self.coord_ref_x_input.setPlaceholderText("Глобальная координата X")
            self.coord_ref_x_input.setStyleSheet('color: red')
            has_errors = True
        if y_text == "":
            self.coord_ref_y_input.setPlaceholderText("Глобальная координата Y")
            self.coord_ref_y_input.setStyleSheet('color: red')
            has_errors = True
            
        if not has_errors:
            self.ref_target_point.global_coords = (x, y)
            return True
        return False

    def reset_color(self, input_field):
        """
        Сброс цвета текста в указанном поле ввода.
        """
        input_field.setStyleSheet('color: black')

    def calculate_width_pixel(self):
        ref_local_coords = np.array([point.local_coords for point in self.ref_points])
        ref_global_coords = np.array([point.global_coords for point in self.ref_points])

        local_distances = np.linalg.norm(ref_local_coords[1:] - ref_local_coords[:-1], axis=1)
        global_distances = np.linalg.norm(ref_global_coords[1:] - ref_global_coords[:-1], axis=1)
        pixel_lengths = global_distances / local_distances
        
        return np.mean(pixel_lengths)

    def calculate_deviation(self):
        return np.linalg.norm(self.ref_target_point.global_coords - self.target_point.global_coords)

    def calculate_deviation_to_pixel_ratio(self):
        return self.deviation / self.width_pixel if self.width_pixel != 0 else 0

    def convert_to_standard_types(self, data):
        """
        Рекурсивная функция для преобразования данных типа float32 и других типов в стандартные типы Python.
        """
        if isinstance(data, np.float32):  # Преобразуем float32 в float
            return float(data)
        elif isinstance(data, dict):  # Если это словарь, рекурсивно обрабатываем его значения
            return {key: self.convert_to_standard_types(value) for key, value in data.items()}
        elif isinstance(data, list):  # Если это список, рекурсивно обрабатываем его элементы
            return [self.convert_to_standard_types(item) for item in data]
        return data  # Если это не специальный тип, возвращаем данные как есть

    def save_analys(self):
        data = {
            "target_point": self.ref_target_point.to_dict(),
            "calculate_target_point": self.target_point.to_dict(),
            "deviation": self.deviation,
            "width_pixel": self.width_pixel,
            "deviation_to_pixel_ratio": self.calculate_deviation_to_pixel_ratio(),
            "num_ref_points": len(self.ref_points),
            "ref_points": [point.to_dict() for point in self.ref_points]
        }

        data = self.convert_to_standard_types(data)

        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Сохранение данных в файл JSON
        file_name = f"logs/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

    def analys(self):
        if self.accept_coords():

            self.deviation = self.calculate_deviation()
            deviation_to_pixel_ratio = self.calculate_deviation_to_pixel_ratio()

            deviation_label = QLabel("Отклонение от известных координат:", self)
            deviation_input = QLineEdit(self)
            deviation_input.setText(f"{self.deviation:.4f}")
            deviation_input.setDisabled(True)

            ratio_label = QLabel("Отношение отклонения к длине пикселя:", self)
            ratio_input = QLineEdit(self)
            ratio_input.setText(f"{deviation_to_pixel_ratio:.4f}")
            ratio_input.setDisabled(True)

            save_analytics_point_btn = QPushButton("Сохранить", self)
            save_analytics_point_btn.clicked.connect(self.save_analys)

            # Добавляем поля в layout перед кнопкой анализа
            self.layout().insertWidget(self.layout().indexOf(self.analys_point_btn), deviation_label)
            self.layout().insertWidget(self.layout().indexOf(self.analys_point_btn), deviation_input)
            self.layout().insertWidget(self.layout().indexOf(self.analys_point_btn), ratio_label)
            self.layout().insertWidget(self.layout().indexOf(self.analys_point_btn), ratio_input)
            self.layout().addWidget(save_analytics_point_btn)