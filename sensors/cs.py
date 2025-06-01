import random

class CSSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        self.value = max(0, min(7, self.value + random.choice([-1, 0, 1])))
        return self.value
