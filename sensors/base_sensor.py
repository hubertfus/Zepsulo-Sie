# base_sensor.py
class BaseSensor:
    def __init__(self, base_value, min_value=None, max_value=None):
        self.value = base_value
        self.min_value = min_value
        self.max_value = max_value

    def get_value(self):
        return round(self.value, 2) if isinstance(self.value, float) else self.value

    def clamp_value(self):
        if self.min_value is not None:
            self.value = max(self.min_value, self.value)
        if self.max_value is not None:
            self.value = min(self.max_value, self.value)

    def simulate_shutdown(self):
        decrease = self.value * 0.15
        self.value = max(self.min_value or 0, self.value - decrease)
        self.clamp_value()
