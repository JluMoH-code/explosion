from PyQt5.QtWidgets import QFileDialog, QMessageBox

class DisplayUtils:
    @staticmethod
    def open_image_file():
        """
        Открыть диалоговое окно для выбора файла изображения или видео.
        """
        file_name, _ = QFileDialog.getOpenFileName(None, "Выберите изображение", "", "Images (*.png *.jpg *.bmp *.jpeg);;Videos (*.mp4 *.avi *.mkv)")
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
    def open_coords_input_window(point, update=False):
        """
        Открыть новое окно для ввода глобальных координат.
        """
        from CoordInputWindow import CoordInputWindow
        
        window = CoordInputWindow(point, update)
        window.exec_()
        
        return window.get_point() if window.get_point() is not None else False
