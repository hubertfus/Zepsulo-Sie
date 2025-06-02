import random
from sensors.base_sensor import BaseSensor

class IPSensor(BaseSensor):
    def __init__(self, base_value, min_value=1, max_value=10):
        super().__init__(base_value, min_value, max_value)

    def simulate(self, cs_value):
        self.value = 0.05 * cs_value + random.uniform(-1, 1)
        self.clamp_value()
        return self.get_value()
