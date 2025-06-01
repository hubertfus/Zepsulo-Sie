from sensors.footfall import FootfallSensor
from sensors.temp_mode import TempModeSensor
from sensors.aq import AQSensor
from sensors.uss import USSSensor
from sensors.cs import CSSensor
from sensors.voc import VOCSensor
from sensors.rp import RPSensor
from sensors.ip import IPSensor
from sensors.temperature import TemperatureSensor

class SensorSimulator:
    def __init__(self, csv_file='sensor_data.csv'):
        import pandas as pd
        import random

        df = pd.read_csv(csv_file)
        self.base_row = df.sample(n=1, random_state=random.randint(0, 100)).iloc[0].to_dict()

        self.sensors = {
            'footfall': FootfallSensor(self.base_row['footfall']),
            'tempMode': TempModeSensor(self.base_row['tempMode']),
            'AQ': AQSensor(self.base_row['AQ']),
            'USS': USSSensor(self.base_row['USS']),
            'CS': CSSensor(self.base_row['CS']),
            'VOC': VOCSensor(self.base_row['VOC']),
            'RP': RPSensor(self.base_row['RP']),
            'IP': IPSensor(self.base_row['IP']),
            'Temperature': TemperatureSensor(self.base_row['Temperature'])
        }

        self.fail = int(self.base_row.get('fail', 0))

    def get_next_reading(self):
        result = {}
        for name, sensor in self.sensors.items():
            result[name] = sensor.simulate()
        result['fail'] = self.fail
        return result
