#TODO: Change code 


import board
import adafruit_vl53l1x

class DistanceSensor:
    __slots__ = ("mode, timing_budget, sensor, last_val, model_info") 
    mode: int
    timing_budget: int
    sensor: str
    last_val: int | None
    model_info = dict

    def __init__(self, mode, timing_budget):
        i2c = board.I2C()
        self.sensor = adafruit_vl53l1x.VL53L1X(i2c)
        self.sensor.distance_mode = mode 
        self.sensor.timing_budget = timing_budget
        self.last_val = None

        self.model_info = {}
        self.mode = mode
        self.timing_budget = timing_budget


    def read_dist(self):
        self.sensor.start_ranging()
        if self.sensor.data_ready:
            dist = self.sensor.distance
            self.sensor.clear_interrupt()
            if dist is not None:
                self.last_val = dist
        return self.last_val

    def end(self):
        self.sensor.stop_ranging()
    
    def get_info(self):
        self.model_info["Distance Mode"] = self.mode
        self.model_info["Timing Budget"] = self.timing_budget
        self.model_info["Sensor Info"] = self.sensor
        return self.model_info