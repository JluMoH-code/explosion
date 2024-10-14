import cv2
import numpy as np
from enum import Enum
from Point import Point
from DisplayUtils import DisplayUtils

class ReferencePointsSelector:
    def __init__(self):
        self.points = []
        
    def ask_for_global_coords(self):
        """
        Ввод глобальных координат через консоль или GUI.
        """
        x = float(input("Enter global coords X: "))
        y = float(input("Enter global coords Y: "))
        return (x, y)
        
    def select_points(self, image, template=None, scale_factor=1):
        """
        Определяет логику выбора точек на изображении.
        """
        raise NotImplementedError
    
    def get_points(self):
        """
        Возвращает список всех выбранных точек: [(локальные_координаты, глобальные_координаты)].
        """
        return self.points
    
class ManualPointsSelector(ReferencePointsSelector):
    def __init__(self, scale_factor = 1):
        super().__init__()
        self.scale_factor = scale_factor
    
    def select_point(self, event):
        """
        Обработка клика на изображении для выбора точки.
        """
        x_scaled = event.pos().x()
        y_scaled = event.pos().y()
        
        # Пересчитываем координаты обратно на оригинальные
        x_original = int(x_scaled / self.scale_factor)
        y_original = int(y_scaled / self.scale_factor)
        
        # Открываем окно для ввода глобальных координат
        coords_input = DisplayUtils.open_coords_input_window(local_coords=(x_original, y_original))
        if coords_input:
            self.points.append(coords_input)

class AutoPointsSelector(ReferencePointsSelector):
    def __init__(self):
        super().__init__()

    def select_points(self, image):
        """
        Автоматическое определение точек на изображении.
        """
        pass

class TemplateMatchingSelector(ReferencePointsSelector):
    def __init__(self):
        super().__init__()
    
    def select_points(self, image, template, scale_factor=1):
        """
        Метод для нахождения точек с использованием шаблонного распознавания.
        """
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(result >= threshold)

        for pt in zip(*loc[::-1]):
            point = Point(pt)
            self.points.append(point)
            print(f"Автоматически (по шаблону) добавлена точка: {point}")

        return self.points
    
class Selector(Enum):
    Manual = ManualPointsSelector()
    Auto = AutoPointsSelector()
    Template = TemplateMatchingSelector()