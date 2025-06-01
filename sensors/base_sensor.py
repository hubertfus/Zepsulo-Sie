class BaseSensor:
    def __init__(self, base_value):
        self.value = base_value

    def simulate(self):
        raise NotImplementedError("simulate() must be implemented in subclass.")
