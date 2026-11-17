import threading
import time
import logging

from picamera2 import Picamera2

class Camera:
    width: int
    height: int
    camera: Picamera2
    

    def __init__(self, width = 640, height = 480):
        self.width = width
        self.height = height
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_video_configuration({"size": (self.width, self.height), "format": "YUV420"}))
        self.frame = None
        self.frame_time = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = None
    
    def start(self):
        self.camera.start()
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.thread.start() 

    def capture_loop(self):
        while not self._stop_event.is_set():
            try:
                frame = self.camera.capture_array()
                with self.lock:
                    self.frame = frame
                    self.frame_time = time.time()
            except Exception as e:
                logging.error(f"Error capturing frame: {e}")
                print(f"Error capturing frame: {e}")
            time.sleep(0.01)  # Adjust the sleep time as needed for your application
    
    def get_latest_frame(self):
        with self.lock:
            return self.frame, self.frame_time