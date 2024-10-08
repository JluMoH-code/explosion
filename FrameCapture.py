import cv2
import time

try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    PiCamera_import = True
except:
    print("Picamera import error")
    PiCamera_import = False

try:
    from picamera2 import Picamera2
    from libcamera import Transform, ColorSpace, controls
    PiCamera2_import = True
except ImportError:
    print("Picamera2 import error")
    PiCamera2_import = False

class FrameCapture:
    def get_frame(self):
        raise NotImplementedError
    
    def release(self):
        raise NotImplementedError
    
    def is_opened(self):
        raise NotImplementedError
    
    def configure(self, **kwargs):
        raise NotImplementedError

class OpenCVFrameCapture(FrameCapture):
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.is_opened():
            raise Exception(f"Не удалось открыть видеофайл по пути: {video_path}")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Не удалось получить кадр из видеопотока")
        return frame
    
    def release(self):
        self.cap.release()
        
    def is_opened(self):
        return self.cap.isOpened()
    
    def configure(self, **kwargs):
        if 'width' in kwargs:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, kwargs['width'])
        if 'height' in kwargs:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, kwargs['height'])
        if 'fps' in kwargs:
            self.cap.set(cv2.CAP_PROP_FPS, kwargs['fps'])
    
class ImageFrameCapture(FrameCapture):
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = cv2.imread(file_path)
        if self.image is None:
            raise Exception(f"Не удалось загрузить изображение по пути: {file_path}")

    def get_frame(self):
        return self.image
    
    def release(self):
        pass
    
    def is_opened(self):
        return self.image is not None
    
    def configure(self, **kwargs):
        pass
 
if PiCamera_import:       
    class PiCameraCapture(FrameCapture):
        def __init__(self, resolution=(640, 480), framerate=32):
            self.camera = PiCamera()
            self.configure(resolution, framerate)
            self.raw_capture = PiRGBArray(self.camera, size=resolution)
            time.sleep(0.1)

        def get_frame(self):
            try:
                self.camera.capture(self.raw_capture, format="bgr")
                return self.raw_capture.array
            except Exception as e:
                raise Exception(f"Ошибка при захвате кадра: {e}")

        def release(self):
            self.camera.close()

        def is_opened(self):
            return True
        
        def configure(self, resolution, framerate):
            self.camera.resolution = resolution
            self.camera.framerate = framerate
            
        def configure(self, **kwargs):
            self.camera.resolution = kwargs.get('resolution', (640, 480))
            self.camera.framerate = kwargs.get('framerate', 32)
            self.raw_capture = PiRGBArray(self.camera, size=kwargs.get('resolution', (640, 480)))
    
if PiCamera2_import:    
    class PiCamera2Capture(FrameCapture):
        def __init__(self, mode=1, size=(1920,1080), lowres=(320,240), framerate=60, buffer_count=4, hflip=1, vflip=0):
            self.camera = Picamera2()
            self.configure(mode=1, size=size, lowres=lowres, framerate=framerate, buffer_count=buffer_count, hflip=hflip, vflip=vflip)
            self.camera.start()

        def camera_config(self, mode, size, lowres, framerate=60, buffer_count=4, hflip=1, vflip=0):
            modes = self.camera.sensor_modes
            mode = modes[mode]
            camera_config = self.camera.create_video_configuration(
                sensor={
                    "output_size": mode['size'],
                    "bit_depth": mode['bit_depth'],
                },
                raw={
                    "size": mode['size'],
                    "format": mode['unpacked'],
                },
                main={                                  # основной поток
                    "size": size,
                    "format": 'RGB888'
                },                    
                lores={"size": lowres},                 # отображаемый потк
                display="lores",
                transform=Transform(hflip=hflip, vflip=vflip),  # отражение по горизонтали/вертикали
                buffer_count=buffer_count,                         # хранимый буфер кадров, больше -- плавнее
                queue=False,
                controls={
                    "FrameRate": framerate,
                    # "FrameDurationLimits": (8333, 16666),    # microseconds per frame
                    "AfMode": controls.AfModeEnum.Continuous,
                },
                )                             
            return camera_config

        def get_frame(self):
            try:
                return self.camera.capture_array()
            except Exception as e:
                raise Exception(f"Ошибка при захвате кадра: {e}")

        def release(self):
            self.camera.close()

        def is_opened(self):
            return True
        
        def configure(self, mode, size, lowres, framerate, buffer_count, hflip, vflip):
            config = self.camera_config(mode, size, lowres, framerate, buffer_count, hflip, vflip)
            self.camera.configure(config)