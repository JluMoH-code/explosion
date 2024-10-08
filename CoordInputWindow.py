from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from ReferencePoint import ReferencePoint

class CoordInputWindow(QDialog):
    def __init__(self, local_coords):
        super().__init__()
        self.setWindowTitle("Введите глобальные координаты")
        self.point = ReferencePoint(local_coords)

        self.local_input = QLabel("Локальные координаты", self)

        # Поля для отображения локальных координат (заблокированные)
        self.local_x_input = QLineEdit(self)
        self.local_x_input.setText(str(local_coords[0]))
        self.local_x_input.setDisabled(True)  # Заблокировано для изменения

        self.local_y_input = QLineEdit(self)
        self.local_y_input.setText(str(local_coords[1]))
        self.local_y_input.setDisabled(True)  # Заблокировано для изменения

        self.global_input = QLabel("Глобальные координаты", self)
        
        # Поля для ввода глобальных координат
        self.coord_x_input = QLineEdit(self)
        self.coord_x_input.setPlaceholderText("Глобальная координата X")

        self.coord_y_input = QLineEdit(self)
        self.coord_y_input.setPlaceholderText("Глобальная координата Y")

        # Кнопки для добавления и удаления точек
        self.add_point_btn = QPushButton("Добавить точку", self)
        self.delete_point_btn = QPushButton("Удалить точку", self)
        self.add_point_btn.clicked.connect(self.accept_coords)
        self.delete_point_btn.clicked.connect(self.reject)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.local_input)
        layout.addWidget(self.local_x_input)
        layout.addWidget(self.local_y_input)
        layout.addWidget(self.global_input)
        layout.addWidget(self.coord_x_input)
        layout.addWidget(self.coord_y_input)
        layout.addWidget(self.add_point_btn)
        layout.addWidget(self.delete_point_btn)
        self.setLayout(layout)

    def accept_coords(self):
        """
        Подтверждение ввода координат (глобальных и локальных).
        """
        try:
            x = float(self.coord_x_input.text())
            y = float(self.coord_y_input.text())
            self.point.global_coords = (x, y)
            self.accept()
        except ValueError:
            # Ошибка ввода
            self.coord_x_input.setText("")
            self.coord_y_input.setText("")

    def get_coords(self):
        """
        Возвращает глобальные и локальные координаты после подтверждения.
        """
        return self.point