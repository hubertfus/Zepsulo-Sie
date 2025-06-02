import random
import pandas as pd

from sensors.cs import CSSensor
from sensors.ip import IPSensor
from sensors.rp import RPSensor
from sensors.temperature import TemperatureSensor
from sensors.uss import USSSensor


class SensorSimulator:
    def __init__(self, csv_path):
        df = pd.read_csv(csv_path)
        base = df.iloc[0]

        self.static_state = {
            'footfall': base['footfall'],
            'tempMode': base['tempMode'],
            'AQ': base['AQ'],
            'VOC': base['VOC'],
            'fail': 0
        }

        self.sensors = {
            'RP': RPSensor(base['RP'], min_value=base['RP']),
            'USS': USSSensor(base['USS'], min_value=base['USS']),
            'CS': CSSensor(base['CS'], min_value=base['CS']),
            'IP': IPSensor(base['IP'], min_value=base['IP']),
            'Temperature': TemperatureSensor(base['Temperature'], min_value=20.0)
        }

    def get_next_reading(self):
        if random.random() < 0.3:
            self.static_state['footfall'] += 1

        self.static_state['AQ'] = min(100, max(0, self.static_state['AQ'] + random.uniform(-2, 2)))
        self.static_state['VOC'] = min(100, max(0, self.static_state['VOC'] + random.uniform(-1, 1)))

        footfall = self.static_state['footfall']
        temp_mode = 1 if self.sensors['Temperature'].get_value() > 60 else 0
        self.static_state['tempMode'] = temp_mode

        self.sensors['RP'].simulate(footfall, temp_mode)
        self.sensors['USS'].simulate(self.sensors['RP'].get_value())
        self.sensors['CS'].simulate(self.sensors['USS'].get_value(), footfall)
        self.sensors['IP'].simulate(self.sensors['CS'].get_value())
        self.sensors['Temperature'].simulate(temp_mode, self.sensors['CS'].get_value(), self.sensors['USS'].get_value(), footfall)

        self.static_state['fail'] = 1 if random.random() < 0.01 else 0

        result = dict(self.static_state)
        for name, sensor in self.sensors.items():
            result[name] = sensor.get_value()

        return result
