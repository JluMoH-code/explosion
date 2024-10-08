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
    def open_coords_input_window(local_coords):
        """
        Открыть новое окно для ввода глобальных координат.
        """
        from CoordInputWindow import CoordInputWindow
        window = CoordInputWindow(local_coords)
        window.exec_()
        if window.get_coords().global_coords is not None:
            return window.get_coords()  # Возвращает координаты после закрытия окна
        else: return False 
