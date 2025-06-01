import tkinter as tk
from tkinter import Menu, filedialog, messagebox
from PIL import Image
import os
import re

from frame_viewer import DIR_ORDER, VEHICLE_DIR_ORDER

class FrameSelector:
    def __init__(self, frame_loader, frames_inner, update_callback, swap_instruction_var):
        self.frame_loader = frame_loader
        self.frames_inner = frames_inner
        self.update_callback = update_callback
        self.swap_instruction_var = swap_instruction_var
        self.selected_idx = None
        self.swap_mode = False
        self.swap_idx = None
        self.copied_img_pair = (None, None)  # Stores (main_img, shadow_img) PIL Image copies
        self.frame_labels = []  # List of (label, idx)

    def clear_selection(self):
        for lbl, _ in self.frame_labels:
            lbl.config(highlightthickness=0, highlightbackground=lbl.master.cget('bg'))
        self.selected_idx = None
        self.swap_mode = False
        self.swap_idx = None

    def set_frame_labels(self, frame_labels):
        self.frame_labels = frame_labels

    def on_left_click(self, idx):
        if self.swap_mode:
            if self.swap_idx is not None and self.swap_idx != idx:
                is_idx_main_half = (idx < self.frame_loader.shadow_offset) if self.frame_loader.has_shadow_frames and self.frame_loader.shadow_offset else True
                is_swap_idx_main_half = (self.swap_idx < self.frame_loader.shadow_offset) if self.frame_loader.has_shadow_frames and self.frame_loader.shadow_offset else True
                if is_idx_main_half == is_swap_idx_main_half:
                    self.frame_loader.swap_frames(self.swap_idx, idx)
                    self.clear_selection()
                    self.update_callback()
                else:
                    messagebox.showwarning("Swap Error", "Cannot swap a main frame with a shadow frame.")
                    self.clear_selection()
            return
        self.clear_selection()
        for lbl, i in self.frame_labels:
            if i == idx:
                lbl.config(highlightthickness=2, highlightbackground="red")
                self.selected_idx = idx

    def on_right_click(self, event, idx):
        menu = Menu(self.frames_inner, tearoff=0)
        menu.add_command(label="Swap", command=lambda: self.start_swap(idx))
        menu.add_command(label="Copy", command=lambda: self.copy_frame(idx))
        menu.add_command(label="Paste", command=lambda: self.paste_frame(idx))
        menu.tk_popup(event.x_root, event.y_root)

    def start_swap(self, idx):
        self.clear_selection()
        for lbl, i in self.frame_labels:
            if i == idx:
                lbl.config(highlightthickness=2, highlightbackground="blue")
        self.swap_mode = True
        self.swap_idx = idx

    def copy_frame(self, idx):
        copied_main_img = None
        copied_shadow_img = None
        main_img_to_copy = self.frame_loader.get_pil_image(idx)
        if main_img_to_copy:
            copied_main_img = main_img_to_copy.copy()
            has_shadow_frames = getattr(self.frame_loader, 'has_shadow_frames', False)
            shadow_offset = getattr(self.frame_loader, 'shadow_offset', None)
            if has_shadow_frames and shadow_offset is not None and idx < shadow_offset:
                corresponding_shadow_idx = idx + shadow_offset
                if corresponding_shadow_idx < len(self.frame_loader.original_images):
                    copied_shadow_img = self.frame_loader.get_pil_image(corresponding_shadow_idx).copy()
            self.copied_img_pair = (copied_main_img, copied_shadow_img)
            messagebox.showinfo("Copy", "Frame and its shadow (if applicable) copied! Now right-click a frame and choose Paste to replace it.")
        else:
            messagebox.showwarning("Copy", "Failed to copy frame.")
            self.copied_img_pair = (None, None)

    def paste_frame(self, idx):
        copied_main_img, copied_shadow_img = self.copied_img_pair
        if copied_main_img is None and copied_shadow_img is None:
            messagebox.showwarning("Paste", "No frame copied yet.")
            return
        has_shadow_frames = getattr(self.frame_loader, 'has_shadow_frames', False)
        shadow_offset = getattr(self.frame_loader, 'shadow_offset', None)
        is_target_main_half = (idx < shadow_offset) if has_shadow_frames and shadow_offset is not None else True
        if is_target_main_half:
            if copied_main_img is not None:
                self.frame_loader.replace_frame(idx, copied_main_img.copy())
            if has_shadow_frames and shadow_offset is not None and copied_shadow_img is not None:
                target_shadow_idx = idx + shadow_offset
                if target_shadow_idx < len(self.frame_loader.original_images):
                    self.frame_loader.replace_frame(target_shadow_idx, copied_shadow_img.copy())
        else:
            if copied_shadow_img is not None:
                self.frame_loader.replace_frame(idx, copied_shadow_img.copy())
            else:
                messagebox.showwarning("Paste", "Copied frame does not have a shadow counterpart to paste into this shadow slot.")
                return
        self.update_callback() 