from ReferencePointsSelector import *

class ReferencePointsManager:
    def __init__(self, selector: ReferencePointsSelector = None):
        self.selector = selector

    def set_selector(self, selector: ReferencePointsSelector):
        """
        Устанавливаем новый способ выбора реперных точек.
        """
        self.selector = selector

    def select_points(self, image, template=None, scale_factor=1):
        """
        Выполняем выбор точек через установленный селектор.
        """
        return self.selector.select_points(image, template, scale_factor)

    def get_points(self):
        """
        Получаем точки через текущий селектор.
        """
        return self.selector.get_points()
