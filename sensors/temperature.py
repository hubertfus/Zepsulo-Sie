import random
from sensors.base_sensor import BaseSensor

class TemperatureSensor(BaseSensor):
    def __init__(self, base_value, min_value=20.0, max_value=100.0):
        super().__init__(base_value, min_value, max_value)

    def simulate(self, temp_mode, cs_value, uss_value, footfall):
        raw_temp = uss_value * 0.3 + cs_value * 0.2 + footfall * 0.5
        cooling = -3 if temp_mode == 1 else 0
        self.value = raw_temp + cooling + random.uniform(-2, 2)
        self.clamp_value()
        return self.get_value()
