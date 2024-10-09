import numpy as np
from Point import Point
import cv2

class CoordinateConverter:  
    @staticmethod
    def convert_to_global(reference_points, target_point):
        """
        Определяет глобальные координаты для искомой точки на основе списка реперных точек.
        
        reference_points: Список реперных точек (Point), у которых есть local_coords и global_coords.
        target_point: Искомая точка (Point), у которой есть только local_coords.
        """
        if not reference_points:
            raise ValueError("Список реперных точек пуст.")
        
        if len(reference_points) < 4:
            raise ValueError("Необходимо как минимум 4 реперные точки для вычисления гомографии.")

        # Получение локальных и глобальных координат реперных точек
        local_coords = np.array([pt.local_coords for pt in reference_points], dtype='float32')
        global_coords = np.array([pt.global_coords for pt in reference_points], dtype='float32')

        # Нахождение матрицы гомографии
        H, status = cv2.findHomography(local_coords, global_coords, cv2.RANSAC)

        # Преобразование локальных координат искомой точки в глобальные
        target_local = np.array([[target_point.local_coords]], dtype='float32')  # добавляем лишний уровень вложенности для функции transform
        target_global = cv2.perspectiveTransform(target_local, H)

        target_point.global_coords = target_global[0][0]
        return target_point
    
    @staticmethod
    def simple_linear_transformation(reference_points, target_point):
        if len(reference_points) < 2:
            raise ValueError("Для линейного преобразования необходимо как минимум 2 реперные точки.")
        
        # Получаем локальные и глобальные координаты
        local_coords = np.array([pt.local_coords for pt in reference_points], dtype='float32')
        global_coords = np.array([pt.global_coords for pt in reference_points], dtype='float32')

        # Линейная регрессия для определения коэффициентов
        A = np.vstack([local_coords.T, np.ones(len(local_coords))]).T
        m, c, a = np.linalg.lstsq(A, global_coords, rcond=None)[0]

        # Применяем к искомой точке
        target_local = np.array(target_point.local_coords)
        target_global = m @ target_local + c

        target_point.global_coords = target_global
        return target_point


# Пример использования
if __name__ == "__main__":
    target_point = Point(local_coords=(576, 403))  
    ref_points = [
        Point(local_coords=(313, 718), global_coords=(48.757120, 44.824560)),
        Point(local_coords=(510, 832), global_coords=(48.756926, 44.825104)),
        Point(local_coords=(826, 742), global_coords=(48.757074, 44.825941)),
        Point(local_coords=(862, 698), global_coords=(48.757147, 44.826040)),
        Point(local_coords=(877, 319), global_coords=(48.757834, 44.826075)),
        Point(local_coords=(799, 209), global_coords=(48.758027, 44.825850)),
        Point(local_coords=(421, 169), global_coords=(48.758092, 44.824850)),
        Point(local_coords=(314, 249), global_coords=(48.757959, 44.824578)),
        Point(local_coords=(268, 295), global_coords=(48.757867, 44.824446)),
        ]

    target_point = CoordinateConverter.convert_to_global(ref_points, target_point)
    
    expected_target_point = Point(local_coords=(576, 403), global_coords=(48.757668, 44.825271))  # Ожидаемые координаты

    # Рассчитаем отклонение
    error = np.linalg.norm(target_point.global_coords - expected_target_point.global_coords)
    print(f"Получена точка: {target_point}")
    print(f"Ожидается точка: {expected_target_point}")
    print(f"Отклонение от ожидаемого результата: {error} метров")
