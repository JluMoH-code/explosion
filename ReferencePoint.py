class ReferencePoint:
    def __init__(self, image_coords, global_coords):
        """
        image_coords: Координаты точки на изображении (локальные)
        global_coords: Глобальные координаты этой точки на поле
        """
        self.image_coords = image_coords
        self.global_coords = global_coords
        
    def __repr__(self):
        return f"ReferencePoint (image_coords={self.image_coords}, global_coords={self.global_coords})"