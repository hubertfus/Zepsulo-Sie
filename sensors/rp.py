import random

class RPSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        fluctuation = random.randint(-5, 5)
        self.value = max(0, self.value + fluctuation)
        return self.value
