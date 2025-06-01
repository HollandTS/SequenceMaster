import tkinter as tk
from PIL import ImageTk

def open_settings_popup(master, images, mode_callback=None):
    popup = tk.Toplevel(master)
    popup.title("Settings")
    popup.grab_set()
    idx = [0]
    selected_rgb = [None]
    shadows_included_var = tk.BooleanVar(value=True)
    mode_popup_var = tk.StringVar(value="")

    def show_image():
        pil_img = images[idx[0]]
        img = ImageTk.PhotoImage(pil_img)
        image_label.config(image=img)
        image_label.image = img
        frame_label.config(text=f"Frame {idx[0]+1} / {len(images)}")
        color_label.config(text="Click image to pick the transparency color")

    def on_click(event):
        pil_img = images[idx[0]]
        x = min(max(event.x, 0), pil_img.width - 1)
        y = min(max(event.y, 0), pil_img.height - 1)
        rgb = pil_img.getpixel((x, y))[:3]
        selected_rgb[0] = rgb
        color_label.config(text=f"Selected color: {rgb}")

    def prev_frame():
        if idx[0] > 0:
            idx[0] -= 1
            show_image()

    def next_frame():
        if idx[0] < len(images) - 1:
            idx[0] += 1
            show_image()

    def on_ok():
        if not mode_popup_var.get():
            tk.messagebox.showwarning("Select Mode", "Pick infantry or vehicle")
            return
        popup.grab_release()
        popup.destroy()
        if mode_callback:
            mode_callback(mode_popup_var.get())
        master.after(10, lambda: callback(selected_rgb[0], mode_popup_var.get(), shadows_included_var.get()))

    def on_skip():
        popup.grab_release()
        popup.destroy()
        master.after(10, lambda: callback(None, mode_popup_var.get(), shadows_included_var.get()))

    def callback(rgb, mode, shadows_included):
        # This function can be used by the caller to get the results
        pass

    frame_label = tk.Label(popup, text="Frame 1")
    frame_label.pack(pady=5)
    image_label = tk.Label(popup)
    image_label.pack(padx=10, pady=10)
    image_label.bind("<Button-1>", on_click)
    color_label = tk.Label(popup, text="Click image to pick color")
    color_label.pack(pady=5)
    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=5)
    prev_btn = tk.Button(btn_frame, text="< Prev", command=prev_frame)
    prev_btn.grid(row=0, column=0, padx=5)
    next_btn = tk.Button(btn_frame, text="Next >", command=next_frame)
    next_btn.grid(row=0, column=1, padx=5)
    shadows_checkbox = tk.Checkbutton(popup, text="Shadows Included", variable=shadows_included_var)
    shadows_checkbox.pack(pady=(5, 0))
    mode_frame = tk.Frame(popup)
    mode_frame.pack(pady=5)
    tk.Label(mode_frame, text="Mode:").pack(side="left")
    tk.Radiobutton(mode_frame, text="Infantry", variable=mode_popup_var, value="Infantry").pack(side="left", padx=5)
    tk.Radiobutton(mode_frame, text="Vehicle", variable=mode_popup_var, value="Vehicle").pack(side="left", padx=5)

    # Facings selector
    facings_frame = tk.Frame(popup)
    facings_frame.pack(pady=5)
    tk.Label(facings_frame, text="Facings:").pack(side="left")
    facings_values = [8, 16, 32, 64]
    facings_var = tk.IntVar(value=8)
    def decrease_facings():
        idx = facings_values.index(facings_var.get())
        if idx > 0:
            facings_var.set(facings_values[idx-1])
    def increase_facings():
        idx = facings_values.index(facings_var.get())
        if idx < len(facings_values)-1:
            facings_var.set(facings_values[idx+1])
    tk.Button(facings_frame, text="<-", width=2, command=decrease_facings).pack(side="left")
    facings_label = tk.Label(facings_frame, textvariable=facings_var, width=3)
    facings_label.pack(side="left")
    tk.Button(facings_frame, text="->", width=2, command=increase_facings).pack(side="left")

    # Sequence input
    seq_label = tk.Label(popup, text="Enter sequence here:")
    seq_label.pack(pady=(10,0))
    sequence_text = tk.Text(popup, width=50, height=6)
    sequence_text.pack(padx=10, pady=(0,10))

    ok_btn = tk.Button(popup, text="OK", command=on_ok)
    ok_btn.pack(side="left", padx=20, pady=10)
    skip_btn = tk.Button(popup, text="Skip", command=on_skip)
    skip_btn.pack(side="right", padx=20, pady=10)
    show_image()
    popup.wait_window() 