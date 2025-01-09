import tkinter as tk
from PIL import Image, ImageTk

class EnvCanvas:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            background_color: str,
            border_width: int,
            image:str,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background_color = background_color
        self.border_width = border_width

        self.image = self.get_image(image)
        self.display_image = None
        self.canvas_image = None

        self.canvas = self.create_canvas()
        self.place_canvas()

        # populate canvas
        self.rows = 40
        self.cols = 40
        self.pan_start = (0, 0)
        self.x_offset = 50
        self.y_offset = 50
        self.cell_size = 50
        self.scale = 1.0
        self.text_label = None

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.draw_image()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def place_canvas(self):#
        self.canvas.place(x=self.x, y=self.y)

    @staticmethod
    def get_image(image_path):
        image = Image.open(image_path)
        crop_box = (0, 0, image.width - 4, image.height - 4)
        image = image.crop(crop_box)
        return image

    def zoom(self, event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        new_scale = self.scale * scale_factor

        # Prevent too much zoom
        new_scale  = max(0.1, min(new_scale, 10))

        # Calculate the point in the grid where the mouse is
        grid_mouse_x = (event.x - self.x_offset) / self.scale
        grid_mouse_y = (event.y - self.y_offset) / self.scale

        # Update offsets to keep the grid under the mouse stable
        self.x_offset -= (grid_mouse_x * new_scale - grid_mouse_x * self.scale)
        self.y_offset -= (grid_mouse_y * new_scale - grid_mouse_y * self.scale)

        # Apply the new scale
        self.scale = new_scale

        self.draw_image()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        self.draw_image()

    def draw_mouse_symbols(self, event):
        mouse_x = event.x
        mouse_y = event.y
        adjusted_x = (mouse_x - self.x_offset) / self.scale
        adjusted_y = (mouse_y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        if 0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height:
            row = int(adjusted_y / self.cell_size )
            col = int(adjusted_x / self.cell_size )
            coords_text = f"[{row}, {col}]"

            if self.text_label is None:
                self.text_label = self.canvas.create_text(
                    mouse_x + 10, mouse_y + 10,  # Position next to the cursor
                    text=coords_text,
                    font=("Arial", 20),
                    fill="#000000",  # Text color
                    anchor="nw"
                )
            else:
                self.canvas.itemconfig(self.text_label, text=coords_text)
                self.canvas.coords(self.text_label, mouse_x + 10, mouse_y + 10)
        else:
            self.canvas.delete(self.text_label)
            self.text_label = None

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas."""
        self.canvas.delete(self.text_label)
        self.text_label = None

    def draw_image(self):
        self.cell_size = self.image.width / self.rows
        width = int(self.rows * self.cell_size * self.scale)
        height = int(self.cols * self.cell_size * self.scale)
        self.display_image = ImageTk.PhotoImage(
            self.image.resize((width, height))
        )

        if self.canvas_image is None:
            self.canvas_image = self.canvas.create_image(
                self.x_offset,
                self.y_offset,
                anchor="nw",
                image=self.display_image
            )
        else:
            self.canvas.itemconfig(self.canvas_image,image=self.display_image)
            self.canvas.coords(self.canvas_image, self.x_offset, self.y_offset)

        self.canvas.config(scrollregion=(0, 0, width, height))
        self.draw_grid()
        return

    def draw_grid(self):
        self.canvas.delete("grid_line")
        adjusted_cell_size = self.cell_size * self.scale

        for row in range(self.rows + 1):
            self.canvas.create_line(
                self.x_offset,
                self.y_offset + row * adjusted_cell_size,
                self.x_offset + self.cols * adjusted_cell_size,
                self.y_offset + row * adjusted_cell_size,
                fill='#000000',
                tags='grid_line',
            )

        for col in range(self.cols + 1):
            self.canvas.create_line(
                self.x_offset + col * adjusted_cell_size,
                self.y_offset,
                self.x_offset + col * adjusted_cell_size,
                self.y_offset + self.rows * adjusted_cell_size,
                fill='#000000',
                tags='grid_line',
            )

        self.draw_grid_labels()

    def draw_grid_labels(self):
        self.canvas.delete("grid_label")
        adjusted_cell_size = self.cell_size * self.scale

        for row in range(self.rows):
            self.canvas.create_text(
                self.x_offset - 10,
                (self.y_offset + row * adjusted_cell_size) +
                    adjusted_cell_size / 2,
                text=str(row),
                anchor="e",
                font=("Arial", 10),
                fill='#FFFFFF',
                tags="grid_label"
            )

        for col in range(self.cols):
            self.canvas.create_text(
                (self.x_offset + col * adjusted_cell_size) +
                    adjusted_cell_size / 2,
                self.y_offset - 15,
                text=str(col),
                angle=90,
                anchor="e",
                font=("Arial", 10),
                fill='#FFFFFF',
                tags="grid_label"
            )


class BuildCanvas:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            background_color: str,
            border_width: int,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background_color = background_color
        self.border_width = border_width

        self.canvas = self.create_canvas()
        self.place_canvas()

        # populate canvas
        self.rows = 100
        self.cols = 100
        self.pan_start = (0, 0)
        self.x_offset = 0
        self.y_offset = 0
        self.cell_size = 50
        self.scale = 1.0
        self.text_label = None

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.draw_grid()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def place_canvas(self):#
        self.canvas.place(x=self.x, y=self.y)

    def zoom(self, event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        new_scale = self.scale * scale_factor

        # Prevent too much zoom
        new_scale  = max(0.1, min(new_scale, 10))

        # Calculate the point in the grid where the mouse is
        grid_mouse_x = (event.x - self.x_offset) / self.scale
        grid_mouse_y = (event.y - self.y_offset) / self.scale

        # Update offsets to keep the grid under the mouse stable
        self.x_offset -= (grid_mouse_x * new_scale - grid_mouse_x * self.scale)
        self.y_offset -= (grid_mouse_y * new_scale - grid_mouse_y * self.scale)

        # Apply the new scale
        self.scale = new_scale

        self.draw_grid()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        self.draw_grid()

    def draw_mouse_symbols(self, event):
        mouse_x = event.x
        mouse_y = event.y
        adjusted_x = (mouse_x - self.x_offset) / self.scale
        adjusted_y = (mouse_y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        if 0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height:
            row = int(adjusted_y / self.cell_size )
            col = int(adjusted_x / self.cell_size )
            coords_text = f"[{row}, {col}]"

            if self.text_label is None:
                self.text_label = self.canvas.create_text(
                    mouse_x + 10, mouse_y + 10,  # Position next to the cursor
                    text=coords_text,
                    font=("Arial", 20),
                    fill="#FFFFFF",  # Text color
                    anchor="nw"
                )
            else:
                self.canvas.itemconfig(self.text_label, text=coords_text)
                self.canvas.coords(self.text_label, mouse_x + 10, mouse_y + 10)
        else:
            self.canvas.delete(self.text_label)
            self.text_label = None

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas."""
        self.canvas.delete(self.text_label)
        self.text_label = None

    def draw_grid(self):
        self.canvas.delete("grid_line")
        adjusted_cell_size = self.cell_size * self.scale

        for row in range(self.rows + 1):
            self.canvas.create_line(
                self.x_offset,
                self.y_offset + row * adjusted_cell_size,
                self.x_offset + self.cols * adjusted_cell_size,
                self.y_offset + row * adjusted_cell_size,
                fill='#FFFFFF',
                tags='grid_line',
            )

        for col in range(self.cols + 1):
            self.canvas.create_line(
                self.x_offset + col * adjusted_cell_size,
                self.y_offset,
                self.x_offset + col * adjusted_cell_size,
                self.y_offset + self.rows * adjusted_cell_size,
                fill='#FFFFFF',
                tags='grid_line',
            )

        self.draw_grid_labels()

    def draw_grid_labels(self):
        self.canvas.delete("grid_label")
        adjusted_cell_size = self.cell_size * self.scale

        for row in range(self.rows):
            self.canvas.create_text(
                self.x_offset - 10,
                (self.y_offset + row * adjusted_cell_size) +
                adjusted_cell_size / 2,
                text=str(row),
                anchor="e",
                font=("Arial", 10),
                fill='#FFFFFF',
                tags="grid_label"
            )

        for col in range(self.cols):
            self.canvas.create_text(
                (self.x_offset + col * adjusted_cell_size) +
                adjusted_cell_size / 2,
                self.y_offset - 15,
                text=str(col),
                angle=90,
                anchor="e",
                font=("Arial", 10),
                fill='#FFFFFF',
                tags="grid_label"
            )


class ResultCanvas:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            background_color: str,
            border_width: int,
            image: str,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background_color = background_color
        self.border_width = border_width

        self.image = self.get_image(image)
        self.display_image = None
        self.canvas_image = None

        self.canvas = self.create_canvas()
        self.place_canvas()

        # populate canvas
        self.rows = 40
        self.cols = 40
        self.pan_start = (0, 0)
        self.x_offset = 50
        self.y_offset = 50
        self.cell_size = 50
        self.scale = 1.0
        self.text_label = None

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.draw_image()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def place_canvas(self):  #
        self.canvas.place(x=self.x, y=self.y)

    @staticmethod
    def get_image(image_path):
        image = Image.open(image_path)
        crop_box = (0, 0, image.width - 4, image.height - 4)
        image = image.crop(crop_box)
        return image

    def zoom(self, event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        new_scale = self.scale * scale_factor

        # Prevent too much zoom
        new_scale = max(0.1, min(new_scale, 10))

        # Calculate the point in the grid where the mouse is
        grid_mouse_x = (event.x - self.x_offset) / self.scale
        grid_mouse_y = (event.y - self.y_offset) / self.scale

        # Update offsets to keep the grid under the mouse stable
        self.x_offset -= (grid_mouse_x * new_scale - grid_mouse_x * self.scale)
        self.y_offset -= (grid_mouse_y * new_scale - grid_mouse_y * self.scale)

        # Apply the new scale
        self.scale = new_scale

        self.draw_image()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        self.draw_image()

    def draw_mouse_symbols(self, event):
        mouse_x = event.x
        mouse_y = event.y
        adjusted_x = (mouse_x - self.x_offset) / self.scale
        adjusted_y = (mouse_y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        if 0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height:
            row = int(adjusted_y / self.cell_size)
            col = int(adjusted_x / self.cell_size)
            coords_text = f"[{row}, {col}]"

            if self.text_label is None:
                self.text_label = self.canvas.create_text(
                    mouse_x + 10, mouse_y + 10,  # Position next to the cursor
                    text=coords_text,
                    font=("Arial", 20),
                    fill="#000000",  # Text color
                    anchor="nw"
                )
            else:
                self.canvas.itemconfig(self.text_label, text=coords_text)
                self.canvas.coords(self.text_label, mouse_x + 10, mouse_y + 10)
        else:
            self.canvas.delete(self.text_label)
            self.text_label = None

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas."""
        self.canvas.delete(self.text_label)
        self.text_label = None

    def draw_image(self):
        self.cell_size = self.image.width / self.rows
        width = int(self.rows * self.cell_size * self.scale)
        height = int(self.cols * self.cell_size * self.scale)
        self.display_image = ImageTk.PhotoImage(
            self.image.resize((width, height))
        )

        if self.canvas_image is None:
            self.canvas_image = self.canvas.create_image(
                self.x_offset,
                self.y_offset,
                anchor="nw",
                image=self.display_image
            )
        else:
            self.canvas.itemconfig(self.canvas_image, image=self.display_image)
            self.canvas.coords(self.canvas_image, self.x_offset, self.y_offset)

        self.canvas.config(scrollregion=(0, 0, width, height))
        self.draw_grid()
        return

    def draw_grid(self):
        self.canvas.delete("grid_line")
        adjusted_cell_size = self.cell_size * self.scale

        for row in range(self.rows + 1):
            self.canvas.create_line(
                self.x_offset,
                self.y_offset + row * adjusted_cell_size,
                self.x_offset + self.cols * adjusted_cell_size,
                self.y_offset + row * adjusted_cell_size,
                fill='#000000',
                tags='grid_line',
            )

        for col in range(self.cols + 1):
            self.canvas.create_line(
                self.x_offset + col * adjusted_cell_size,
                self.y_offset,
                self.x_offset + col * adjusted_cell_size,
                self.y_offset + self.rows * adjusted_cell_size,
                fill='#000000',
                tags='grid_line',
            )

        self.draw_grid_labels()

    def draw_grid_labels(self):
        self.canvas.delete("grid_label")
        adjusted_cell_size = self.cell_size * self.scale

        for row in range(self.rows):
            self.canvas.create_text(
                self.x_offset - 10,
                (self.y_offset + row * adjusted_cell_size) +
                adjusted_cell_size / 2,
                text=str(row),
                anchor="e",
                font=("Arial", 10),
                fill='#FFFFFF',
                tags="grid_label"
            )

        for col in range(self.cols):
            self.canvas.create_text(
                (self.x_offset + col * adjusted_cell_size) +
                adjusted_cell_size / 2,
                self.y_offset - 15,
                text=str(col),
                angle=90,
                anchor="e",
                font=("Arial", 10),
                fill='#FFFFFF',
                tags="grid_label"
            )