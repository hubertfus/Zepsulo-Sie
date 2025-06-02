import random
from sensors.base_sensor import BaseSensor

class RPSensor(BaseSensor):
    def __init__(self, base_value, min_value=0, max_value=100):
        super().__init__(base_value, min_value, max_value)

    def simulate(self, footfall, temp_mode):
        self.value = footfall * 5 + temp_mode * 10 + random.uniform(-5, 5)
        self.clamp_value()
        return self.get_value()
