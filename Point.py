import numpy as np

class Point:
    def __init__(self, local_coords = None, global_coords = None):
        """
        local_coords: Координаты точки на изображении (локальные)
        global_coords: Глобальные координаты этой точки на поле
        """
        self.local_coords = local_coords
        self.global_coords = global_coords
        
    def __repr__(self):
        return f"Point (local_coords={self.local_coords}, global_coords={self.global_coords})"
    
    def has_global(self):
        if self.global_coords is not None: return True
        return False
    
    def to_dict(self):
        """
        Преобразует объект Point в словарь для последующей сериализации в JSON.
        """
        return {
            "local_coords": self.local_coords.tolist() if isinstance(self.local_coords, np.ndarray) else self.local_coords,
            "global_coords": self.global_coords.tolist() if isinstance(self.global_coords, np.ndarray) else self.global_coords
        }