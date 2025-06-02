import random
from sensors.base_sensor import BaseSensor

class CSSensor(BaseSensor):
    def __init__(self, base_value, min_value=0, max_value=100):
        super().__init__(base_value, min_value, max_value)

    def simulate(self, uss_value, footfall):
        self.value += 0.5 * uss_value + 0.3 * footfall + random.uniform(-3, 3)
        self.clamp_value()
        return self.get_value()
