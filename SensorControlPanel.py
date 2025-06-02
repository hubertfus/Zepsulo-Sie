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

        self.data = {sensor: [] for sensor in self.sensors}
        self.value_labels = {}
        self.figures = {}
        self.axes = {}
        self.graph_lines = {}
        self.canvas_widgets = {}
        self.warning_lights = {}
        self.warning_states = {}
        self.warning_blinking = {}
        self.machine_running = False
        self.detail_windows = {}

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
            value_label = tk.Label(self.control_frame, text="—", font=("Arial", 10))
            value_label.grid(row=i, column=1, padx=5, pady=5)
            self.value_labels[sensor] = value_label
            tk.Button(self.control_frame, text="Szczegóły", command=lambda s=sensor: self.open_sensor_detail_view(s)).grid(row=i, column=2, padx=5, pady=5)

            warning_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
            warning_light.grid(row=i, column=3, padx=5, pady=5)
            warning_circle = warning_light.create_oval(5, 5, 15, 15, fill="green")
            self.warning_lights[sensor] = (warning_light, warning_circle)
            self.warning_states[sensor] = False
            self.warning_blinking[sensor] = False

        tk.Label(self.control_frame, text="fail", font=("Arial", 10)).grid(row=len(self.sensors), column=0, padx=5, pady=5, sticky="w")
        self.fail_value = tk.IntVar(value=0)
        self.fail_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
        self.fail_light.grid(row=len(self.sensors), column=1, padx=5, pady=5)
        self.fail_circle = self.fail_light.create_oval(5, 5, 15, 15, fill="gray")
        self.update_fail_light()

        tk.Label(self.control_frame, text="Status maszyny", font=("Arial", 10)).grid(row=len(self.sensors)+1, column=0, padx=5, pady=5, sticky="w")
        self.status_light = tk.Canvas(self.control_frame, width=20, height=20, bg="white", highlightthickness=0)
        self.status_light.grid(row=len(self.sensors)+1, column=1, padx=5, pady=5)
        self.status_circle = self.status_light.create_oval(5, 5, 15, 15, fill="green")

        tk.Button(self.control_frame, text="Pokaż wszystkie wykresy", command=self.show_all_plots).grid(row=len(self.sensors)+2, column=0, columnspan=3, pady=5)

        self.toggle_button = tk.Button(self.control_frame, text="Włącz maszynę", command=self.toggle_machine, bg="green", fg="white")
        self.toggle_button.grid(row=len(self.sensors)+3, column=0, columnspan=3, pady=5)

        for sensor in self.sensors:
            fig, ax = plt.subplots(figsize=(4, 2.5))
            ax.set_title(sensor)
            ax.grid(True)
            line, = ax.plot([], [])
            self.figures[sensor] = fig
            self.axes[sensor] = ax
            self.graph_lines[sensor] = line

        self.show_all_plots()
        self.simulator = SensorSimulator('sensor_data.csv')
        self.sensor_objects = self.simulator.sensors
        self.root.after(300, self.update_live_data)

    def open_sensor_detail_view(self, sensor):
        if sensor in self.detail_windows:
            self.detail_windows[sensor].lift()
            return

        window = tk.Toplevel(self.root)
        self.detail_windows[sensor] = window
        window.title(f"Szczegóły: {sensor}")
        window.protocol("WM_DELETE_WINDOW", lambda: self.detail_windows.pop(sensor, None) or window.destroy())

        fig = self.figures[sensor]
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(padx=10, pady=10)
        self.canvas_widgets[sensor + '_detail'] = canvas

        sensor_obj = self.sensor_objects.get(sensor)
        if hasattr(sensor_obj, 'min_value') and hasattr(sensor_obj, 'max_value'):
            min_var = tk.DoubleVar(value=sensor_obj.min_value)
            max_var = tk.DoubleVar(value=sensor_obj.max_value)

            frame = tk.Frame(window)
            frame.pack(pady=10)

            tk.Label(frame, text="Min:").grid(row=0, column=0, sticky="e")
            tk.Entry(frame, textvariable=min_var, width=10).grid(row=0, column=1)
            tk.Label(frame, text="Max:").grid(row=1, column=0, sticky="e")
            tk.Entry(frame, textvariable=max_var, width=10).grid(row=1, column=1)

            def save_changes():
                sensor_obj.min_value = min_var.get()
                sensor_obj.max_value = max_var.get()
                window.destroy()
                self.detail_windows.pop(sensor, None)

            tk.Button(window, text="Zapisz", command=save_changes).pack(pady=5)

    def toggle_machine(self):
        self.machine_running = not self.machine_running
        self.update_status_light()
        if self.machine_running:
            self.toggle_button.config(text="Wyłącz maszynę", bg="black", fg="white")
        else:
            self.toggle_button.config(text="Włącz maszynę", bg="darkgreen", fg="white")

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
        self.canvas_widgets.clear()

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
        self.canvas_widgets[sensor] = canvas

    def update_live_data(self):
        try:
            if self.machine_running:
                row = self.simulator.get_next_reading()
                for sensor in self.sensors:
                    value = row[sensor]
                    self.append_sensor_value(sensor, value)
                    self.value_labels[sensor].config(text=f"{value:.2f}" if isinstance(value, float) else str(value))
                    self.update_warning_light(sensor)
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

    def simulate_shutdown_step(self):
        dynamic_sensors = ['USS', 'CS', 'RP', 'IP', 'Temperature']
        all_off = True

        for sensor in dynamic_sensors:
            if sensor in self.sensor_objects:
                obj = self.sensor_objects[sensor]
                prev = obj.get_value()
                obj.simulate_shutdown()
                new = obj.get_value()

                self.append_sensor_value(sensor, new)
                self.value_labels[sensor].config(text=f"{new:.1f}")
                self.update_warning_light(sensor)

                if new > (obj.min_value or 0) + 0.5:
                    all_off = False

        if all_off:
            print("Maszyna całkowicie wyłączona.")

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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1135x600")
    root.resizable(False, False)
    app = SensorTogglePanel(root)
    root.mainloop()
