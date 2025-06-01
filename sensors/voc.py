import random

class VOCSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        if random.random() < 0.2:
            self.value = max(0, min(6, self.value + random.choice([-1, 0, 1])))
        return self.value
