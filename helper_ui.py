from tkinter import scrolledtext, messagebox, ttk
import tkinter as tk
from ini_processor import process_ini_data

TS_KEYS = [
    "SecondaryFire", "SecondaryProne", "Deploy", "Deployed", "DeployedFire", "DeployedIdle", "Undeploy", "Paradrop", "Cheer", "Panic", "Shovel", "Carry", 
    "AirDeathStart", "AirDeathFalling", "AirDeathFinish", "Tread", "Swim", 
    "WetAttack", "WetIdle1", "WetIdle2", "WetDie1", "WetDie2"
]

def open_inf_sequence_helper(parent_window):
    helper_win = tk.Toplevel(parent_window)
    helper_win.title("Inf Sequence Helper")
    helper_win.geometry('900x400')
    helper_group = ttk.LabelFrame(helper_win, text="Infantry Sequence Helper")
    helper_group.pack(fill='both', expand=True, padx=10, pady=10)

    ts_var = tk.BooleanVar()
    def on_ts_check():
        input_text = input_text_box.get("1.0", tk.END).strip()
        process_input_text(input_text)
    ts_checkbox = tk.Checkbutton(helper_group, text="TS", variable=ts_var, command=on_ts_check)
    ts_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    def show_help_dialog(help_text):
        help_window = tk.Toplevel(helper_win)
        help_window.title("Help")
        help_text_box = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, width=80, height=20)
        help_text_box.pack(expand=True, fill='both')
        help_text_box.insert(tk.END, help_text)
        help_text_box.config(state=tk.DISABLED)
    def open_help():
        try:
            with open("help.txt", "r") as help_file:
                help_text = help_file.read()
                show_help_dialog(help_text)
        except FileNotFoundError:
            messagebox.showerror("Error", "help.txt file not found.")
    help_button = tk.Button(helper_group, text="Help", command=open_help)
    help_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    input_text_box_label = tk.Label(helper_group, text="Enter Infantry Sequence INI here:")
    input_text_box_label.grid(row=1, column=0, sticky="w")
    output_text_box_label = tk.Label(helper_group, text="Processed output:")
    output_text_box_label.grid(row=1, column=1, sticky="w")
    input_text_box = scrolledtext.ScrolledText(helper_group, width=50, height=10)
    input_text_box.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
    output_text_box = scrolledtext.ScrolledText(helper_group, width=50, height=10)
    output_text_box.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    helper_group.columnconfigure(0, weight=1)
    helper_group.columnconfigure(1, weight=1)

    def process_input_text(input_text):
        if not input_text:
            output_text_box.delete("1.0", tk.END)
            return
        output_text, added_keys = process_ini_data(input_text)
        if ts_var.get():
            lines = output_text.split('\n')
            filtered_lines = [line for line in lines if not any(line.startswith(key) for key in TS_KEYS)]
            output_text = '\n'.join(filtered_lines)
        output_text_box.delete("1.0", tk.END)
        output_text_box.insert(tk.END, output_text)
    def on_input_change(event):
        input_text = input_text_box.get("1.0", tk.END).strip()
        process_input_text(input_text)
    input_text_box.bind('<KeyRelease>', on_input_change) 