from tkinter import scrolledtext, messagebox, filedialog, ttk
import tkinter as tk
import time
from PIL import Image, ImageTk, ImageSequence
import os
from ini_processor import process_ini_data, parse_ini_data, build_frame_grid
from helper_ui import open_inf_sequence_helper
from settings_ui import open_settings_popup
from frame_viewer import FrameLoader, display_frames
from frame_selector import FrameSelector

TS_KEYS = [
    "SecondaryFire", "SecondaryProne", "Deploy", "Deployed", "DeployedFire", "DeployedIdle", "Undeploy", "Paradrop", "Cheer", "Panic", "Shovel", "Carry", 
    "AirDeathStart", "AirDeathFalling", "AirDeathFinish", "Tread", "Swim", 
    "WetAttack", "WetIdle1", "WetIdle2", "WetDie1", "WetDie2"
]

# Add a simple loading popup for frame updates
class FrameLoadingPopup:
    def __init__(self, master, message="Loading frames..."):
        self.top = tk.Toplevel(master)
        self.top.title("Loading")
        self.top.geometry("300x80")
        self.label = tk.Label(self.top, text=message, font=("Arial", 12))
        self.label.pack(expand=True, fill="both", pady=20)
        self.top.update()
    def set_message(self, message):
        self.label.config(text=message)
        self.top.update()
    def close(self):
        self.top.destroy()

# Persistent settings storage
settings_state = {
    'mode': '',  # No default, user must choose
    'facings': 8,
    'transparency_color': None
}

def create_ui():
    window = tk.Tk()
    window.title("Infantry Sequence Helper")
    window.geometry('1100x800')

    # --- Frames Group ---
    frames_group = ttk.LabelFrame(window, text="Frames")
    frames_group.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    window.grid_rowconfigure(1, weight=1)

    loaded_filepaths = []
    frame_loader = FrameLoader()
    mode_var = tk.StringVar(value="")

    # --- Insert after window = tk.Tk() ---
    menubar = tk.Menu(window)
    menubar.add_command(label="Inf Sequence Helper", command=lambda: open_inf_sequence_helper(window))
    window.config(menu=menubar)

    # --- Main window Sequence group as converter ---
    sequence_group = ttk.LabelFrame(window, text="Sequence")
    sequence_group.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    # Disabled mode radio buttons
    infantry_radio = tk.Radiobutton(sequence_group, text="Infantry", variable=mode_var, value="Infantry", state='disabled')
    infantry_radio.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    vehicle_radio = tk.Radiobutton(sequence_group, text="Vehicle", variable=mode_var, value="Vehicle", state='disabled')
    vehicle_radio.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    input_text_box_label = tk.Label(sequence_group, text="Input sequence")
    input_text_box_label.grid(row=1, column=0, sticky="w")
    input_text_box = scrolledtext.ScrolledText(sequence_group, width=50, height=10)
    input_text_box.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
    input_text_box.config(state='normal')  # Make editable

    # Reload button
    def reload_sequence():
        seq = input_text_box.get('1.0', tk.END).strip()
        facings = settings_state.get('facings', 8)
        update_sequence_boxes(seq, facings)

    reload_btn = tk.Button(sequence_group, text="Reload", command=reload_sequence)
    reload_btn.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # --- Convert group ---
    convert_group = ttk.LabelFrame(window, text="Convert")
    convert_group.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    window.grid_columnconfigure(1, weight=0)

    # Convert button
    def convert_action():
        mode = mode_var.get() or settings_state.get('mode', 'Infantry')
        seq = input_text_box.get('1.0', tk.END).strip()
        has_shadow = frame_loader.has_shadow_frames
        shadow_offset = frame_loader.shadow_offset
        # Use PIL.Image objects, not ImageTk.PhotoImage
        if has_shadow and shadow_offset is not None:
            frames = frame_loader.original_images[:shadow_offset]
            shadows = frame_loader.original_images[shadow_offset:]
        else:
            frames = frame_loader.original_images[:]
            shadows = None
        import convert
        if mode == 'Infantry':
            new_ini, new_frames, new_shadows = convert.convert_infantry_to_vehicle(seq, frames, shadows)
        else:
            new_ini, new_frames, new_shadows = convert.convert_vehicle_to_infantry(seq, frames, shadows)
        # Replace input sequence with new INI
        input_text_box.delete('1.0', tk.END)
        input_text_box.insert(tk.END, new_ini)
        # Rebuild frame_loader.frames and .original_images in new order
        from PIL import ImageTk
        def rebuild_frames(new_frames, new_shadows):
            all_imgs = new_frames[:]
            if new_shadows:
                all_imgs += new_shadows
            frame_loader.original_images = all_imgs
            frame_loader.frames = [(f"{i:04d}.png", ImageTk.PhotoImage(img)) for i, img in enumerate(all_imgs)]
            frame_loader.cropped_images = list(all_imgs)
            n_main = len(new_frames)
            n_shadow = len(new_shadows) if new_shadows else 0
            if n_shadow > 0:
                frame_loader.has_shadow_frames = True
                frame_loader.shadow_offset = n_main
            else:
                frame_loader.has_shadow_frames = False
                frame_loader.shadow_offset = None
        rebuild_frames(new_frames, new_shadows)
        # Reapply transparency color if set
        if settings_state.get('transparency_color') is not None:
            frame_loader.set_transparency(settings_state['transparency_color'])
        # Switch mode after conversion
        if mode == 'Infantry':
            mode_var.set('Vehicle')
        else:
            mode_var.set('Infantry')
        # Update display
        facings = settings_state.get('facings', 8)
        update_sequence_boxes(new_ini, facings)
        # Always update processed output with new INI and commented old INI
        commented_old = convert.comment_out_ini(seq)
        output_text_box.config(state='normal')
        output_text_box.delete('1.0', tk.END)
        output_text_box.insert(tk.END, new_ini + '\n\n' + commented_old)
        output_text_box.config(state='disabled')

    convert_btn = tk.Button(convert_group, text="Convert to vehicle/Infantry", command=convert_action)
    convert_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    # Cut Turret checkbox
    cut_turret_var = tk.BooleanVar(value=False)
    cut_turret_checkbox = tk.Checkbutton(convert_group, text="Paste Turret on Walk frames (WIP)", variable=cut_turret_var)
    cut_turret_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    def update_cut_turret_state(*args):
        mode = mode_var.get() or settings_state.get('mode', 'Infantry')
        if mode == 'Infantry':
            cut_turret_checkbox.config(state='disabled')
        else:
            cut_turret_checkbox.config(state='normal')
    mode_var.trace_add('write', update_cut_turret_state)
    update_cut_turret_state()

    # Processed output textbox
    output_text_box_label = tk.Label(convert_group, text="Processed output:")
    output_text_box_label.grid(row=1, column=0, sticky="w")
    output_text_box = scrolledtext.ScrolledText(convert_group, width=50, height=10)
    output_text_box.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    output_text_box.config(state='disabled')

    # --- Frames group continued ---
    transparency_color_box = tk.Label(frames_group, text='', width=2, height=1, relief='solid', bd=1)
    transparency_color_box.grid(row=0, column=5, padx=(10,2), pady=5)

    # --- Add a green loading bar ---
    progress_var = tk.DoubleVar(value=0)
    progress_bar = ttk.Progressbar(frames_group, variable=progress_var, maximum=100, mode='determinate', length=300)
    progress_bar.grid(row=0, column=8, padx=10, pady=5, sticky='ew')
    progress_bar.grid_remove()  # Hide by default

    def show_loading_bar():
        progress_var.set(0)
        progress_bar.grid()
        progress_bar.update()

    def hide_loading_bar():
        progress_bar.grid_remove()
        progress_bar.update()

    def update_loading_bar(percent):
        progress_var.set(percent)
        progress_bar.update()

    # Function to update the color box in the main UI
    def update_main_transparency_color_box():
        rgb = settings_state['transparency_color']
        if rgb:
            hex_color = '#%02x%02x%02x' % rgb
            transparency_color_box.config(bg=hex_color)
        else:
            transparency_color_box.config(bg='SystemButtonFace')

    # --- Frame viewer display (final simple version) ---
    def clear_frames_inner():
        for widget in frames_inner.winfo_children():
            widget.destroy()

    # Add a label for swap instructions next to Add Files
    swap_instruction_var = tk.StringVar(value="")
    swap_instruction_label = tk.Label(frames_group, textvariable=swap_instruction_var, fg="blue", font=("Arial", 10, "bold"))
    swap_instruction_label.grid(row=0, column=7, sticky="nw", padx=5, pady=5)

    # Persistent dict to track original frame names for tooltips
    frame_original_names = {}

    # Tooltip logic
    tooltip = None
    def show_tooltip(event, text):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
        x = event.x_root + 10
        y = event.y_root + 10
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack(ipadx=1)
    def hide_tooltip(event=None):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None

    def show_animations_simple(frames_grid):
        clear_frames_inner()
        if not frames_grid or frame_loader.count() == 0:
            tk.Label(frames_inner, text="No frames loaded.").pack(padx=10, pady=10)
            return
        thumb_refs = []  # Prevent garbage collection
        DIE_KEYS = {f"Die{i}" for i in range(1, 6)}
        IDLE_KEYS = {"Idle1", "Idle2"}
        SPECIAL_KEYS = DIE_KEYS | IDLE_KEYS | {"Struggle"}
        VEHICLE_DEATH_IDLE = {"DeathFrames", "IdleFrames"}
        mode = mode_var.get() or settings_state.get('mode', 'Infantry')
        if mode == 'Vehicle':
            DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        else:
            DIRS = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
        frame_labels = []
        for anim, directions_dict in frames_grid.items():
            tk.Label(frames_inner, text=f"{anim}:", font=("Arial", 11, "bold"), anchor="w").pack(anchor="w", pady=(4,1))
            is_special = anim in SPECIAL_KEYS or anim in VEHICLE_DEATH_IDLE
            # Calculate per-direction frame counts
            dir_frame_counts = [len(frames) for frames in directions_dict.values() if len(frames) > 0]
            all_dirs_same = len(dir_frame_counts) > 0 and all(n == dir_frame_counts[0] for n in dir_frame_counts)
            frame_count = dir_frame_counts[0] if all_dirs_same else 0
            # Calculate total unique frames for this animation
            all_frame_indices = []
            for frame_indices in directions_dict.values():
                all_frame_indices.extend(frame_indices)
            unique_frame_indices = list(dict.fromkeys(all_frame_indices))  # preserve order, remove duplicates

            if is_special or (all_dirs_same and 1 <= frame_count <= 4):
                # Show all directions and their frames in a single row, with direction labels inline
                row_frame = tk.Frame(frames_inner)
                row_frame.pack(anchor="w", pady=0)
                for dir_name in DIRS:
                    frame_indices = directions_dict.get(dir_name, [])
                    if not frame_indices:
                        continue
                    tk.Label(row_frame, text=f"{dir_name}", padx=2).pack(side="left")
                    for frame_idx in frame_indices:
                        frame = frame_loader.get_frame(frame_idx)
                        if frame:
                            fname, img = frame
                            thumb_refs.append(img)
                            lbl = tk.Label(row_frame, image=img, borderwidth=0, width=img.width(), height=img.height(), padx=0, pady=0)
                            lbl.pack(side="left", padx=0, pady=0)
                            if frame_idx not in frame_original_names:
                                frame_original_names[frame_idx] = fname
                            def make_tooltip(idx=frame_idx, name=fname):
                                def on_enter(event):
                                    prev = frame_original_names.get(idx, name)
                                    text = f"{name}"
                                    if prev != name:
                                        text += f"\nwas {prev}"
                                    show_tooltip(event, text)
                                return on_enter
                            lbl.bind("<Enter>", make_tooltip())
                            lbl.bind("<Leave>", hide_tooltip)
                            lbl.bind("<Button-1>", lambda e, idx=frame_idx: selector.on_left_click(idx))
                            lbl.bind("<Button-3>", lambda e, idx=frame_idx: selector.on_right_click(e, idx))
                            frame_labels.append((lbl, frame_idx))
                        else:
                            tk.Label(row_frame, text="", width=4, height=2, borderwidth=0, padx=0, pady=0).pack(side="left", padx=0, pady=0)
                # Add a little space at the end
                tk.Label(row_frame, text="").pack(side="left", padx=4)
            else:
                # Always use per-direction grid for other cases
                grid_frame = tk.Frame(frames_inner)
                grid_frame.pack(anchor="w", pady=0)
                for row, dir_name in enumerate(DIRS):
                    frame_indices = directions_dict.get(dir_name, [])
                    if not frame_indices:
                        continue
                    tk.Label(grid_frame, text=dir_name, width=4, anchor="w", borderwidth=0, padx=0, pady=0).grid(row=row, column=0, padx=0, pady=0)
                    for col, frame_idx in enumerate(frame_indices):
                        frame = frame_loader.get_frame(frame_idx)
                        if frame:
                            fname, img = frame
                            thumb_refs.append(img)
                            lbl = tk.Label(grid_frame, image=img, borderwidth=0, width=img.width(), height=img.height(), padx=0, pady=0)
                            lbl.grid(row=row, column=col+1, padx=0, pady=0)
                            if frame_idx not in frame_original_names:
                                frame_original_names[frame_idx] = fname
                            def make_tooltip(idx=frame_idx, name=fname):
                                def on_enter(event):
                                    prev = frame_original_names.get(idx, name)
                                    text = f"{name}"
                                    if prev != name:
                                        text += f"\nwas {prev}"
                                    show_tooltip(event, text)
                                return on_enter
                            lbl.bind("<Enter>", make_tooltip())
                            lbl.bind("<Leave>", hide_tooltip)
                            lbl.bind("<Button-1>", lambda e, idx=frame_idx: selector.on_left_click(idx))
                            lbl.bind("<Button-3>", lambda e, idx=frame_idx: selector.on_right_click(e, idx))
                            frame_labels.append((lbl, frame_idx))
                        else:
                            tk.Label(grid_frame, text="", width=4, height=2, borderwidth=0, padx=0, pady=0).grid(row=row, column=col+1, padx=0, pady=0)
        frames_inner._thumb_refs = thumb_refs  # Prevent garbage collection
        # Set up FrameSelector for editing
        global selector
        try:
            selector
        except NameError:
            selector = FrameSelector(frame_loader, frames_inner, lambda: show_animations_simple(frames_grid), swap_instruction_var)
            frames_inner._frame_selector = selector
        # Always update the callback to use the current frames_grid
        selector.update_callback = lambda: show_animations_simple(frames_grid)
        selector.set_frame_labels(frame_labels)
        # Show swap instruction if in swap mode
        if hasattr(selector, 'swap_mode') and selector.swap_mode:
            swap_instruction_var.set("Click on a frame to swap")
        else:
            swap_instruction_var.set("")

    # Replace all previous grid/animation selector logic with this:
    def update_sequence_boxes(seq, facings=8):
        input_text_box.delete('1.0', tk.END)
        input_text_box.insert(tk.END, seq)
        output_text_box.config(state='normal')
        output_text_box.delete('1.0', tk.END)
        output_text_box.config(state='disabled')
        # Parse and build grid
        mode = mode_var.get()
        data = parse_ini_data(seq)
        vehicle_keys = {"StandingFrames", "WalkFrames", "DeathFrames", "FiringFrames", "IdleFrames"}
        infantry_keys = set([
            "Ready", "Guard", "Prone", "Walk", "FireUp", "FireProne", "Down", "Crawl", 
            "Up", "Idle1", "Idle2", "Die1", "Die2", "Die3", "Die4", "Die5", 
            "Fly", "Hover", "FireFly", "Tumble", "SecondaryFire", "SecondaryProne", 
            "Deploy", "Deployed", "DeployedFire", "DeployedIdle", "Undeploy", 
            "Paradrop", "Cheer", "Panic", "Shovel", "Carry", "AirDeathStart", 
            "AirDeathFalling", "AirDeathFinish", "Tread", "Swim", "WetAttack", 
            "WetIdle1", "WetIdle2", "WetDie1", "WetDie2", "Struggle"
        ])
        if mode == 'Vehicle':
            if not any(k in data for k in vehicle_keys):
                messagebox.showerror("Wrong INI Type", "You are in Vehicle mode but the sequence does not contain any vehicle keys (StandingFrames, WalkFrames, etc). Please use a vehicle INI.")
                return
        elif mode == 'Infantry':
            if not any(k in data for k in infantry_keys):
                messagebox.showerror("Wrong INI Type", "You are in Infantry mode but the sequence does not contain any infantry keys (Walk, Ready, Die1, etc). Please use an infantry INI.")
                return
        max_frame = 0
        for v in data.values():
            parts = [p.strip() for p in v.split(",") if p.strip()]
            if len(parts) >= 3:
                start = int(parts[0])
                count = int(parts[1])
                skip = int(parts[2])
                if mode == 'Infantry':
                    end = start + 8 * skip - 1 if skip else start + count - 1
                else:
                    end = start + facings * count - 1
                if end > max_frame:
                    max_frame = end
        total_frames = (max_frame + 1) * 2  # normal + shadow
        frames_grid, _ = build_frame_grid(data, mode, facings, total_frames)
        show_animations_simple(frames_grid)

    def add_files():
        filetypes = [("Image files", "*.png *.gif"), ("PNG", "*.png"), ("GIF", "*.gif")]
        files = filedialog.askopenfilenames(title="Select PNG or GIF files", filetypes=filetypes)
        if files:
            loaded_filepaths.clear()
            loaded_filepaths.extend(files)
            from PIL import Image
            preview_images = [Image.open(f).convert('RGBA') for f in files]
            selected_transparency = [None]
            # Show the settings popup after loading files
            def mode_callback(selected_mode):
                mode_var.set(selected_mode)
            def after_settings(seq=None, facings=8):
                show_loading_bar()
                window.update_idletasks()
                total = len(files)
                for i, f in enumerate(files):
                    update_loading_bar((i / max(1, total)) * 100)
                    window.update_idletasks()
                frame_loader.load_files(files)
                if selected_transparency[0] is not None:
                    frame_loader.set_transparency(selected_transparency[0])
                update_loading_bar(100)
                window.update_idletasks()
                hide_loading_bar()
                print(f"[DEBUG] Loaded {len(frame_loader.frames)} frames.")
                mode = mode_var.get() or settings_state['mode']
                if mode == 'Vehicle' and (seq is None or not seq.strip()):
                    messagebox.showwarning("No Sequence", "Please enter a valid sequence for vehicle mode. Frames will not be displayed until a sequence is provided.")
                    return
                if seq is not None:
                    update_sequence_boxes(seq, facings)
            def open_settings_popup_with_state(master, images, mode_callback=None):
                popup = tk.Toplevel(master)
                popup.title("Settings")
                popup.grab_set()
                idx = [0]
                selected_rgb = [settings_state['transparency_color']]
                mode_popup_var = tk.StringVar(value=settings_state['mode'])
                facings_values = [8, 16, 32, 64]
                facings_var = tk.IntVar(value=settings_state['facings'])

                def update_facings_state(selected_mode):
                    if selected_mode == "Infantry":
                        facings_var.set(8)
                        facings_left_btn.config(state='disabled')
                        facings_right_btn.config(state='disabled')
                        facings_label.config(state='disabled')
                    elif selected_mode == "Vehicle":
                        facings_left_btn.config(state='normal')
                        facings_right_btn.config(state='normal')
                        facings_label.config(state='normal')
                    else:
                        facings_left_btn.config(state='disabled')
                        facings_right_btn.config(state='disabled')
                        facings_label.config(state='disabled')

                def on_mode_change():
                    update_facings_state(mode_popup_var.get())

                def show_image():
                    pil_img = images[idx[0]]
                    img = ImageTk.PhotoImage(pil_img)
                    image_label.config(image=img)
                    image_label.image = img
                    frame_label.config(text=f"Frame {idx[0]+1} / {len(images)}")
                    color_label.config(text=f"Selected color: {selected_rgb[0]}" if selected_rgb[0] else "Click image to pick the transparency color")

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

                def update_transparency_color_box():
                    rgb = selected_rgb[0]
                    if rgb:
                        hex_color = '#%02x%02x%02x' % rgb
                        transparency_color_box.config(bg=hex_color)
                    else:
                        transparency_color_box.config(bg='SystemButtonFace')

                def on_ok():
                    if not mode_popup_var.get():
                        tk.messagebox.showwarning("Select Mode", "Pick infantry or vehicle")
                        return
                    # Store settings
                    settings_state['mode'] = mode_popup_var.get()
                    settings_state['facings'] = facings_var.get()
                    settings_state['transparency_color'] = selected_rgb[0]
                    seq_value = seq_box.get('1.0', tk.END).strip()  # Get value before destroying popup
                    facings_value = facings_var.get()
                    selected_transparency[0] = selected_rgb[0]
                    popup.grab_release()
                    popup.destroy()
                    frame_loader.shadows_included = True
                    if mode_callback:
                        mode_callback(mode_popup_var.get())
                    update_transparency_color_box()
                    update_main_transparency_color_box()
                    window.after(10, lambda: after_settings(seq_value, facings_value))

                def on_skip():
                    popup.grab_release()
                    popup.destroy()
                    frame_loader.shadows_included = True
                    update_transparency_color_box()
                    update_main_transparency_color_box()
                    master.after(10, lambda: after_settings(None, facings_var.get()))

                def on_reset_transparency():
                    selected_rgb[0] = None
                    settings_state['transparency_color'] = None
                    frame_loader.frames = [(f"{i:04d}.png", ImageTk.PhotoImage(img)) for i, img in enumerate(frame_loader.original_images)]
                    frame_loader.cropped_images = list(frame_loader.original_images)
                    color_label.config(text="Transparency reset. Click image to pick a new color.")
                    update_transparency_color_box()
                    update_main_transparency_color_box()

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
                reset_btn = tk.Button(popup, text="Reset Transparency", command=on_reset_transparency)
                reset_btn.pack(pady=(0, 5))
                mode_frame = tk.Frame(popup)
                mode_frame.pack(pady=5)
                tk.Label(mode_frame, text="Mode:").pack(side="left")
                infantry_radio = tk.Radiobutton(mode_frame, text="Infantry", variable=mode_popup_var, value="Infantry", command=on_mode_change)
                infantry_radio.pack(side="left", padx=5)
                vehicle_radio = tk.Radiobutton(mode_frame, text="Vehicle", variable=mode_popup_var, value="Vehicle", command=on_mode_change)
                vehicle_radio.pack(side="left", padx=5)
                facings_frame = tk.Frame(popup)
                facings_frame.pack(pady=5)
                tk.Label(facings_frame, text="Facings:").pack(side="left")
                facings_left_btn = tk.Button(facings_frame, text="<-", width=2, command=lambda: facings_var.set(max(8, facings_var.get()//2)))
                facings_left_btn.pack(side="left")
                facings_label = tk.Label(facings_frame, textvariable=facings_var, width=3)
                facings_label.pack(side="left")
                facings_right_btn = tk.Button(facings_frame, text="->", width=2, command=lambda: facings_var.set(min(64, facings_var.get()*2)))
                facings_right_btn.pack(side="left")
                seq_label = tk.Label(popup, text="Enter sequence here:")
                seq_label.pack(pady=(10,0))
                seq_box = tk.Text(popup, width=50, height=6)
                seq_box.pack(padx=10, pady=(0,10))
                ok_btn = tk.Button(popup, text="OK", command=on_ok)
                ok_btn.pack(side="left", padx=20, pady=10)
                skip_btn = tk.Button(popup, text="Skip", command=on_skip)
                skip_btn.pack(side="right", padx=20, pady=10)
                show_image()
                update_facings_state(mode_popup_var.get())
                update_transparency_color_box()
                # If mode is '', deselect both radio buttons
                if mode_popup_var.get() == '':
                    infantry_radio.deselect()
                    vehicle_radio.deselect()
                popup.wait_window()
            open_settings_popup_with_state(window, preview_images, mode_callback=mode_callback)

    add_files_btn = tk.Button(frames_group, text="Add Files", command=add_files)
    add_files_btn.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
    help_frames_btn = tk.Button(frames_group, text="Help", command=lambda: messagebox.showinfo("Help", "[Help content removed]") )
    help_frames_btn.grid(row=0, column=1, sticky="nw", padx=5, pady=5)
    select_transparency_btn = tk.Button(frames_group, text="Settings", command=lambda: open_settings_popup(window, frame_loader.original_images, mode_callback=lambda selected_mode: mode_var.set(selected_mode)))
    select_transparency_btn.grid(row=0, column=2, sticky="nw", padx=5, pady=5)

    # Canvas for frames (placeholder, no frame logic)
    frames_canvas = tk.Canvas(frames_group, height=400)
    frames_canvas.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)
    frames_group.rowconfigure(1, weight=1)
    frames_group.columnconfigure(0, weight=1)

    # Scrollbars for frames canvas (placeholders)
    frames_scrollbar_y = tk.Scrollbar(frames_group, orient="vertical", command=frames_canvas.yview)
    frames_scrollbar_y.grid(row=1, column=4, sticky="ns")
    frames_canvas.configure(yscrollcommand=frames_scrollbar_y.set)

    frames_scrollbar_x = tk.Scrollbar(frames_group, orient="horizontal", command=frames_canvas.xview)
    frames_scrollbar_x.grid(row=2, column=0, columnspan=4, sticky="ew")
    frames_canvas.configure(xscrollcommand=frames_scrollbar_x.set)

    # Frame inside canvas (placeholder)
    frames_inner = tk.Frame(frames_canvas)
    frames_canvas.create_window((0, 0), window=frames_inner, anchor="nw")

    def on_canvas_configure(event):
        frames_canvas.configure(scrollregion=frames_canvas.bbox("all"))
    frames_inner.bind("<Configure>", on_canvas_configure)

    # At the end of create_ui, initialize the color box
    update_main_transparency_color_box()

    # Enable the 'Save Frames' button and implement saving logic
    def save_frames_action():
        if not frame_loader.frames:
            messagebox.showwarning("Save", "No frames to save.")
            return
        outdir = filedialog.askdirectory(title="Select output directory for frames")
        if not outdir:
            return
        for fname, img in frame_loader.frames:
            # img is an ImageTk.PhotoImage, get the underlying PIL image
            idx = int(fname.split('.')[0])
            pil_img = frame_loader.get_pil_image(idx)
            if pil_img is not None:
                pil_img.save(os.path.join(outdir, fname))
        messagebox.showinfo("Save", f"Saved {len(frame_loader.frames)} frames to {outdir}")

    save_btn = tk.Button(frames_group, text="Save Frames", command=save_frames_action, state='normal')
    save_btn.grid(row=0, column=6, sticky="ne", padx=5, pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_ui()