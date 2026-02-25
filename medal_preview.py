#!/usr/bin/env python3
"""
tkinter version of medal preview tool.
drag a medal onto a jacket photo, resize with the scroll wheel & save the result.
"""

import sys
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox


class MedalPreviewTool:
    def __init__(self, base_image_path, medal_image_path):
        self.base_image_path = base_image_path
        self.medal_image_path = medal_image_path

        self.base_image = Image.open(base_image_path).convert("RGBA")
        self.medal_image = Image.open(medal_image_path).convert("RGBA")
        self.original_medal_size = self.medal_image.size

        self.medal_x = 100
        self.medal_y = 100
        self.medal_scale = 1.0

        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.setup_ui()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Medal preview tool")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=0, column=0, columnspan=2)

        # Fit to screen
        screen_width = self.root.winfo_screenwidth() - 200
        screen_height = self.root.winfo_screenheight() - 300
        img_width, img_height = self.base_image.size
        self.display_scale = min(screen_width / img_width, screen_height / img_height, 1.0)
        display_width = int(img_width * self.display_scale)
        display_height = int(img_height * self.display_scale)

        self.canvas = tk.Canvas(canvas_frame, width=display_width, height=display_height)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-4>", lambda e: self.on_scroll(e, direction=1))   # Linux scroll up
        self.canvas.bind("<Button-5>", lambda e: self.on_scroll(e, direction=-1))  # Linux scroll down

        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Label(controls_frame, text="Medal Size:").grid(row=0, column=0, padx=5)
        self.scale_var = tk.DoubleVar(value=1.0)
        self.scale_slider = ttk.Scale(controls_frame, from_=0.1, to=3.0,
                                       variable=self.scale_var, orient=tk.HORIZONTAL,
                                       length=200, command=self.on_scale_change)
        self.scale_slider.grid(row=0, column=1, padx=5)

        self.scale_label = ttk.Label(controls_frame, text="100%")
        self.scale_label.grid(row=0, column=2, padx=5)

        ttk.Button(controls_frame, text="Save Preview",
                   command=self.save_preview).grid(row=0, column=3, padx=10)
        ttk.Button(controls_frame, text="Reset",
                   command=self.reset_position).grid(row=0, column=4, padx=5)

        ttk.Label(main_frame,
                  text="Click and drag to position the medal. Use scroll wheel or slider to resize."
                  ).grid(row=2, column=0, columnspan=2, pady=5)

        self.update_preview()

    def get_scaled_medal(self):
        new_width = max(1, int(self.original_medal_size[0] * self.medal_scale))
        new_height = max(1, int(self.original_medal_size[1] * self.medal_scale))
        return self.medal_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def create_composite(self):
        composite = self.base_image.copy()
        scaled_medal = self.get_scaled_medal()
        composite.paste(scaled_medal, (int(self.medal_x), int(self.medal_y)), scaled_medal)
        return composite

    def update_preview(self):
        composite = self.create_composite()

        display_width = int(composite.width * self.display_scale)
        display_height = int(composite.height * self.display_scale)
        display_image = composite.resize((display_width, display_height), Image.Resampling.LANCZOS)

        # Hold a reference so tkinter doesn't garbage-collect the image
        self.photo = ImageTk.PhotoImage(display_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Dashed outline around the medal for visibility
        scaled_medal = self.get_scaled_medal()
        x1 = int(self.medal_x * self.display_scale)
        y1 = int(self.medal_y * self.display_scale)
        x2 = int((self.medal_x + scaled_medal.width) * self.display_scale)
        y2 = int((self.medal_y + scaled_medal.height) * self.display_scale)
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=2, dash=(4, 4))

    def on_click(self, event):
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        if self.dragging:
            dx = (event.x - self.drag_start_x) / self.display_scale
            dy = (event.y - self.drag_start_y) / self.display_scale
            self.medal_x += dx
            self.medal_y += dy
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.update_preview()

    def on_release(self, event):
        self.dragging = False

    def on_scroll(self, event, direction=None):
        if direction is None:
            direction = 1 if event.delta > 0 else -1
        self.medal_scale *= 1.1 if direction > 0 else (1 / 1.1)
        self.medal_scale = max(0.1, min(3.0, self.medal_scale))
        self.scale_var.set(self.medal_scale)
        self.scale_label.config(text=f"{int(self.medal_scale * 100)}%")
        self.update_preview()

    def on_scale_change(self, value):
        self.medal_scale = float(value)
        self.scale_label.config(text=f"{int(self.medal_scale * 100)}%")
        self.update_preview()

    def reset_position(self):
        self.medal_x = 100
        self.medal_y = 100
        self.medal_scale = 1.0
        self.scale_var.set(1.0)
        self.scale_label.config(text="100%")
        self.update_preview()

    def save_preview(self):
        composite = self.create_composite()
        output_path = "medal_preview_output.png"
        composite.convert("RGB").save(output_path, quality=95)
        messagebox.showinfo("Saved", f"Preview saved to {output_path}")

    def run(self):
        self.root.mainloop()


def main():
    base_image = "3099.jpg"
    medal_image = "85494.avif"

    if len(sys.argv) >= 3:
        base_image = sys.argv[1]
        medal_image = sys.argv[2]

    try:
        tool = MedalPreviewTool(base_image, medal_image)
        tool.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nUsage: python medal_preview.py [base_image] [medal_image]")
        print("Default: python medal_preview.py 3099.jpg 85494.avif")
        sys.exit(1)


if __name__ == "__main__":
    main()
