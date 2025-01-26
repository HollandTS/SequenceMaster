import tkinter as tk
from tkinter import scrolledtext, messagebox
from ini_processor import process_ini_data
import os

# List of keys to be removed when TS is checked
TS_KEYS = [
    "SecondaryFire", "SecondaryProne", "Deploy", "Deployed", "DeployedFire", 
    "DeployedIdle", "Undeploy", "Paradrop", "Cheer", "Panic", "Shovel", "Carry", 
    "AirDeathStart", "AirDeathFalling", "AirDeathFinish", "Tread", "Swim", 
    "WetAttack", "WetIdle1", "WetIdle2", "WetDie1", "WetDie2"
]

def create_ui():
    def process_input_text(input_text):
        if not input_text:
            messagebox.showwarning("Input Error", "Please paste INI data before processing.")
            return
        output_text, added_keys = process_ini_data(input_text)
        if ts_var.get():
            output_text = remove_ts_keys(output_text)
        output_text_box.delete("1.0", tk.END)
        output_text_box.insert(tk.END, output_text)
        highlight_added_keys(added_keys)

    def remove_ts_keys(text):
        lines = text.split('\n')
        filtered_lines = [line for line in lines if not any(line.startswith(key) for key in TS_KEYS)]
        return '\n'.join(filtered_lines)

    def highlight_added_keys(added_keys):
        output_text_box.tag_remove("underlined", "1.0", tk.END)
        for key in added_keys:
            start = output_text_box.search(key, "1.0", stopindex=tk.END)
            while start:
                end = f"{start}+{len(key)}c"
                output_text_box.tag_add("underlined", start, end)
                start = output_text_box.search(key, end, stopindex=tk.END)
        output_text_box.tag_config("underlined", underline=True)

    def on_input_change(event):
        input_text = input_text_box.get("1.0", tk.END).strip()
        # Check if there is a new entry with at least two values
        if '=' in input_text:
            lines = input_text.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    if ',' in value:
                        process_input_text(input_text)
                        break

    def on_ts_check():
        input_text = input_text_box.get("1.0", tk.END).strip()
        process_input_text(input_text)

    def open_help():
        try:
            with open("help.txt", "r") as help_file:
                help_text = help_file.read()
                show_help_dialog(help_text)
        except FileNotFoundError:
            messagebox.showerror("Error", "help.txt file not found.")

    def show_help_dialog(help_text):
        help_window = tk.Toplevel(window)
        help_window.title("Help")

        help_text_box = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, width=80, height=20)
        help_text_box.pack(expand=True, fill='both')
        help_text_box.insert(tk.END, help_text)
        help_text_box.config(state=tk.DISABLED)  # Make the text box read-only

    window = tk.Tk()
    window.title("Infantry Sequence Helper")
    window.geometry('800x522')  # Reduce the height by 13%

    # Help Button
    help_button = tk.Button(window, text="Help", command=open_help)
    help_button.pack(side=tk.LEFT, padx=5, pady=5)

    # TS Checkbox
    ts_var = tk.BooleanVar()
    ts_checkbox = tk.Checkbutton(window, text="TS", variable=ts_var, command=on_ts_check)
    ts_checkbox.pack(pady=5)

    # Frame to hold both sections
    frame = tk.Frame(window)
    frame.pack(expand=True, fill='both', padx=5, pady=5)

    # Left Frame for the input
    left_frame = tk.Frame(frame)
    left_frame.pack(side="left", expand=True, fill='both', padx=5, pady=5)

    # Right Frame for the output
    right_frame = tk.Frame(frame)
    right_frame.pack(side="right", expand=True, fill='both', padx=5, pady=5)

    # Input section: Text Box (on the left side)
    input_text_box_label = tk.Label(left_frame, text="Enter Infantry Sequence INI here:")
    input_text_box_label.pack()

    input_text_box = scrolledtext.ScrolledText(left_frame, width=28, height=43)  # Adjusted height
    input_text_box.pack()
    input_text_box.bind('<KeyRelease>', on_input_change)  # Bind the KeyRelease event to detect changes

    # Output section: Text Box (on the right side)
    output_text_box_label = tk.Label(right_frame, text="Processed output:")
    output_text_box_label.pack()

    output_text_box = scrolledtext.ScrolledText(right_frame, width=28, height=43)  # Adjusted height
    output_text_box.pack()

    # Note text
    note_label = tk.Label(window, text="* Underlined means automatically assigned")
    note_label.pack(pady=5)
    note_label_underline = tk.Label(window, text="Underlined", font=("Arial", 10, "underline"))
    note_label_underline.pack(pady=5)

    window.mainloop()

# Run the UI
if __name__ == "__main__":
    create_ui()