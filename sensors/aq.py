import random

class AQSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        change = random.choice([-1, 0, 1])
        self.value = max(0, min(7, self.value + change))
        return self.value
