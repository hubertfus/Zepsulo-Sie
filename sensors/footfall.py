import random

class FootfallSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        self.value += random.randint(0, 2)
        return self.value
