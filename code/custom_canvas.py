import tkinter as tk
from PIL import Image, ImageTk

class Canvas:
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

        #
        # TODO: Open for rework needs rework
        #

        self.image_scale = 1

        # Grid settings
        self.grid_rows = 40
        self.grid_cols = 40
        self.grid_color = "#000000"
        self.grid_thickness = 1

        # None initialized vars
        self.original_image = None
        self.display_image = None
        self.image_on_canvas = None
        self.pan_start = None
        self.text_label = None

        self.add_image_to_canvas()

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

    #
    # TODO: From here needs rework
    #

    def add_image_to_canvas(self):
        # Load the image
        # TODO: change so created image is displayed
        image = Image.open("./env_001--4_2.png")

        # Crop the image
        crop_box = (0, 0, image.width - 4, image.height - 4)
        image = image.crop(crop_box)

        self.original_image = image
        self.display_image = image  # Image to be displayed

        # Display the initial image
        self.update_display_image()

        # Bind mouse events for zoom and pan
        self.canvas.bind("<Leave>", self.remove_coordinates_display)
        self.canvas.bind("<Motion>", self.update_grid_coordinates)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)

    def update_display_image(self):
        """Update the image displayed on the canvas based on the current scale."""
        new_width = int(self.original_image.width * self.image_scale)
        new_height = int(self.original_image.height * self.image_scale)
        resized_image = self.original_image.resize((new_width, new_height))
        self.display_image = ImageTk.PhotoImage(resized_image)

        if self.image_on_canvas is None:
            # Display the image initially
            self.image_on_canvas = self.canvas.create_image(
                50, 50, anchor="nw", image=self.display_image
            )
        else:
            # Update the image
            self.canvas.itemconfig(self.image_on_canvas,
                                   image=self.display_image)

        # Update canvas scroll region to match the current image size
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))

        # Redraw the grid
        self.draw_grid(new_width, new_height)

    def draw_grid(self, img_width, img_height):
        """Draw a grid with numerical labels fixed to the image."""
        # Clear existing grid lines and labels
        self.canvas.delete("grid_line")
        self.canvas.delete("grid_label")

        # Calculate grid spacing
        row_spacing = img_height / self.grid_rows
        col_spacing = img_width / self.grid_cols

        # Get the current position of the image
        x0, y0 = self.canvas.coords(self.image_on_canvas)

        # Draw horizontal lines and row labels
        for i in range(self.grid_rows + 1):
            y = y0 + i * row_spacing
            # Draw horizontal grid line
            self.canvas.create_line(
                x0, y, x0 + img_width, y,
                fill=self.grid_color,
                width=self.grid_thickness,
                tags="grid_line"
            )
            # Add row labels
            if i < self.grid_rows:
                label_y = y + row_spacing / 2  # Center label between grid lines
                self.canvas.create_text(
                    x0 - 20, label_y,  # Position relative to the image
                    text=str(i),
                    anchor="e",  # Align text to the right
                    font=("Arial", 10),
                    fill='#FFFFFF',
                    tags="grid_label"
                )

        # Draw vertical lines and column labels
        for i in range(self.grid_cols + 1):
            x = x0 + i * col_spacing
            # Draw vertical grid line
            self.canvas.create_line(
                x, y0, x, y0 + img_height,
                fill=self.grid_color,
                width=self.grid_thickness,
                tags="grid_line"
            )
            # Add column labels
            if i < self.grid_cols:
                label_x = x + col_spacing / 2  # Center label between grid lines
                self.canvas.create_text(
                    label_x, y0 - 20,  # Position relative to the image
                    text=str(i),
                    anchor="e",  # Align text to the bottom
                    angle=90,
                    font=("Arial", 10),
                    fill='#FFFFFF',
                    tags="grid_label"
                )

    def update_grid_coordinates(self, event):
        """Update the grid coordinates and display the current cell under the cursor."""
        # Get the position of the mouse on the canvas
        mouse_x = event.x
        mouse_y = event.y

        # Get the current position of the image on the canvas
        image_coords = self.canvas.coords(self.image_on_canvas)
        if not image_coords:
            return  # Image not loaded yet

        x0, y0 = image_coords

        # Adjust for panning and scaling
        adjusted_x = (mouse_x - x0) / self.image_scale
        adjusted_y = (mouse_y - y0) / self.image_scale

        # Check if the cursor is within the bounds of the image
        img_width = self.original_image.width
        img_height = self.original_image.height
        if 0 <= adjusted_x < img_width and 0 <= adjusted_y < img_height:
            # Calculate the grid cell row and column
            row_spacing = img_height / self.grid_rows
            col_spacing = img_width / self.grid_cols

            row = int(adjusted_y / row_spacing)
            col = int(adjusted_x / col_spacing)

            # Format the row and column to be displayed
            coords_text = f"[{row}, {col}]"

            # If the text label doesn't exist, create it
            if self.text_label is None:
                self.text_label = self.canvas.create_text(
                    mouse_x + 10, mouse_y + 10,  # Position next to the cursor
                    text=coords_text,
                    font=("Arial", 12),
                    fill="#000000",  # Text color
                    anchor="nw"
                )
            else:
                # Update the text and position of the label
                self.canvas.itemconfig(self.text_label, text=coords_text)
                self.canvas.coords(self.text_label, mouse_x + 10, mouse_y + 10)
        else:
            # Remove the label if the cursor is not over the image
            if self.text_label is not None:
                self.canvas.delete(self.text_label)
                self.text_label = None

    def remove_coordinates_display(self, event):
        """Clear the coordinates label when the mouse leaves the canvas."""
        if self.text_label is not None:
            self.canvas.delete(self.text_label)
            self.text_label = None

    def zoom(self, event):
        """Zoom the image in or out."""
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.image_scale *= scale_factor
        self.image_scale = max(0.1,
                               self.image_scale)  # Prevent negative or zero scale
        self.update_display_image()

    def start_pan(self, event):
        """Start the pan operation."""
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        """Pan the image and grid together."""
        if self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas.move(self.image_on_canvas, dx, dy)
            self.canvas.move("grid_line", dx, dy)
            self.canvas.move("grid_label", dx, dy)
            self.pan_start = (event.x, event.y)
