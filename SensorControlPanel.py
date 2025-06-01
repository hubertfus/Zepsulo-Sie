import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from sensor_simulator import SensorSimulator
import traceback

class SensorTogglePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Machine panel")

        self.sensors = [
            'footfall', 'tempMode', 'AQ', 'USS',
            'CS', 'VOC', 'RP', 'IP', 'Temperature'
        ]

        self.states = {}
        self.graph_lines = {}
        self.data = {sensor: [] for sensor in self.sensors}
        self.value_labels = {}
        self.machine_running = True  # flaga pracy maszyny

        # === UI ===
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side="left", padx=10, pady=10, anchor="n")

        self.graph_container = tk.Frame(root)
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
            tk.Label(self.control_frame, text=sensor, font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5, sticky="w")

            button = tk.Button(self.control_frame, text="OFF", width=6, bg="red", fg="white",
                               command=lambda s=sensor: self.toggle(s))
            button.grid(row=i, column=1, padx=5, pady=5)

            tk.Button(self.control_frame, text="Wykres", command=lambda s=sensor: self.show_single_plot(s)).grid(row=i, column=2, padx=5, pady=5)

            value_label = tk.Label(self.control_frame, text="—", font=("Arial", 10))
            value_label.grid(row=i, column=3, padx=5, pady=5)
            self.value_labels[sensor] = value_label

            self.states[sensor] = {'value': False, 'button': button}

        # === FAIL LIGHT ===
        tk.Label(self.control_frame, text="fail", font=("Arial", 10)).grid(row=len(self.sensors), column=0, padx=5, pady=5, sticky="w")
        self.fail_value = tk.IntVar(value=0)
        self.fail_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
        self.fail_light.grid(row=len(self.sensors), column=1, padx=5, pady=5)
        self.fail_circle = self.fail_light.create_oval(5, 5, 15, 15, fill="gray")
        self.update_fail_light()

        # === STATUS MASZYNY ===
        tk.Label(self.control_frame, text="Status maszyny", font=("Arial", 10)).grid(row=len(self.sensors)+1, column=0, padx=5, pady=5, sticky="w")
        self.status_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
        self.status_light.grid(row=len(self.sensors)+1, column=1, padx=5, pady=5)
        self.status_circle = self.status_light.create_oval(5, 5, 15, 15, fill="green")

        # === Przyciski ===
        tk.Button(self.control_frame, text="Pokaż wszystkie wykresy", command=self.show_all_plots).grid(row=len(self.sensors)+2, column=0, columnspan=4, pady=5)
        tk.Button(self.control_frame, text="Wyłącz maszynę", command=self.shutdown_machine, bg="black", fg="white").grid(row=len(self.sensors)+3, column=0, columnspan=4, pady=5)
        tk.Button(self.control_frame, text="Włącz maszynę", command=self.start_machine, bg="darkgreen", fg="white").grid(row=len(self.sensors)+4, column=0, columnspan=4, pady=5)

        # === WYKRESY ===
        self.figures = {}
        self.axes = {}
        self.canvas_widgets = {}
        for sensor in self.sensors:
            fig, ax = plt.subplots(figsize=(4, 2.5))
            ax.set_title(sensor)
            ax.grid(True)
            line, = ax.plot([], [])
            self.figures[sensor] = fig
            self.axes[sensor] = ax
            self.graph_lines[sensor] = line

        self.show_all_plots()

        # === SYMULATOR ===
        self.simulator = SensorSimulator('sensor_data.csv')
        self.root.after(1000, self.update_live_data)

    def toggle(self, sensor):
        state = self.states[sensor]['value']
        new_state = not state
        self.states[sensor]['value'] = new_state
        button = self.states[sensor]['button']
        button.config(text="ON" if new_state else "OFF", bg="green" if new_state else "red")

    def set_fail(self, value: int):
        self.fail_value.set(value)
        self.update_fail_light()

    def update_fail_light(self):
        color = "red" if self.fail_value.get() == 1 else "gray"
        self.fail_light.itemconfig(self.fail_circle, fill=color)

    def update_status_light(self):
        color = "green" if self.machine_running else "gray"
        self.status_light.itemconfig(self.status_circle, fill=color)

    def clear_graphs(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

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

    def show_single_plot(self, sensor):
        self.clear_graphs()
        canvas = FigureCanvasTkAgg(self.figures[sensor], master=self.scrollable_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(padx=10, pady=10)

    def update_live_data(self):
        try:
            if self.machine_running:
                row = self.simulator.get_next_reading()
                for sensor in self.sensors:
                    if self.states[sensor]['value']:
                        value = row[sensor]
                        self.append_sensor_value(sensor, value)
                        self.value_labels[sensor].config(text=str(value))
                self.set_fail(int(row['fail']))
            else:
                self.simulate_shutdown_step()
        except Exception as e:
            print(f"Błąd symulacji: {e}")
            traceback.print_exc()
        self.update_status_light()
        self.root.after(1000, self.update_live_data)

    def append_sensor_value(self, sensor, value):
        self.data[sensor].append(value)
        if len(self.data[sensor]) > 20:
            self.data[sensor] = self.data[sensor][-20:]
        line = self.graph_lines[sensor]
        line.set_data(range(len(self.data[sensor])), self.data[sensor])
        self.axes[sensor].set_xlim(0, max(20, len(self.data[sensor])))
        y_min = min(self.data[sensor])
        y_max = max(self.data[sensor])
        margin = (y_max - y_min) * 0.1 if y_max != y_min else 1
        self.axes[sensor].set_ylim(y_min - margin, y_max + margin)
        self.canvas_widgets[sensor].draw()

    def shutdown_machine(self):
        self.machine_running = False
        print("Rozpoczynam wyłączanie maszyny...")

    def start_machine(self):
        self.machine_running = True
        print("Maszyna włączona ponownie")

    def simulate_shutdown_step(self):
        dynamic_sensors = ['USS', 'CS', 'RP', 'IP', 'Temperature']
        all_off = True
        for sensor in self.sensors:
            if self.states[sensor]['value'] and sensor in dynamic_sensors and self.data[sensor]:
                last_value = self.data[sensor][-1]
                new_value = max(0, last_value - (last_value * 0.15))
                if new_value > 0.5:
                    all_off = False
                else:
                    new_value = 0
                self.append_sensor_value(sensor, new_value)
                self.value_labels[sensor].config(text=f"{new_value:.1f}")
        if all_off:
            print("Maszyna całkowicie wyłączona.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1140x600")
    root.resizable(False, False)
    app = SensorTogglePanel(root)
    root.mainloop()
