import random

class TempModeSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        if random.random() < 0.1:
            self.value = random.randint(0, 7)
        return self.value
