import tkinter as tk
from PIL import Image, ImageTk

DIR_ORDER = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
VEHICLE_DIR_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

class FrameLoader:
    def __init__(self):
        self.original_images = []
        self.frames = []
        self.cropped_images = []
        self.transparency_color = None
        self._update_callback = None
        self.shadows_included = True
        self.has_shadow_frames = False
        self.shadow_offset = None

    def crop_transparent(self, pil_img):
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        bbox = pil_img.getchannel('A').getbbox()
        if bbox:
            return pil_img.crop(bbox)
        return pil_img

    def set_transparency(self, rgb, update_callback=None):
        # Remove the selected color from all frames and crop
        new_frames = []
        new_cropped_images = []
        for i, pil_img in enumerate(self.original_images):
            datas = pil_img.getdata()
            newData = []
            for item in datas:
                if item[:3] == rgb:
                    newData.append((255, 255, 255, 0))  # Fully transparent
                else:
                    newData.append(item)
            new_img = Image.new("RGBA", pil_img.size)
            new_img.putdata(newData)
            cropped_img = self.crop_transparent(new_img)
            new_cropped_images.append(cropped_img)
            new_frames.append((self.frames[i][0], ImageTk.PhotoImage(cropped_img)))
        self.frames = new_frames
        self.cropped_images = new_cropped_images
        self.transparency_color = rgb
        cb = update_callback if update_callback is not None else getattr(self, '_update_callback', None)
        if cb:
            cb()

    def load_files(self, filepaths, master=None, update_callback=None):
        self.frames.clear()
        self.original_images.clear()
        self.cropped_images = []
        self.transparency_color = None
        self._update_callback = update_callback
        for path in filepaths:
            pil_img = Image.open(path).convert('RGBA')
            self.original_images.append(pil_img)
        # By default, no transparency applied
        self.frames = [(f"{i:04d}.png", ImageTk.PhotoImage(img)) for i, img in enumerate(self.original_images)]
        self.cropped_images = list(self.original_images)
        # Set shadow frame info
        n = len(self.original_images)
        if n > 0 and n % 2 == 0:
            self.has_shadow_frames = True
            self.shadow_offset = n // 2
        else:
            self.has_shadow_frames = False
            self.shadow_offset = None
        if update_callback:
            update_callback()

    def count(self):
        return len(self.frames)

    def get_frame(self, idx):
        if 0 <= idx < len(self.frames):
            return self.frames[idx]
        return None

    def swap_frames(self, idx1, idx2):
        # Ensure valid indices
        if not (0 <= idx1 < len(self.frames) and 0 <= idx2 < len(self.frames)):
            print(f"Invalid indices for swap: {idx1}, {idx2}")
            return

        # Swap the (filename, ImageTk.PhotoImage) tuples in self.frames
        self.frames[idx1], self.frames[idx2] = self.frames[idx2], self.frames[idx1]

        # Swap the underlying PIL Image objects in original_images
        self.original_images[idx1], self.original_images[idx2] = self.original_images[idx2], self.original_images[idx1]

        # Swap cropped images if they exist
        if hasattr(self, 'cropped_images') and self.cropped_images:
            self.cropped_images[idx1], self.cropped_images[idx2] = self.cropped_images[idx2], self.cropped_images[idx1]

        # Handle shadow frames mirroring the main frame swap
        has_shadow_frames = getattr(self, 'has_shadow_frames', False)
        shadow_offset = getattr(self, 'shadow_offset', None)

        # Only mirror if the swap happened within the main frame block (first half)
        # The UI `on_left_click` should prevent cross-half swaps.
        if has_shadow_frames and shadow_offset is not None and \
           (idx1 < shadow_offset and idx2 < shadow_offset): # Both indices are in the main half
            sidx1 = idx1 + shadow_offset
            sidx2 = idx2 + shadow_offset
            # Perform the swap on shadow PIL images
            if sidx1 < len(self.original_images) and sidx2 < len(self.original_images):
                self.original_images[sidx1], self.original_images[sidx2] = self.original_images[sidx2], self.original_images[sidx1]
                if hasattr(self, 'cropped_images') and self.cropped_images:
                    self.cropped_images[sidx1], self.cropped_images[sidx2] = self.cropped_images[sidx2], self.cropped_images[sidx1]

    def replace_frame(self, idx, pil_img):
        # Ensure pil_img is RGBA before processing
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        self.original_images[idx] = pil_img # Store the new PIL image
        # Apply transparency and cropping to the new image for display/cropped_images
        processed_pil_img = pil_img.copy()
        if getattr(self, 'transparency_color', None) is not None:
            rgb = self.transparency_color
            datas = processed_pil_img.getdata()
            newData = []
            for item in datas:
                if item[:3] == rgb:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
            processed_pil_img.putdata(newData)
        # Always apply cropping if the feature is enabled (i.e., transparency color is set)
        if getattr(self, 'transparency_color', None) is not None:
            processed_pil_img = self.crop_transparent(processed_pil_img)
        # Update the cropped_images list if it exists
        if hasattr(self, 'cropped_images') and self.cropped_images:
            self.cropped_images[idx] = processed_pil_img
        # Update the displayed frame (ImageTk.PhotoImage) in self.frames
        # Use processed_pil_img which has transparency and cropping applied for display
        self.frames[idx] = (self.frames[idx][0], ImageTk.PhotoImage(processed_pil_img))

    def get_pil_image(self, idx):
        if 0 <= idx < len(self.original_images):
            return self.original_images[idx]
        return None

# Main display function

def display_frames(frames_inner, frame_loader, frames_grid, mode="Infantry"):
    for widget in frames_inner.winfo_children():
        widget.destroy()
    if not frames_grid or frame_loader.count() == 0:
        return
    row = 0
    DIE_KEYS = {f"Die{i}" for i in range(1, 6)}
    IDLE_KEYS = {"Idle1", "Idle2"}
    SPECIAL_KEYS = DIE_KEYS | IDLE_KEYS | {"Struggle"}
    VEHICLE_DEATH_IDLE = {"DeathFrames", "IdleFrames"}
    for anim, directions_dict in frames_grid.items():
        anim_label = tk.Label(frames_inner, text=f"{anim}:", font=("Arial", 10, "bold"))
        anim_label.grid(row=row, column=0, sticky="w", pady=(10, 0))
        row += 1
        is_special = anim in SPECIAL_KEYS or anim in VEHICLE_DEATH_IDLE
        all_dirs_short = all(len(frames) <= 4 for frames in directions_dict.values())
        if is_special:
            # Show only unique frames in a single row, no direction labels
            seen = set()
            unique_indices = []
            for frame_indices in directions_dict.values():
                for frame_idx in frame_indices:
                    if frame_idx not in seen:
                        seen.add(frame_idx)
                        unique_indices.append(frame_idx)
            for i, frame_idx in enumerate(unique_indices):
                frame = frame_loader.get_frame(frame_idx)
                if frame:
                    fname, img = frame
                    lbl = tk.Label(frames_inner, image=img)
                    lbl.image = img
                    lbl.grid(row=row, column=i+1, padx=1, pady=2, sticky="n")
            row += 1
        elif all_dirs_short:
            # Show all directions in a single row, direction letter above each frame
            dir_names = list(directions_dict.keys())
            frame_indices_list = [directions_dict[dir_name] for dir_name in dir_names]
            # Direction label row
            for i, dir_name in enumerate(dir_names):
                tk.Label(frames_inner, text=dir_name, font=("Arial", 8)).grid(row=row, column=i+1, padx=2, pady=(0, 0))
            row += 1
            # Frame row
            for i, dir_name in enumerate(dir_names):
                frame_indices = frame_indices_list[i]
                for frame_idx in frame_indices:
                    frame = frame_loader.get_frame(frame_idx)
                    if frame:
                        fname, img = frame
                        lbl = tk.Label(frames_inner, image=img)
                        lbl.image = img
                        lbl.grid(row=row, column=i+1, padx=1, pady=2, sticky="n")
            row += 1
        else:
            # Normal: show each direction as a row
            for dir_name, frame_indices in directions_dict.items():
                tk.Label(frames_inner, text=dir_name, font=("Arial", 8)).grid(row=row, column=0, padx=2, pady=(0, 0), sticky="w")
                for i, frame_idx in enumerate(frame_indices):
                    frame = frame_loader.get_frame(frame_idx)
                    if frame:
                        fname, img = frame
                        lbl = tk.Label(frames_inner, image=img)
                        lbl.image = img
                        lbl.grid(row=row, column=i+1, padx=1, pady=2, sticky="n")
                row += 1 