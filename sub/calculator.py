
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import numpy as np
import json

class SubwooferDesignTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Subwoofer Design Tool")

        # T/S Parameter Inputs
        self.create_widgets()

    def create_widgets(self):
        # Create input fields
        tk.Label(self.master, text="Fs (Hz):").grid(row=0, column=0)
        self.fs_entry = tk.Entry(self.master)
        self.fs_entry.grid(row=0, column=1)

        tk.Label(self.master, text="Qts:").grid(row=1, column=0)
        self.qts_entry = tk.Entry(self.master)
        self.qts_entry.grid(row=1, column=1)

        tk.Label(self.master, text="Vas (liters):").grid(row=2, column=0)
        self.vas_entry = tk.Entry(self.master)
        self.vas_entry.grid(row=2, column=1)

        tk.Label(self.master, text="Xmax (mm):").grid(row=3, column=0)
        self.xmax_entry = tk.Entry(self.master)
        self.xmax_entry.grid(row=3, column=1)

        self.enclosure_type_var = tk.StringVar(value="sealed")
        tk.Radiobutton(self.master, text="Sealed", variable=self.enclosure_type_var, value="sealed").grid(row=4, column=0)
        tk.Radiobutton(self.master, text="Ported", variable=self.enclosure_type_var, value="ported").grid(row=4, column=1)

        tk.Label(self.master, text="Desired Tuning Frequency (Fb, Hz):").grid(row=5, column=0)
        self.fb_entry = tk.Entry(self.master)
        self.fb_entry.grid(row=5, column=1)

        tk.Label(self.master, text="Port Diameter (cm):").grid(row=6, column=0)
        self.dv_entry = tk.Entry(self.master)
        self.dv_entry.grid(row=6, column=1)

        tk.Button(self.master, text="Calculate", command=self.calculate).grid(row=7, column=0)
        tk.Button(self.master, text="Save Design", command=self.save_design).grid(row=7, column=1)
        tk.Button(self.master, text="Load Design", command=self.load_design).grid(row=8, column=0)
        tk.Button(self.master, text="Clear", command=self.clear_fields).grid(row=8, column=1)

        self.result_text = tk.Text(self.master, width=50, height=10)
        self.result_text.grid(row=9, column=0, columnspan=2)

        # Tooltips
        self.create_tooltips()

    def create_tooltips(self):
        tooltips = {
            self.fs_entry: "Resonant frequency (Fs) of the driver in Hz.",
            self.qts_entry: "Total Q factor of the driver.",
            self.vas_entry: "Equivalent volume of air (Vas) in liters.",
            self.xmax_entry: "Maximum linear excursion (Xmax) of the driver in mm.",
            self.fb_entry: "Desired tuning frequency (Fb) in Hz for ported enclosure.",
            self.dv_entry: "Diameter of the port in cm for ported enclosure."
        }
        for widget, tip in tooltips.items():
            widget.bind("<Enter>", lambda e, tip=tip: self.show_tooltip(e, tip))
            widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event, tooltip_text):
        self.tooltip = tk.Toplevel(self.master)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = tk.Label(self.tooltip, text=tooltip_text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def input_validation(self):
        try:
            fs = float(self.fs_entry.get())
            qts = float(self.qts_entry.get())
            vas = float(self.vas_entry.get())
            xmax = float(self.xmax_entry.get())
            fb = float(self.fb_entry.get()) if self.enclosure_type_var.get() == "ported" else None
            dv = float(self.dv_entry.get()) if self.enclosure_type_var.get() == "ported" else None

            if fs <= 0 or qts <= 0 or vas <= 0 or xmax < 0 or (fb and fb <= 0) or (dv and dv <= 0):
                raise ValueError

            return fs, qts, vas, xmax, fb, dv
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numbers.")
            return None

    def calculate(self):
        params = self.input_validation()
        if not params:
            return

        fs, qts, vas, xmax, fb, dv = params

        if self.enclosure_type_var.get() == "sealed":
            vb = self.calculate_box_volume(qts, vas)
            result = f"Recommended Sealed Box Volume: {vb:.2f} liters\n"
            result += "Frequency Response:\n"
            self.plot_frequency_response(vb, fs)
        else:
            vb = self.calculate_box_volume(qts, vas)
            lv = self.calculate_port_dimensions(vb, fb, dv / 100)  # Convert diameter from cm to meters
            result = f"Recommended Port Length: {lv:.2f} m\n"
            result += f"Recommended Box Volume: {vb:.2f} liters\n"
            result += "Frequency Response:\n"
            self.plot_frequency_response(vb, fs, fb, dv / 100)  # Convert diameter from cm to meters

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def calculate_box_volume(self, qts, vas):
        qtc = 0.707  # target Q value
        vb = vas * (qts ** 2 / (qtc ** 2 - qts ** 2))
        return vb

    def calculate_port_dimensions(self, vb, fb, d_v):
        lv = (2352 * d_v ** 2) / (vb * fb ** 2) - 0.823 * d_v
        return lv

    def plot_frequency_response(self, vb, fs, fb=None, dv=None):
        # Generate frequency response curve for illustration
        frequencies = np.linspace(10, 200, 500)  # from 10Hz to 200Hz
        response = 20 * np.log10((fs ** 2) / (frequencies ** 2))  # Simplified model

        plt.figure()
        plt.plot(frequencies, response, label='Frequency Response', color='blue')
        plt.title('Frequency Response')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Response (dB)')
        plt.grid()
        plt.axvline(x=fs, color='red', linestyle='--', label='Fs')
        if fb:
            plt.axvline(x=fb, color='green', linestyle='--', label='Fb')
        plt.legend()
        plt.show()

    def save_design(self):
        design = {
            'Fs': float(self.fs_entry.get()),
            'Qts': float(self.qts_entry.get()),
            'Vas': float(self.vas_entry.get()),
            'Xmax': float(self.xmax_entry.get()),
            'Enclosure Type': self.enclosure_type_var.get(),
            'Fb': float(self.fb_entry.get()) if self.enclosure_type_var.get() == "ported" else None,
            'Port Diameter': float(self.dv_entry.get()) if self.enclosure_type_var.get() == "ported" else None,
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(design, f)
                messagebox.showinfo("Success", "Design saved successfully!")

    def load_design(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                try:
                    design = json.load(f)
                    self.fs_entry.delete(0, tk.END)
                    self.fs_entry.insert(0, design['Fs'])
                    self.qts_entry.delete(0, tk.END)
                    self.qts_entry.insert(0, design['Qts'])
                    self.vas_entry.delete(0, tk.END)
                    self.vas_entry.insert(0, design['Vas'])
                    self.xmax_entry.delete(0, tk.END)
                    self.xmax_entry.insert(0, design['Xmax'])
                    
                    self.enclosure_type_var.set(design['Enclosure Type'])
                    if design['Enclosure Type'] == "ported":
                        self.fb_entry.delete(0, tk.END)
                        self.fb_entry.insert(0, design['Fb'])
                        self.dv_entry.delete(0, tk.END)
                        self.dv_entry.insert(0, design['Port Diameter'])
                    else:
                        self.fb_entry.delete(0, tk.END)
                        self.dv_entry.delete(0, tk.END)
                except (KeyError, ValueError) as e:
                    messagebox.showerror("File Error", "Invalid design file format.")

    def clear_fields(self):
        self.fs_entry.delete(0, tk.END)
        self.qts_entry.delete(0, tk.END)
        self.vas_entry.delete(0, tk.END)
        self.xmax_entry.delete(0, tk.END)
        self.fb_entry.delete(0, tk.END)
        self.dv_entry.delete(0, tk.END)
        self.enclosure_type_var.set("sealed")
        self.result_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SubwooferDesignTool(root)
    root.mainloop()

