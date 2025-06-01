import random

class IPSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        self.value += random.choice([-1, 0, 1])
        self.value = max(1, min(7, self.value))
        return self.value
