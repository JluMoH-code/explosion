import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter

class ZoomingLabel(QLabel):
    clicked_point = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        self.scale_value = 1.0
        self.is_mouse_pressed = False 
        self.mouse_point = QPoint() 
        self.crop_rect = QRect()
        self.center_crop_rect = QPoint()

        self.SCALE_MAX = 20.0
        self.SCALE_MIN = 1.0
        self.SCALE_STEP = 0.05

    def setPixmap(self, pixmap):
        """
        Устанавливаем изображение для QLabel.
        """
        super().setPixmap(pixmap)
        self.crop_rect = pixmap.rect()
        self.center_crop_rect = self.crop_rect.center()
        self.update()

    def paintEvent(self, event):
        """
        Перерисовываем изображение с учетом масштаба и обрезки.
        """
        if self.pixmap() is None:
            return

        painter = QPainter(self)

        # Рассчитываем область видимости с учетом текущего масштаба
        scaled_pixmap = self.crop_pixmap()

        # Отрисовываем результат
        painter.drawPixmap(self.rect(), scaled_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_mouse_pressed = True
            self.mouse_point = event.pos()

            image_coords = self.getImageCoordinatesFromMouse(self.mouse_point)
            self.clicked_point.emit(image_coords)

        if event.button() == Qt.RightButton:
            self.is_mouse_pressed = False
            self.scale_value = self.SCALE_MIN_VALUE

        self.update()

    def mouseMoveEvent(self, event):
        if self.is_mouse_pressed and self.scale_value > 1.0:
            delta = event.pos() - self.mouse_point
            self.move_crop_rect(event.pos(), delta)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_mouse_pressed = False

    def wheelEvent(self, event):
        """
        Обрабатываем колесо мыши для изменения масштаба.
        """
        num_steps = event.angleDelta().y() / 120

        old_scale = self.scale_value
        self.scale_value = self.calculate_scale_value(num_steps, self.scale_value)

        # Изменение координат для зумирования в точку под курсором
        self.changeWheelValue(event.pos(), old_scale)
        self.update()

    def crop_pixmap(self):
        crop_size = self.size() / self.scale_value
        self.crop_rect.setSize(crop_size)

        # Ограничиваем crop_rect в пределах исходного изображения
        self.crop_rect.moveCenter(self.center_crop_rect)
        self.crop_rect = self.crop_rect.intersected(self.pixmap().rect())

        # Вырезаем часть изображения
        cropped_pixmap = self.pixmap().copy(self.crop_rect)

        # Масштабируем вырезанную область до размеров QLabel
        scaled_pixmap = cropped_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return scaled_pixmap

    def getImageCoordinatesFromMouse(self, mouse_pos):
        adjustedMousePoint = mouse_pos + self.crop_rect.topLeft() * self.scale_value
        scaledMousePoint = adjustedMousePoint / self.scale_value
        
        return scaledMousePoint

    def move_crop_rect(self, pos, delta):
        self.mouse_point = pos
        self.center_crop_rect -= delta / self.scale_value
        self.center_crop_rect = self.clamp_crop()

    def calculate_scale_value(self, num_steps, old):
        if num_steps > 0:
            scale_value = min(old * (1 + self.SCALE_STEP), self.SCALE_MAX)
        else:
            scale_value = max(old * (1 - self.SCALE_STEP), self.SCALE_MIN)
        return scale_value

    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))
    
    def clamp_crop(self):
        """
        Ограничивает координаты центра области обрезки в пределах изображения.
        """
        crop_size = self.crop_rect.size()
        pixmap_size = self.pixmap().size()

        x = int(self.clamp(self.center_crop_rect.x(), crop_size.width() / 2, pixmap_size.width() - crop_size.width() / 2))
        y = int(self.clamp(self.center_crop_rect.y(), crop_size.height() / 2, pixmap_size.height() - crop_size.height() / 2))

        return QPoint(x, y)

    def changeWheelValue(self, mouse_pos, old_scale):
        """
        Изменение позиции области обрезки при зумировании в ту точку, где находится курсор.
        """
        # Получаем координаты курсора относительно изображения
        image_pos_before_zoom = self.getImageCoordinatesFromMouse(mouse_pos)

        # Масштабируем изображение
        scale_factor = self.scale_value / old_scale

        # Считаем новое смещение области обрезки
        offset = (image_pos_before_zoom - self.crop_rect.center()) * (scale_factor - 1)

        # Смещаем область обрезки в направлении курсора
        self.center_crop_rect += offset

        self.center_crop_rect = self.clamp_crop()
        self.update()


class MainWindow(QMainWindow):
    def __init__(self, path):
        super().__init__()
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.is_selecting_point = False

        self.setWindowTitle("Zoomable Image Viewer")
        self.setGeometry(100, 100, self.WIDTH, self.HEIGHT)

        # Основной виджет QLabel
        self.label = ZoomingLabel(self)
        self.setCentralWidget(self.label)

        # Загружаем изображение
        self.load_image(path)

        self.label.clicked_point[QPoint].connect(self.on_mouse_clicked)

    def load_image(self, image_path):
        """
        Загружаем изображение и отображаем его в QLabel.
        """
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(self.WIDTH, self.HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pixmap.isNull():
            print("Ошибка: не удалось загрузить изображение.")
        else:
            self.label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        """
        Обрабатываем нажатие клавиши 'e' для активации режима выбора точки.
        """
        if event.key() == Qt.Key_E:
            self.is_selecting_point = True
            print("Режим выбора точки активирован. Кликните по изображению.")

    @pyqtSlot(QPoint)
    def on_mouse_clicked(self, pos):
        """
        Обрабатываем координаты клика мыши из ZoomingLabel.
        """
        if self.is_selecting_point:
            print(f"Координаты клика: x = {pos.x()}, y = {pos.y()}")
            self.is_selecting_point = False  # Отключаем режим выбора точки после первого клика

# Запуск приложения
def run_app():
    app = QApplication(sys.argv)
    window = MainWindow('C:\\Users\\Anton\\Downloads\\test_2.jpg')
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()