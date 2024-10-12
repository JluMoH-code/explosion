from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2

class DisplayUtils:
    @staticmethod
    def open_image_file():
        """
        Открыть диалоговое окно для выбора файла изображения или видео.
        """
        file_name, _ = QFileDialog.getOpenFileName(None, "Выберите изображение", "", "Images (*.png *.jpg *.bmp *.jpeg);;Videos (*.mp4 *.avi *.mkv)")
        if not file_name:
            return False
        if not cv2.haveImageReader(file_name):
            raise Exception('Ошибка чтения файла')
        return file_name        

    @staticmethod
    def show_message(message):
        """
        Показать сообщение в диалоговом окне.
        """
        msg = QMessageBox()
        msg.setText(message)
        msg.exec_()
        
    @staticmethod
    def from_cv_to_qimg(image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_height, original_width, _ = image_rgb.shape
        
        # Преобразуем изображение OpenCV в формат QImage
        bytes_per_line = 3 * original_width
        return QImage(image_rgb.data, original_width, original_height, bytes_per_line, QImage.Format_RGB888)

    @staticmethod
    def get_scaled_pixmap(image, max_width=1280, max_height=720):
        
        original_width = image.width()
        original_height = image.height()
        
        # Рассчитываем коэффициент масштабирования
        scale_factor = min(max_width / original_width, max_height / original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Преобразуем QImage в QPixmap и масштабируем
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)

        return scaled_pixmap, scale_factor

    @staticmethod
    def open_coords_input_window(point, update=False):
        """
        Открыть новое окно для ввода глобальных координат.
        """
        from CoordInputWindow import CoordInputWindow
        
        window = CoordInputWindow(point, update)
        window.exec_()
        
        return window.get_point() if window.get_point() is not None else False
    
    @staticmethod
    def open_template_input_window(image):
        """
        Открыть новое окно для выбора шаблона.
        """
        from TemplateSelectorWindow import TemplateSelectorWindow
        
        window = TemplateSelectorWindow(image)
        window.exec_()
        
        return window.get_template() if window.get_template() is not None else False
    
    @staticmethod
    def calculate_scale_factor(original_height, original_width, max_width=1280, max_height=720):
        if original_width > max_width or original_height > max_height:
            scale_factor = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
        else:
            new_width, new_height = original_width, original_height
            scale_factor = 1.0
            
        return scale_factor, new_width, new_height
        