import tkinter as tk
from tkinter.colorchooser import askcolor
from PIL import Image, ImageDraw, ImageColor
from tkinter import filedialog
from tkinter import ttk
import pickle



class PixelArtPainter:
    def __init__(self, master, canvas_width=500, canvas_height=500, pixel_size=20):
        self.master = master
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height + 50
        self.pixel_size = pixel_size
        self.master.title("PyxelArt Painter")
        self.color = "black"
        self.grid_bool = True
        self.outline_bool = True
        self.create_widgets()
        self.canvas.config(background="white")

    def create_widgets(self):
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)

        # create file menu and add open and save options
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Export", command=self.save_image)
        self.file_menu.add_command(label="Open Projetct", command=self.open_project)
        self.file_menu.add_command(label="Save Projetct", command=self.save_project)
        self.file_menu.add_command(label="Settings", command=self.settings)

        self.canvas = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.canvas.bind("<B1-Motion>", self.draw_pixel)
        self.canvas.bind("<Button-1>", self.draw_pixel)  # also draw on initial click
        self.canvas.bind("<Button-2>", self.get_color)
        self.canvas.bind("<Button-3>", self.remove_pixel)  # also draw on initial click
        self.clear_button = ttk.Button(self.master, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(side="left")
        self.color_button = ttk.Button(self.master, text="Color", command=self.choose_color)
        self.color_button.pack(side="left")

        self.grid_var = tk.BooleanVar(value=True)
        self.grid_button = ttk.Checkbutton(self.master, text="Show grid", variable=self.grid_var,
                                           command=self.toggle_grid)
        self.grid_button.pack(side="left")
        self.outline_var = tk.BooleanVar(value=True)
        self.outline_button = ttk.Checkbutton(self.master, text="Show outline", variable=self.outline_var,
                                           command=self.toggle_outline)
        self.outline_button.pack(side="left")

        self.color_box = tk.Label(root, width=3, height=1, bg='black')
        self.color_box.pack(side="left")
        self.color_label = tk.Label(self.master, text="R: 0, G: 0, B: 0", font=("Helvetica", 8))
        self.color_label.pack(side="left")
        if self.grid_bool:
            self.draw_grid()
        self.pixels = []

    def settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")

        # canvas size
        canvas_size_frame = ttk.Frame(settings_window)
        canvas_size_label = ttk.Label(canvas_size_frame, text="Canvas size:")
        canvas_size_label.pack(side="left")
        canvas_size_options = [("300x300", 300), ("500x500", 500), ("700x700", 700)]
        canvas_size_var = tk.StringVar(settings_window, f"{self.canvas_width}x{self.canvas_height}")
        canvas_size_menu = ttk.OptionMenu(canvas_size_frame, canvas_size_var, *canvas_size_options)
        canvas_size_menu.pack(side="left")
        canvas_size_frame.pack(pady=10)

        # pixel size
        pixel_size_frame = ttk.Frame(settings_window)
        pixel_size_label = ttk.Label(pixel_size_frame, text="Pixel size:")
        pixel_size_label.pack(side="left")
        pixel_size_options = [("10", 10), ("15", 15), ("20", 20), ("30", 30)]
        pixel_size_var = tk.StringVar(settings_window, str(self.pixel_size))
        pixel_size_menu = ttk.OptionMenu(pixel_size_frame, pixel_size_var, *pixel_size_options)
        pixel_size_menu.pack(side="left")
        pixel_size_frame.pack(pady=10)

        # apply button
        apply_button = ttk.Button(settings_window, text="Apply",
                                  command=lambda: self.apply_settings(canvas_size_var.get(), pixel_size_var.get()))
        apply_button.pack()

    def apply_settings(self, canvas_size, pixel_size):
        size = int(canvas_size.replace(")", "").split(" ")[-1])
        width, height = size, size
        self.canvas_width = width
        self.canvas_height = height
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.master.geometry(f"{self.canvas_width}x{self.canvas_height+ 30}")
        # update pixel size
        self.pixel_size = int(pixel_size.replace(")", "").split(" ")[-1])
        self.clear_canvas()

    def update_color_status(self):
        RGB = ImageColor.getcolor(self.color, "RGB")
        self.color_label.config(text=f"R: {RGB[0]}, G: {RGB[1]}, B: {RGB[2]}")
        self.color_box.config(bg=self.color)

    def get_color(self, event=None):
        radius = self.pixel_size // 10
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x - radius, y - radius, x + radius, y + radius)
        for item in items:
            if item != self.clear_button and item != self.color_button:
                if "gridline" not in self.canvas.gettags(item):
                    pixel_color = self.canvas.itemcget(item, "fill")
                    self.color_box.config(bg=pixel_color)
                    RGB = ImageColor.getcolor(pixel_color, "RGB")
                    self.color_label.config(text=f"R: {RGB[0]}, G: {RGB[1]}, B: {RGB[2]}")
                    self.color = pixel_color

    def pixels_to_list(self):
        for item in self.canvas.find_all():
            fill = self.canvas.itemcget(item, "fill")
            if fill:
                x0, y0, x1, y1 = self.canvas.coords(item)
                self.pixels.append((x0, y0, fill))

    def remove_outline(self):
        self.pixels = []
        self.pixels_to_list()

        self.clear_canvas()
        self.outline_bool = False
        self.draw_pixels()

    def add_outline(self):
        self.clear_canvas()
        self.outline_bool = True
        self.draw_pixels()

    def draw_grid(self):
        for x in range(0, self.canvas_width, self.pixel_size):
            for y in range(0, self.canvas_height, self.pixel_size):
                self.canvas.create_rectangle(x, y, x + self.pixel_size, y + self.pixel_size, outline="gray", tags="gridline")

    def toggle_grid(self):
        if self.grid_var.get():
            self.draw_grid()
            self.grid_bool = True
        else:
            self.canvas.delete("gridline")
            self.grid_bool = False

    def toggle_outline(self):
        if self.outline_var.get():
            self.outline_bool = True
            self.add_outline()
        else:
            self.outline_bool = False
            self.remove_outline()

    def draw_pixel(self, event):
        x = event.x // self.pixel_size * self.pixel_size
        y = event.y // self.pixel_size * self.pixel_size
        if self.outline_bool:
            self.canvas.create_rectangle(x, y, x + self.pixel_size, y + self.pixel_size, fill=self.color)
        else:
            self.canvas.create_rectangle(x, y, x + self.pixel_size, y + self.pixel_size, fill=self.color, outline="")
        
    def draw_pixels(self):
        for x, y, color in self.pixels:
            if self.outline_bool:
                self.canvas.create_rectangle(x, y, x + self.pixel_size, y + self.pixel_size, fill=color)
            else:
                self.canvas.create_rectangle(x, y, x + self.pixel_size, y + self.pixel_size, fill=color, outline="")
        
    def remove_pixel(self, event):
        radius = self.pixel_size//5
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x - radius, y - radius, x + radius, y + radius)
        for item in items:
            if item != self.clear_button and item != self.color_button:
                if "gridline" not in self.canvas.gettags(item):
                    self.canvas.delete(item)

    def save_project(self):
        self.pixels = []
        for item in self.canvas.find_all():
            fill = self.canvas.itemcget(item, "fill")
            if fill:
                x0, y0, x1, y1 = self.canvas.coords(item)
                self.pixels.append((x0, y0, fill))
        file_path = filedialog.asksaveasfilename(defaultextension=".pkl")
        if file_path:
            with open(file_path, "wb") as f:
                pickle.dump(self.pixels, f)
    
    def open_project(self):
        self.canvas.delete("all")
        file_path = filedialog.askopenfilename(defaultextension=".pkl")
        if file_path:
            with open(file_path, "rb") as f:
                self.pixels = pickle.load(f)
            self.draw_pixels()
            if self.grid_bool:
                self.draw_grid()
    
    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            with Image.new("RGB", (self.canvas_width, self.canvas_height), "white") as image:
                draw = ImageDraw.Draw(image)
                
                for item in self.canvas.find_all():
                    fill = self.canvas.itemcget(item, "fill")
                    if fill:
                        x0, y0, x1, y1 = self.canvas.coords(item)
                        if self.outline_bool:
                            draw.rectangle((x0, y0, x1, y1), outline='black', fill=fill)
                        else:
                            draw.rectangle((x0, y0, x1, y1), fill=fill)
                image.save(file_path)

    def clear_canvas(self):
        self.canvas.delete("all")
        if self.grid_bool:
            self.draw_grid()

    def choose_color(self):
        color = askcolor(title="Choose color")
        if color:
            self.color = color[1]
        self.update_color_status()
     

if __name__ == "__main__":
    root = tk.Tk()
    painter = PixelArtPainter(root)
    root.mainloop()
    
    
    
    
    
    

