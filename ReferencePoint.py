class ReferencePoint:
    def __init__(self, local_coords = None, global_coords = None):
        """
        local_coords: Координаты точки на изображении (локальные)
        global_coords: Глобальные координаты этой точки на поле
        """
        self.local_coords = local_coords
        self.global_coords = global_coords
        
    def __repr__(self):
        return f"ReferencePoint (local_coords={self.local_coords}, global_coords={self.global_coords})"