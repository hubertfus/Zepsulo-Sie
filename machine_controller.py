import time
from ml_model import MLModel
import threading

class MachineController:
    def __init__(self):
        self.ml_model = MLModel()
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()

    def start_machine(self):
        self.is_running = True
        self.run_cycle()

    def stop_machine(self):
        self.is_running = False

    def pause_machine(self, seconds=10):
        self.is_paused = True
        self.pause_event.clear()
        print(f"Maszyna wstrzymana na {seconds} sekund - ryzyko awarii >70%")
        time.sleep(seconds)
        self.is_paused = False
        self.pause_event.set()

    def run_cycle(self):
        while self.is_running:
            if self.is_paused:
                self.pause_event.wait()
                continue

            sensor_data = self.read_sensors()

            # Predykcja awarii
            failure_prob = self.ml_model.predict_failure(sensor_data)
            print(f"Prawdopodobieństwo awarii: {failure_prob:.2f}%")

            if failure_prob > 70:
                self.pause_machine()
            elif 70 > failure_prob > 40:
                print("Wysokie ryzyko zepsucia się maszyny")
            else:
                print("Kontynuacja normalnej pracy")

            time.sleep(1)

    def read_sensors(self):
        raise NotImplementedError("This method should be implemented in the main application")