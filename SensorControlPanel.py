import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from sensor_simulator import SensorSimulator
from machine_controller import MachineController
import traceback
import threading

class SensorTogglePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Machine Panel")

        self.sensors = [
            'footfall', 'tempMode', 'AQ', 'USS',
            'CS', 'VOC', 'RP', 'IP', 'Temperature'
        ]

        self.data = {sensor: [] for sensor in self.sensors}
        self.value_labels = {}
        self.figures = {}
        self.axes = {}
        self.graph_lines = {}
        self.canvas_widgets = {}
        self.warning_lights = {}
        self.warning_states = {sensor: False for sensor in self.sensors}
        self.warning_blinking = {sensor: False for sensor in self.sensors}
        self.machine_running = False
        self.detail_windows = {}
        self.failure_prob = 0.0

        self.machine_controller = MachineController()
        self.machine_controller.read_sensors = self.get_current_sensor_data

        self.setup_ui()

        self.simulator = SensorSimulator('sensor_data.csv')
        self.sensor_objects = self.simulator.sensors

        self.root.after(300, self.update_live_data)

    def setup_ui(self):
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side="left", padx=10, pady=10, anchor="n")

        self.graph_container = tk.Frame(self.root)
        self.graph_container.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.graph_container)
        self.scrollbar = ttk.Scrollbar(self.graph_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        for i, sensor in enumerate(self.sensors):
            tk.Label(self.control_frame, text=sensor, font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5,
                                                                               sticky="w")

            value_label = tk.Label(self.control_frame, text="—", font=("Arial", 10))
            value_label.grid(row=i, column=1, padx=5, pady=5)
            self.value_labels[sensor] = value_label

            tk.Button(self.control_frame, text="Details",
                      command=lambda s=sensor: self.open_sensor_detail_view(s)).grid(row=i, column=2, padx=5, pady=5)

            warning_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
            warning_light.grid(row=i, column=3, padx=5, pady=5)
            warning_circle = warning_light.create_oval(5, 5, 15, 15, fill="green")
            self.warning_lights[sensor] = (warning_light, warning_circle)

        tk.Label(self.control_frame, text="Failure Risk", font=("Arial", 10)).grid(
            row=len(self.sensors), column=0, padx=5, pady=5, sticky="w")

        self.failure_prob_label = tk.Label(self.control_frame, text="0.00%", font=("Arial", 10))
        self.failure_prob_label.grid(row=len(self.sensors), column=1, padx=5, pady=5)

        self.fail_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
        self.fail_light.grid(row=len(self.sensors), column=2, padx=5, pady=5)
        self.fail_circle = self.fail_light.create_oval(5, 5, 15, 15, fill="gray")

        tk.Label(self.control_frame, text="Machine Status", font=("Arial", 10)).grid(
            row=len(self.sensors) + 1, column=0, padx=5, pady=5, sticky="w")

        self.status_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
        self.status_light.grid(row=len(self.sensors) + 1, column=1, padx=5, pady=5)
        self.status_circle = self.status_light.create_oval(5, 5, 15, 15, fill="gray")

        tk.Button(self.control_frame, text="Show All Plots", command=self.show_all_plots).grid(
            row=len(self.sensors) + 2, column=0, columnspan=3, pady=5)

        self.toggle_button = tk.Button(
            self.control_frame, text="Start Machine",
            command=self.toggle_machine, bg="green", fg="white")
        self.toggle_button.grid(row=len(self.sensors) + 3, column=0, columnspan=3, pady=5)

        for sensor in self.sensors:
            fig, ax = plt.subplots(figsize=(4, 2.5))
            ax.set_title(sensor)
            ax.grid(True)
            line, = ax.plot([], [])
            self.figures[sensor] = fig
            self.axes[sensor] = ax
            self.graph_lines[sensor] = line

        self.show_all_plots()

    def get_current_sensor_data(self):
        return {
            'footfall': self.data['footfall'][-1] if self.data['footfall'] else 0,
            'tempMode': self.data['tempMode'][-1] if self.data['tempMode'] else 0,
            'AQ': self.data['AQ'][-1] if self.data['AQ'] else 0,
            'USS': self.data['USS'][-1] if self.data['USS'] else 0,
            'CS': self.data['CS'][-1] if self.data['CS'] else 0,
            'VOC': self.data['VOC'][-1] if self.data['VOC'] else 0,
            'RP': self.data['RP'][-1] if self.data['RP'] else 0,
            'IP': self.data['IP'][-1] if self.data['IP'] else 0,
            'Temperature': self.data['Temperature'][-1] if self.data['Temperature'] else 0
        }

    def toggle_machine(self):
        self.machine_running = not self.machine_running
        self.update_status_light()

        if self.machine_running:
            self.toggle_button.config(text="Stop Machine", bg="red", fg="white")
            machine_thread = threading.Thread(
                target=self.machine_controller.start_machine,
                daemon=True)
            machine_thread.start()
        else:
            self.toggle_button.config(text="Start Machine", bg="green", fg="white")
            self.machine_controller.stop_machine()

    def update_status_light(self):
        if not self.machine_running:
            color = "gray"
        elif self.machine_controller.is_paused:
            color = "red"
        else:
            color = "green"

        self.status_light.itemconfig(self.status_circle, fill=color)

    def update_live_data(self):
        try:
            if self.machine_running:
                row = self.simulator.get_next_reading()

                for sensor in self.sensors:
                    value = row[sensor]
                    self.append_sensor_value(sensor, value)
                    self.value_labels[sensor].config(
                        text=f"{value:.2f}" if isinstance(value, float) else str(value))
                    self.update_warning_light(sensor)

                self.failure_prob = self.machine_controller.ml_model.predict_failure(
                    self.get_current_sensor_data())
                self.failure_prob_label.config(text=f"{self.failure_prob:.2f}%")

                self.fail_light.itemconfig(
                    self.fail_circle,
                    fill="red" if self.failure_prob > 70 else "gray")

        except Exception as e:
            print(f"Simulation error: {e}")
            traceback.print_exc()

        self.update_status_light()
        self.root.after(1000, self.update_live_data)

    def append_sensor_value(self, sensor, value):
        self.data[sensor].append(value)
        if len(self.data[sensor]) > 20:
            self.data[sensor] = self.data[sensor][-20:]

        line = self.graph_lines[sensor]
        ax = self.axes[sensor]

        line.set_data(range(len(self.data[sensor])), self.data[sensor])
        ax.set_xlim(0, max(20, len(self.data[sensor])))

        y_min = min(self.data[sensor])
        y_max = max(self.data[sensor])
        margin = (y_max - y_min) * 0.1 if y_max != y_min else 1
        ax.set_ylim(y_min - margin, y_max + margin)

        if sensor in self.canvas_widgets:
            self.canvas_widgets[sensor].draw()
        if sensor + '_detail' in self.canvas_widgets:
            self.canvas_widgets[sensor + '_detail'].draw()

    def update_warning_light(self, sensor):
        sensor_obj = self.sensor_objects.get(sensor)
        if not sensor_obj or not hasattr(sensor_obj, 'max_value'):
            return

        current = sensor_obj.get_value()
        threshold = 0.9 * sensor_obj.max_value

        if current >= threshold:
            if not self.warning_blinking[sensor]:
                self.warning_blinking[sensor] = True
                self.toggle_warning_light(sensor)
        else:
            self.warning_blinking[sensor] = False
            self.warning_states[sensor] = False
            canvas, circle = self.warning_lights[sensor]
            canvas.itemconfig(circle, fill="green")

    def toggle_warning_light(self, sensor):
        if not self.warning_blinking[sensor]:
            return

        self.warning_states[sensor] = not self.warning_states[sensor]
        new_color = "red" if self.warning_states[sensor] else "white"
        canvas, circle = self.warning_lights[sensor]
        canvas.itemconfig(circle, fill=new_color)
        self.root.after(500, lambda: self.toggle_warning_light(sensor))

    def open_sensor_detail_view(self, sensor):
        if sensor in self.detail_windows:
            self.detail_windows[sensor].lift()
            return

        window = tk.Toplevel(self.root)
        self.detail_windows[sensor] = window
        window.title(f"Sensor Details: {sensor}")
        window.protocol("WM_DELETE_WINDOW", lambda: self.detail_windows.pop(sensor, None) or window.destroy())

        fig = self.figures[sensor]
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)

    def show_all_plots(self):
        self.clear_graphs()
        for idx, sensor in enumerate(self.sensors):
            row = idx // 2
            col = idx % 2
            canvas = FigureCanvasTkAgg(self.figures[sensor], master=self.scrollable_frame)
            canvas.draw()
            widget = canvas.get_tk_widget()
            widget.grid(row=row, column=col, padx=10, pady=10)
            self.canvas_widgets[sensor] = canvas

    def clear_graphs(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.canvas_widgets.clear()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1135x600")
    root.resizable(False, False)
    app = SensorTogglePanel(root)
    root.mainloop()