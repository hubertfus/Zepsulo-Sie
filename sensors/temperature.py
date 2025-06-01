import random

class TemperatureSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        change = random.uniform(-0.5, 0.5)
        self.value = round(min(100, max(0, self.value + change)), 1)
        return self.value
