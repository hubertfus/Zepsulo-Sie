import random
from sensors.base_sensor import BaseSensor

class USSSensor(BaseSensor):
    def __init__(self, base_value, min_value=0, max_value=100):
        super().__init__(base_value, min_value, max_value)

    def simulate(self, rp_value):
        self.value = rp_value * 0.7 + random.uniform(-3, 3)
        self.clamp_value()
        return self.get_value()
