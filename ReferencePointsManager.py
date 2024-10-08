from ReferencePointsSelector import *

class ReferencePointsManager:
    def __init__(self, selector: ReferencePointsSelector):
        self.selector = selector

    def set_selector(self, selector: ReferencePointsSelector):
        """
        Устанавливаем новый способ выбора реперных точек.
        """
        self.selector = selector

    def select_points(self, image):
        """
        Выполняем выбор точек через установленный селектор.
        """
        self.selector.select_points(image)

    def get_points(self):
        """
        Получаем точки через текущий селектор.
        """
        return self.selector.get_points()
