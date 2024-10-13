from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel

class CoordInputWindow(QDialog):
    def __init__(self, point, update):
        super().__init__()
        self.setWindowTitle("Координаты точки")
        self.point = point
        self.update = update

        self.local_input = QLabel("Локальные координаты", self)

        # Поля для отображения локальных координат (заблокированные)
        self.local_x_input = QLineEdit(self)
        self.local_x_input.setText(str(self.point.local_coords[0]))
        self.local_x_input.setDisabled(True)  # Заблокировано для изменения

        self.local_y_input = QLineEdit(self)
        self.local_y_input.setText(str(self.point.local_coords[1]))
        self.local_y_input.setDisabled(True)  # Заблокировано для изменения

        self.global_input = QLabel("Глобальные координаты", self)
        
        # Поля для ввода глобальных координат
        self.coord_x_input = QLineEdit(self)
        self.coord_x_input.setPlaceholderText("Глобальная координата X")
        self.coord_x_input.textChanged.connect(lambda: self.reset_color(self.coord_x_input))

        self.coord_y_input = QLineEdit(self)
        self.coord_y_input.setPlaceholderText("Глобальная координата Y")
        self.coord_y_input.textChanged.connect(lambda: self.reset_color(self.coord_y_input))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.local_input)
        layout.addWidget(self.local_x_input)
        layout.addWidget(self.local_y_input)
        layout.addWidget(self.global_input)
        layout.addWidget(self.coord_x_input)
        layout.addWidget(self.coord_y_input)
        
        if update:
            if self.point.global_coords is not None:
                self.coord_x_input.setText(str(self.point.global_coords[0]))
                self.coord_y_input.setText(str(self.point.global_coords[1]))
            self.update_point_btn = QPushButton("Обновить точку", self)
            self.delete_point_btn = QPushButton("Удалить точку", self)
            self.update_point_btn.clicked.connect(self.accept_coords)
            self.delete_point_btn.clicked.connect(self.reject_with_delete)
            layout.addWidget(self.update_point_btn)
            layout.addWidget(self.delete_point_btn)

        elif point.global_coords is not None:
            self.coord_x_input.setText(str(self.point.global_coords[0]))
            self.coord_y_input.setText(str(self.point.global_coords[1]))
            self.coord_x_input.setDisabled(True)  # Заблокировано для изменения
            self.coord_y_input.setDisabled(True)  # Заблокировано для изменения
        else:
            # Кнопки для добавления и удаления точек
            self.add_point_btn = QPushButton("Добавить точку", self)
            self.delete_point_btn = QPushButton("Удалить точку", self)
            self.add_point_btn.clicked.connect(self.accept_coords)
            self.delete_point_btn.clicked.connect(self.reject_with_delete)
            layout.addWidget(self.add_point_btn)
            layout.addWidget(self.delete_point_btn)
            
        self.setLayout(layout)

    def accept_coords(self):
        """
        Подтверждение ввода координат (глобальных и локальных).
        """
        x, y = 0, 0
        x_text = self.coord_x_input.text()
        y_text = self.coord_y_input.text()
        has_errors = False
            
        try:
            x = float(self.coord_x_input.text())
        except ValueError:
            self.coord_x_input.setText("")
            self.coord_x_input.setPlaceholderText("Координата должна быть числом!")
            self.coord_x_input.setStyleSheet('color: red')
            has_errors = True
            
        try:
            y = float(self.coord_y_input.text())
        except ValueError:
            self.coord_y_input.setText("")
            self.coord_y_input.setPlaceholderText("Координата должна быть числом!")   
            self.coord_y_input.setStyleSheet('color: red')
            has_errors = True
            
        if x_text == "":
            self.coord_x_input.setPlaceholderText("Глобальная координата X")
            self.coord_x_input.setStyleSheet('color: red')
            has_errors = True
        if y_text == "":
            self.coord_y_input.setPlaceholderText("Глобальная координата Y")
            self.coord_y_input.setStyleSheet('color: red')
            has_errors = True
            
        if not has_errors:
            self.point.global_coords = (x, y)
            self.accept()

    def reject_with_delete(self):
        self.point = None
        super().reject()

    def reset_color(self, input_field):
        """
        Сброс цвета текста в указанном поле ввода.
        """
        input_field.setStyleSheet('color: black')

    def get_point(self):
        """
        Возвращает глобальные и локальные координаты после подтверждения.
        """
        return self.point