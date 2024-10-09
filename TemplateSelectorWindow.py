from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QRubberBand, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QDialog
from DisplayUtils import DisplayUtils
import cv2

class TemplateSelectorWindow(QDialog):
    """
    Окно для выделения шаблона на изображении.
    """
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.template = None
        """
        Используется магическая QRubberBand
        """                
        self.rubberBand = None
        self.origin = QPoint()

        self.image_label = QLabel(self)
        scaled_pixmap, self.scale_factor = DisplayUtils.get_scaled_pixmap(self.image, 1280, 720)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())

        # Layout для изображения
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Настройка окна
        self.setWindowTitle('Выбор шаблона')
        self.resize(self.image_label.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            if not self.rubberBand:
                self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if self.rubberBand and not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
            rect = self.rubberBand.geometry()
            
            self.template = self.crop_image(rect)
            
            template_window = TemplateWindow(self.template)
            template_window.exec_()
            
            if template_window.accept_template:
                super().accept()
            else:
                self.template = None
                
    def get_template(self):
        return self.template
            
    def crop_image(self, rect):
        """
        Метод для вырезания области изображения, с учётом масштаба.
        """
        # Переводим координаты выделенной области обратно к оригинальному изображению
        x1 = int(rect.x() / self.scale_factor)
        y1 = int(rect.y() / self.scale_factor)
        x2 = int((rect.x() + rect.width()) / self.scale_factor)
        y2 = int((rect.y() + rect.height()) / self.scale_factor)

        # Обрезаем исходное изображение
        template = self.image.copy(x1, y1, x2 - x1, y2 - y1)
        return template  
            
class TemplateWindow(QDialog):
    """
    Окно для подтверждения шаблона.
    """
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.accept_template = False
        
        # Основной layout для всего окна
        self.main_layout = QVBoxLayout()
        self.bottom_layout = QHBoxLayout()

        self.image_label = QLabel(self)
        scaled_pixmap, self.scale_factor = DisplayUtils.get_scaled_pixmap(self.image, 1280, 720)
        self.image_label.setPixmap(scaled_pixmap)
        
        # Кнопка для подтверждения шаблона
        self.access_btn = QPushButton("Подтвердить", self)
        self.bottom_layout.addWidget(self.access_btn, alignment=Qt.AlignCenter)
        self.access_btn.clicked.connect(self.accept)
        
        # Кнопка для выбора другого шаблона
        self.change_template_btn = QPushButton("Выбрать другой", self)
        self.bottom_layout.addWidget(self.change_template_btn, alignment=Qt.AlignCenter)
        self.change_template_btn.clicked.connect(self.change_template_btn)

        self.main_layout.addWidget(self.image_label)
        self.main_layout.addLayout(self.bottom_layout)
        
        self.setLayout(self.main_layout)

        # Настройка окна
        self.setWindowTitle('Подтверждение шаблона')
        
    def accept(self):
        self.accept_template = True
        super().accept()        
    
    def change_template_btn(self):
        self.accept_template = False
        super().accept()  