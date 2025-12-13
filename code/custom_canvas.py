"""Provides custom variations of standard Tkinter canvases.

Includes a custom EnvCanvas, BuildCanvas, TrainListCanvas, ResultCanvas and
PathListCanvas.

Example usage:
    import custom_canvas

    env_canvas = custom_canvas.EnvCanvas(
        root=frame,
        width=10,
        height=10,
        x=0,
        y=0,
        font=(family='Arial', size=20),
        background_color='#000000',
        grid_color='#000000',
        border_width=0,
        image='path_to_image',
        rows=10,
        cols=10
    )
"""

import platform
import threading

import numpy as np
import pandas as pd

from code.custom_widgets import *
from code.config import AGENT_COLORS


# Platform: 
sys_platform = platform.system()


class EnvCanvas:
    """A custom tkinter Canvas to display created environments.

    Attributes:
        root (tk.Frame):
            The parent container of this canvas.
        width (int):
            specify the width of the canvas in pixel.
        height (int):
            specify the height of the canvas in pixel.
        x (int):
            specifies the x position of the canvas in the parent container.
        y (int):
            specifies the y position of the canvas in the parent container.
        font (tk.font.Font):
            applied to the grid label and mouse text on the canvas.
            Can be font family and font size.
            E.g. (family='Arial', size=20).
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        grid_color (str):
            is applied t o the grid lines and if enabled the grid labels.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the canvas in pixel.
        image (str):
            path to an image file. Will be displayed on the canvas.
        display_image (ImageTk.PhotoImage):
            holds the image that is displayed on the canvas.
        canvas_image (int):
            holds the object id of the image on the canvas.
        canvas (tk.Canvas):
            the actual canvas that is initialized internally with the
            passed parameters.
        rows (int):
            specifies how many rows the grid should have.
        cols (int):
            specifies how many columns the grid should have.
        pan_start (tuple(int,int)):
            holds the initial mouse position when panning.
        x_offset (int):
            grid and image offset in x direction on the canvas.
        y_offset (int):
            grid and image offset in y direction on the canvas.
        cell_size (int):
            holds the current cell_size of the grid.
        scale (float):
            holds the current zoom level.
        buffer_factor(float):
            holds the factor of how much the buffer is larger than
            the visible area of the canvas image.
        self.buffer_x(int):
            holds the x coordinate of the top left corner of the
            buffer area.
        self.buffer_y(int):
            holds the y coordinate of the top left corner of the
            buffer area.
        text_label (int):
            holds the object id of the mouse coordinates text.
        high_quality_render(int):
            Holds the Tkinter id of the scheduled high-quality image update.
        draw_grid_numbers(bool):
            whether to draw row and col numbers on the outside of the canvas.
    """
    def __init__(
            self,
            root: tk.Frame,
            width: int,
            height: int,
            x: int,
            y: int,
            font: Tuple[str, int],
            background_color: str,
            grid_color: str,
            border_width: int,
            image: str,
            rows: int,
            cols: int,
    ):
        """Initializes a custom tkinter Canvas to display created environments.

        Draws the grid and environment image on the initial position.

        Args:
            root (tk.Frame):
                The parent container of this canvas.
            width (int):
                specify the width of the canvas in pixel.
            height (int):
                specify the height of the canvas in pixel.
            x (int):
                specifies the x position of the canvas in the parent container.
            y (int):
                specifies the y position of the canvas in the parent container.
            font (tk.font.Font):
                applied to the grid label and mouse text on the canvas.
                Can be font family and font size.
                E.g. (family='Arial', size=20).
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            grid_color (str):
                is applied t o the grid lines and if enabled the grid labels.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the canvas in pixel.
            image (str):
                path to an image file. Will be displayed on the canvas.
            rows (int):
                specifies how many rows the grid should have.
            cols (int):
                specifies how many columns the grid should have.
        """
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.font = font
        self.background_color = background_color
        self.grid_color = grid_color
        self.border_width = border_width

        self.image = self.get_image(image)
        self.display_image = None
        self.canvas_image = None

        self.canvas = self.create_canvas()
        self.place_canvas()

        # populate canvas
        self.rows = rows
        self.cols = cols
        self.pan_start = (0, 0)
        self.x_offset = 0
        self.y_offset = 0
        self.cell_size = 50
        self.scale = 1.0
        self.buffer_factor = 0.5
        self.buffer_x = 0
        self.buffer_y = 0
        self.text_label = None
        self.high_quality_render = None

        # draw grid labels
        self.draw_grid_numbers = False

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.root.after(100, self.initial_zoom)

    def create_canvas(self) -> tk.Canvas:
        """Initializes a tkinter canvas with the current attribute values.

        Returns:
            canvas (tk.Canvas):
                handle for the tkinter canvas.
        """
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def place_canvas(self):#
        """Places canvas on the parent container at the specified position."""
        self.canvas.place(x=self.x, y=self.y)

    @staticmethod
    def get_image(image_path) -> Image.Image:
        """Load an image and convert it to a format usable by tkinter.

        Crops out the white border created automatically by Flatland.

        Args:
            image_path (str):
                file path to the image.

        Returns:
            image (Image.Image):
                processed image, formatted for use in Tkinter widgets.
        """
        image = Image.open(image_path)
        crop_box = (0, 0, image.width - 4, image.height - 4)
        image = image.crop(crop_box)
        return image

    def draw_mouse_symbols(self, event):
        """Draw the coordinates of the current grid cell next to the cursor.

        Args:
            event (tk.Event):
                event generated by the canvas when the mouse is inside its
                boundaries.
        """
        # get the dimensions of the grid
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # if inside the grid place the text next to the cursor
        if 0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height:
            # get the current grid cell
            row = int(adjusted_y / self.cell_size )
            col = int(adjusted_x / self.cell_size )
            coords_text = f"[{row}, {col}]"

            # place or move the text label
            if self.text_label is None:
                self.text_label = self.canvas.create_text(
                    event.x + 10, event.y + 10,
                    text=coords_text,
                    font=self.font,
                    fill="#000000",
                    anchor="nw"
                )
            else:
                self.canvas.itemconfig(self.text_label, text=coords_text)
                self.canvas.coords(self.text_label, event.x + 10, event.y + 10)
        else:
            # remove the coordinates on leaving the canvas
            self.canvas.delete(self.text_label)
            self.text_label = None

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse leaves the canvas
                boundaries.
        """
        self.canvas.delete(self.text_label)
        self.text_label = None

    def draw_grid(self):
        """Draw the grid lines on the canvas."""
        self.canvas.delete("grid_line")
        adjusted_cell_size = self.cell_size * self.scale

        if adjusted_cell_size < 8:
            return

        for row in range(self.rows + 1):
            self.canvas.create_line(
                self.x_offset,
                self.y_offset + row * adjusted_cell_size,
                self.x_offset + self.cols * adjusted_cell_size,
                self.y_offset + row * adjusted_cell_size,
                fill=self.grid_color,
                width=(adjusted_cell_size/100)*(1/self.scale),
                tags='grid_line',
            )

        for col in range(self.cols + 1):
            self.canvas.create_line(
                self.x_offset + col * adjusted_cell_size,
                self.y_offset,
                self.x_offset + col * adjusted_cell_size,
                self.y_offset + self.rows * adjusted_cell_size,
                fill=self.grid_color,
                width=(adjusted_cell_size/100)*(1/self.scale),
                tags='grid_line',
            )

        if self.draw_grid_numbers:
            self.draw_grid_labels()

    def draw_grid_labels(self):
        """Draw the row and column labels next to the grid."""
        self.canvas.delete("grid_label")
        adjusted_cell_size = self.cell_size * self.scale

        font = self.font.copy()
        font.config(size=int(self.font.cget("size") * adjusted_cell_size * 0.02))

        for row in range(self.rows):
            self.canvas.create_text(
                self.x_offset - 10,
                (self.y_offset + row * adjusted_cell_size) +
                    adjusted_cell_size / 2,
                text=str(row),
                anchor="e",
                font=font,
                fill=self.grid_color,
                tags="grid_label"
            )

        for col in range(self.cols):
            self.canvas.create_text(
                (self.x_offset + col * adjusted_cell_size) +
                    adjusted_cell_size,
                self.y_offset - adjusted_cell_size,
                text=str(col),
                angle=90,
                anchor="s",
                font=font,
                fill=self.grid_color,
                tags="grid_label"
            )

    def initial_zoom(self):
        """Calculate the initial position of the image centred on the canvas."""
        if self.rows > self.cols:
            self.cell_size = (self.canvas.winfo_height() * 0.8) / self.rows
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2
            self.draw_image()
        else:
            self.cell_size = (self.canvas.winfo_width() * 0.8) / self.cols
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2
            self.draw_image()

    def zoom(self, event):
        """Calculate new scale and offset.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse wheel is scrolled.
        """
        scale_factor = 1.2 if event.delta > 0 else 0.8
        new_scale = self.scale * scale_factor

        new_scale  = max(1/2, min(new_scale, max(self.rows/3, self.cols/3)))

        grid_mouse_x = (event.x - self.x_offset) / self.scale
        grid_mouse_y = (event.y - self.y_offset) / self.scale

        self.x_offset -= (grid_mouse_x * new_scale - grid_mouse_x * self.scale)
        self.y_offset -= (grid_mouse_y * new_scale - grid_mouse_y * self.scale)

        self.scale = new_scale

        self.draw_image()

    def start_pan(self, event):
        """Get the initial mouse position when panning.

         Args:
            event (tk.Event):
                event generated by the canvas when left mouse button is pressed.
        """
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        """Calculate new offset and moves the grid and image.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse is moved while holding
                the left mouse button.
        """
        # compute the mouse movement
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        # shift the offsets and update the pan_start location
        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        # move the canvas objects
        self.canvas.move("env_image", dx, dy)
        self.canvas.move("grid_line", dx, dy)
        self.canvas.move("grid_label", dx, dy)

        # re-render the visible area if the new area is outside the buffer zone
        if self._check_buffer_boundary():
            self.draw_image()

    def _check_buffer_boundary(self) -> bool:
        """Check if the visible area is still within the buffer zone.

        Returns:
            bool (boolean):
                whether the visible area is outside the buffer zone.
        """
        # compute environment size
        env_width, env_height = self.get_env_size()

        # check if the image is not loaded yet
        if env_width == -1:
            return False

        # get canvas size
        canvas_width, canvas_height = self.get_canvas_size()

        # check if canvas is not loaded
        if canvas_width == -1:
            return False

        # determine corner points of the visible area
        view_left, view_top, view_right, view_bottom = self.get_visible_area(
            env_width, env_height, canvas_width, canvas_height
        )

        # stop if the visible area is flipped or non-existing
        if view_left == -1:
            return False

        # compute buffer zone
        buf_left = self.buffer_x
        buf_top = self.buffer_y
        buf_right = buf_left + int(canvas_width * self.buffer_factor)
        buf_bottom = buf_top + int(canvas_height * self.buffer_factor)

        # check if the visible area is outside the buffer zone
        margin = 10
        if view_left < buf_left + margin:
            return True
        if view_top < buf_top + margin:
            return True
        if view_right > buf_right - margin:
            return True
        if view_bottom > buf_bottom - margin:
            return True

        return False

    def get_env_size(self) -> Tuple[int, int]:
        """Calculate the width and height of the environment grid.

        Returns:
            env_width (int):
                width of the environment grid. -1 if the image is not yet loaded.
            env_height (int):
                height of the environment grid. -1 if the image is not yet loaded.
        """
        # compute environment grid size
        env_width = int(self.cols * self.cell_size * self.scale)
        env_height = int(self.rows * self.cell_size * self.scale)

        # reload if the image is not loaded yet
        if env_width <= 0 or env_height <= 0:
            self.root.after(100, self.initial_zoom)
            return -1, -1
        else:
            return env_width, env_height

    def get_canvas_size(self) -> Tuple[int, int]:
        """Calculate the width and height of the canvas.

        Returns:
            canvas_width (int):
                width of the canvas. -1 if the canvas is not yet loaded.
            canvas_height (int):
                height of the canvas. -1 if the canvas is not yet loaded.
        """
        # get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # reload if canvas is not loaded
        if canvas_width <= 0 or canvas_height <= 0:
            return -1, -1
        else:
            return canvas_width, canvas_height

    def get_visible_area(self, env_width, env_height, canvas_width, canvas_height) -> Tuple[int, int, int, int]:
        """Calculate the corner points of the visible area.

        Args:
            env_width (int):
                width of the environment grid.
            env_height (int):
                height of the environment grid.
            canvas_width (int):
                width of the canvas.
            canvas_height (int):
                height of the canvas.

        Returns:
            vis_left (int):
                x coordinate of the top left corner of the visible area.
                -1 if the visible area is flipped or non-existing.
            vis_top (int):
                y coordinate of the top left corner of the visible area.
                -1 if the visible area is flipped or non-existing.
            vis_right (int):
                x coordinate of the bottom right corner of the visible area.
                -1 if the visible area is flipped or non-existing.
            vis_bottom (int):
                y coordinate of the bottom right corner of the visible area.
                -1 if the visible area is flipped or non-existing.
        """
        # determine corner points of the visible area
        vis_left = max(0, -int(self.x_offset))
        vis_top = max(0, -int(self.y_offset))
        vis_right = min(env_width, canvas_width - int(self.x_offset))
        vis_bottom = min(env_height, canvas_height - int(self.y_offset))

        # stop if the visible area is flipped or non-existing
        if vis_left >= vis_right or vis_top >= vis_bottom:
            return -1, -1, -1, -1
        else:
            return vis_left, vis_top, vis_right, vis_bottom

    def get_visible_projection_on_image(
            self,
            env_width,
            env_height,
            vis_left,
            vis_top,
            vis_right,
            vis_bottom
    ) -> Tuple[Union[Image.Image, None], int, int]:
        """Calculate the projection of the visible area on the original image.

        Args:
            env_width (int):
                width of the environment grid.
            env_height (int):
                height of the environment grid.
            vis_left (int):
                x coordinate of the top left corner of the visible area.
            vis_top (int):
                y coordinate of the top left corner of the visible area.
            vis_right (int):
                x coordinate of the bottom right corner of the visible area.
            vis_bottom (int):
                y coordinate of the bottom right corner of the visible area.

        Returns:
            region (Image.Image):
                projection of the visible area on the original image.
                None if the visible area is non-existing.
            vis_width (int):
                width of the visible area.
                -1 if the visible area is non-existing.
            vis_height (int):
                height of the visible area.
                -1 if the visible area is non-existing.
        """
        # get original image dimensions and get the scale factor relative to the modified image
        base_w, base_h = self.image.size
        sx = env_width / base_w
        sy = env_height / base_h

        # calculate visible are projected onto original image
        src_left = int(vis_left / sx)
        src_top = int(vis_top / sy)
        src_right = int(vis_right / sx)
        src_bottom = int(vis_bottom / sy)

        # crop the original image to the visible area projected onto it
        region = self.image.crop((src_left, src_top, src_right, src_bottom))

        # get the width and height of the visible area
        vis_width = int(vis_right - vis_left)
        vis_height = int(vis_bottom - vis_top)

        # stop if the new visible area is non-existing
        if vis_width <= 0 or vis_height <= 0:
            return None, -1, -1
        else:
            return region, vis_width, vis_height

    def draw_image(self):
        """Display the image on the canvas and adjust to the current scale"""

        # compute environment size
        env_width, env_height = self.get_env_size()

        # reload if the image is not loaded yet
        if env_width == -1:
            return

        # get canvas size
        canvas_width, canvas_height = self.get_canvas_size()

        # reload if canvas is not loaded
        if canvas_width == -1:
            return

        # determine corner points of the visible area
        vis_left, vis_top, vis_right, vis_bottom = self.get_visible_area(
            env_width, env_height, canvas_width, canvas_height
        )

        # stop if the visible area is flipped or non-existing
        if vis_left == -1:
            return

        # calculate buffer zone size
        buf_w = int(canvas_width * self.buffer_factor)
        buf_h = int(canvas_height * self.buffer_factor)

        # center the buffer around the visible area
        center_x = (vis_left + vis_right) // 2
        center_y = (vis_top + vis_bottom) // 2
        buf_left = max(0, center_x - buf_w // 2)
        buf_top = max(0, center_y - buf_h // 2)
        buf_right = min(env_width, buf_left + buf_w)
        buf_bottom = min(env_height, buf_top + buf_h)

        # update buffer x and y anchor to the centered coordinates of the top left corner
        self.buffer_x = buf_right - buf_w if buf_right - buf_w > 0 else buf_left
        self.buffer_y = buf_bottom - buf_h if buf_bottom - buf_h > 0 else buf_top

        # get cropped region and the dimensions of the visible are projected on the original image
        region, vis_width, vis_height = self.get_visible_projection_on_image(
            env_width, env_height, vis_left, vis_top, vis_right, vis_bottom
        )

        # stop if the new visible area is non-existing
        if vis_width == -1:
            return

        # resize the cropped image to the visible area using NEAREST interpolation
        visible_img = region.resize((vis_width, vis_height), Image.NEAREST)
        self.display_image = ImageTk.PhotoImage(visible_img)

        # determine location of top left corner for the resized image
        canvas_x = max(int(self.x_offset), 0)
        canvas_y = max(int(self.y_offset), 0)

        if self.canvas_image is None:
            # place the image object on the canvas
            self.canvas_image = self.canvas.create_image(
                canvas_x,
                canvas_y,
                anchor="nw",
                image=self.display_image,
                tags='env_image'
            )
        else:
            # update the image object on the canvas and move it to the correct coordinates
            self.canvas.itemconfig(self.canvas_image, image=self.display_image)
            self.canvas.coords(self.canvas_image, canvas_x, canvas_y)

        # update the size of the interactive area of the canvas
        self.canvas.config(scrollregion=(0, 0, env_width, env_height))
        self.draw_grid()

        # schedule high quality render or reschedule on new zoom command
        if self.high_quality_render:
            self.root.after_cancel(self.high_quality_render)
        self.high_quality_render = self.root.after(
            500, self.render_image_high_quality
        )

    def render_image_high_quality(self):
        """Render the full image with high quality."""
        # start worker thread to resize the original image
        threading.Thread(
            target=self._hq_resize_thread,
            args=(),
            daemon=True
        ).start()

    def _hq_resize_thread(self):
        """Resize the image to the new size according to the current zoom level."""
        # compute environment size
        env_width, env_height = self.get_env_size()

        # get canvas size
        canvas_width, canvas_height = self.get_canvas_size()

        # determine corner points of the visible area
        vis_left, vis_top, vis_right, vis_bottom = self.get_visible_area(
            env_width, env_height, canvas_width, canvas_height
        )

        if vis_left == -1:
            return

        # get cropped region and the dimensions of the visible are projected on the original image
        region, vis_width, vis_height = self.get_visible_projection_on_image(
            env_width, env_height, vis_left, vis_top, vis_right, vis_bottom
        )

        # stop if the new visible area is non-existing
        if vis_width == -1:
            return

        # resize the image with LANCZOS interpolation
        hq_image = region.resize((vis_width, vis_height), Image.LANCZOS)

        # determine location of top left corner for the resized image
        canvas_x = max(int(self.x_offset), 0)
        canvas_y = max(int(self.y_offset), 0)

        # change to main thread and place the high quality image on the canvas
        self.root.after(
            10,
            lambda: self._place_hq_image(hq_image, canvas_x, canvas_y, env_width, env_height),
        )

    def _place_hq_image(self, hq_image, canvas_x, canvas_y, env_width, env_height):
        """Place the high quality image on the canvas.

        Args:
            hq_image (Image.Image):
                image to be placed.
            canvas_x (int):
                x coordinate of the top left corner of the canvas.
            canvas_y (int):
                y coordinate of the top left corner of the canvas.
            env_width (int):
                width of the environment grid.
            env_height (int):
                height of the environment grid.
        """
        # convert image to tk format
        self.display_image = ImageTk.PhotoImage(hq_image)

        # update the image object on the canvas and move it to the correct coordinates
        self.canvas.itemconfig(self.canvas_image, image=self.display_image)
        self.canvas.coords(self.canvas_image, canvas_x, canvas_y)

        # update the size of the interactive area of the canvas
        self.canvas.config(scrollregion=(0, 0, env_width, env_height))
        self.draw_grid()


class BuildCanvas:
    """A custom tkinter Canvas to create environments.

    Attributes:
        root (tk.Frame):
            The parent container of this canvas.
        width (int):
            specify the width of the canvas in pixel.
        height (int):
            specify the height of the canvas in pixel.
        x (int):
            specifies the x position of the canvas in the parent container.
        y (int):
            specifies the y position of the canvas in the parent container.
        font (tk.font.Font):
            applied to the grid label and mouse text on the canvas.
            Can be font family and font size.
            E.g. (family='Arial', size=20).
        id_label_font (tk.font.Font):
            applied to the text on the canvas. Can be font family, font
            size and font style.
            E.g. (family='Arial', size=20, style='bold').
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        grid_color (str):
            is applied t o the grid lines and if enabled the grid labels.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        train_color (str):
            applied to the id label of trains.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        station_color (str):
            applied to the id label of stations.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the canvas in pixel.
        canvas (tk.Canvas):
            the actual canvas that is initialized internally with the
            passed parameters.
        pan_start (tuple(int,int)):
            holds the initial mouse position when panning.
        x_offset (int):
            grid and image offset in x direction on the canvas.
        y_offset (int):
            grid and image offset in y direction on the canvas.
        cell_size (int):
            holds the current cell_size of the grid.
        scale (float):
            holds the current zoom level.
        text_label (int):
            holds the object id of the mouse coordinates text.
        current_selection_image (ImageTk.PhotoImage):
            holds the image displayed next to the curser of the currently
            selected object.
        mouse_image (int):
            holds the object id of the mouse image of the current selection.
        draw_grid_numbers(bool):
            whether to draw row and col numbers on the outside of the canvas.
        image_refs (dict):
            holds image references to prevent garbage collection.
        resized_cache (dict):
            holds resized images.
        canvas_images (dict):
            hold object ids for images displayed in the grid cells.
        image_cache (dict):
            a cache for images in different zoom levels.
        image_dict (dict):
            a dictionary linking flatland ids to the paths of images for
            trains, stations and tracks. Also contains a rotation that should
            be applied to each image.
        current_selection (int):
            keeps track of the current selected object type.
        array (np.array):
            holds the environment as a numpy array
        rows (int):
            specifies how many rows the grid should have.
        cols (int):
            specifies how many columns the grid should have.
        train_data (pd.DataFrame):
            holds the trains in the environment as a DataFrame
        train_list (custom_canvas.TrainListCanvas):
            holds a reference to the TrainListCanvas.
        train_index (int):
            keeps track of the currently selected train id when placing a
            station. To connect the station to the correct train.
        dir (dict):
            for conversion between numerical and string represented directions.
    """
    def __init__(
            self,
            root: tk.Frame,
            width: int,
            height: int,
            x: int,
            y: int,
            font: Tuple[str, int],
            id_label_font: Tuple[str, int, str],
            background_color: str,
            grid_color: str,
            train_color: str,
            station_color: str,
            border_width: int,
            array: np.ndarray,
            train_data: pd.DataFrame,
    ):
        """Initializes a custom tkinter Canvas to create environments.

        Draws the grid on the initial position.
        If in modify mode also loads existing objects into the grid.

        Args:
            root (tk.Frame):
                The parent container of this canvas.
            width (int):
                specify the width of the canvas in pixel.
            height (int):
                specify the height of the canvas in pixel.
            x (int):
                specifies the x position of the canvas in the parent container.
            y (int):
                specifies the y position of the canvas in the parent container.
            font (tk.font.Font):
                applied to the grid label and mouse text on the canvas.
                Can be font family and font size.
                E.g. (family='Arial', size=20).
            id_label_font (tk.font.Font):
                applied to the text on the canvas. Can be font family, font
                size and font style.
                E.g. (family='Arial', size=20, style='bold').
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            grid_color (str):
                is applied t o the grid lines and if enabled the grid labels.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            train_color (str):
                applied to the id label of trains.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            station_color (str):
                applied to the id label of stations.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the canvas in pixel.
            array (np.array):
                holds the environment as a numpy array
            train_data (pd.DataFrame):
                holds the trains in the environment as a DataFrame
        """
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.font = font
        self.id_label_font = id_label_font
        self.background_color = background_color
        self.grid_color = grid_color
        self.train_color = train_color
        self.station_color = station_color
        self.border_width = border_width

        self.canvas = self.create_canvas()
        self.place_canvas()

        self.pan_start = (0, 0)
        self.x_offset = 0
        self.y_offset = 0
        self.cell_size = 50
        self.scale = 1.0
        self.text_label = None
        self.current_selection_image = None
        self.mouse_image = None

        # draw grid labels
        self.draw_grid_numbers = False

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.modify_array)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.image_refs = {}
        self.resized_cache = {}
        self.canvas_images = {}
        self.image_cache = {}
        self.image_dict = self.set_img_dict()
        self.load_images()

        self.current_selection = None
        self.array = array
        self.rows, self.cols = array[0].shape
        self.train_data = train_data
        self.train_list = None
        self.train_index = None

        self.dir = {
            1: 'n',
            2: 'e',
            3: 's',
            4: 'w',
            'n': 1,
            'e': 2,
            's': 3,
            'w': 4,
        }

        self.root.after(100, self.calculate_initial_pos)

    def create_canvas(self) -> tk.Canvas:
        """Initializes a tkinter canvas with the current attribute values.

        Returns:
            canvas (tk.Canvas):
                handle for the tkinter canvas.
        """
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def place_canvas(self):#
        """Places canvas on the parent container at the specified position."""
        self.canvas.place(x=self.x, y=self.y)

    def select(self, selection):
        """Set the current selection.

        Args:
            selection (int):
                the currently selected track or train type or the eraser.
        """
        self.current_selection = selection

    def select_station(self, index):
        """Set current selection and train index when selecting a station.

        Args:
            index (int):
                the train for which the station is being placed.
        """
        self.current_selection = 5
        self.train_index = index

    def draw_grid(self):
        """Draw the grid lines on the canvas."""
        self.canvas.delete("grid_line")
        adjusted_cell_size = self.cell_size * self.scale

        if adjusted_cell_size < 8:
            return

        for row in range(self.rows + 1):
            self.canvas.create_line(
                self.x_offset,
                self.y_offset + row * adjusted_cell_size,
                self.x_offset + self.cols * adjusted_cell_size,
                self.y_offset + row * adjusted_cell_size,
                fill=self.grid_color,
                width=(adjusted_cell_size / 100) * (1 / self.scale),
                tags='grid_line',
            )

        for col in range(self.cols + 1):
            self.canvas.create_line(
                self.x_offset + col * adjusted_cell_size,
                self.y_offset,
                self.x_offset + col * adjusted_cell_size,
                self.y_offset + self.rows * adjusted_cell_size,
                fill=self.grid_color,
                width=(adjusted_cell_size / 100) * (1 / self.scale),
                tags='grid_line',
            )

        if self.draw_grid_numbers:
            self.draw_grid_labels()

    def draw_grid_labels(self):
        """Draw the row and column labels next to the grid."""
        self.canvas.delete("grid_label")
        adjusted_cell_size = self.cell_size * self.scale

        font = self.font.copy()
        font.config(size=int(self.font.cget("size") * adjusted_cell_size * 0.02))

        for row in range(self.rows):
            self.canvas.create_text(
                self.x_offset - 10,
                (self.y_offset + row * adjusted_cell_size) +
                adjusted_cell_size / 2,
                text=str(row),
                anchor="e",
                font=font,
                fill=self.grid_color,
                tags="grid_label"
            )

        for col in range(self.cols):
            self.canvas.create_text(
                (self.x_offset + col * adjusted_cell_size) +
                adjusted_cell_size,
                self.y_offset - adjusted_cell_size,
                text=str(col),
                angle=90,
                anchor="s",
                font=font,
                fill=self.grid_color,
                tags="grid_label"
            )

    def draw_mouse_symbols(self, event):
        """Draw symbols next to the cursor.

        Draws the current grid cell if over the grid.
        Draws the symbol of the current selection if there is one.

        Args:
            event (tk.Event):
                event generated by the canvas when the mouse is inside its
                boundaries.
        """
        # get the dimensions of the grid
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # remove symbols if not inside the grid
        if not (0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height):
            self.canvas.delete(self.text_label)
            self.canvas.delete(self.mouse_image)
            self.text_label = None
            self.mouse_image = None
            return

        # get the current grid cell
        row = int(adjusted_y / self.cell_size )
        col = int(adjusted_x / self.cell_size )
        coords_text = f"[{row}, {col}]"

        if self.text_label is None:
            self.text_label = self.canvas.create_text(
                event.x + 10,
                event.y + 10,
                text=coords_text,
                font=self.font,
                fill="#FFFFFF",
                anchor="nw"
            )
        else:
            self.canvas.itemconfig(self.text_label, text=coords_text)
            self.canvas.coords(self.text_label, event.x + 10, event.y + 10)

        if self.current_selection is not None:
            image = self.image_cache[self.current_selection].resize((30, 30))
            self.current_selection_image = ImageTk.PhotoImage(image)

            if self.mouse_image is None:
                self.mouse_image = self.canvas.create_image(
                    event.x + 10,
                    event.y - 20,
                    image=self.current_selection_image,
                    anchor="nw"
                )
            else:
                self.canvas.itemconfig(
                    self.mouse_image,
                    image=self.current_selection_image
                )
                self.canvas.coords(self.mouse_image, event.x + 10, event.y - 20)

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse leaves the canvas
                boundaries.
        """
        self.canvas.delete(self.text_label)
        self.text_label = None

    @staticmethod
    def set_img_dict() -> dict:
        """Initialize the image_dict.

        Returns:
            dictionary (dict).
                links flatland ids to the paths of images for
                trains, stations and tracks. Also contains a rotation that should
                be applied to each image.
        """
        dictionary = {
            0: ('eraser', 0),
            1: ('Zug_Gleis_#0091ea', 0),
            2: ('Zug_Gleis_#0091ea', 270),
            3: ('Zug_Gleis_#0091ea', 180),
            4: ('Zug_Gleis_#0091ea', 90),
            5: ('Bahnhof_#d50000', 0),
            32800: ('Gleis_vertikal', 0),
            1025: ('Gleis_horizontal', 0),
            2064: ('Gleis_kurve_oben_links', 0),
            72: ('Gleis_kurve_oben_rechts', 0),
            16386: ('Gleis_kurve_unten_rechts', 0),
            4608: ('Gleis_kurve_unten_links', 0),
            3089: ('Weiche_horizontal_oben_links', 0),
            1097: ('Weiche_horizontal_oben_rechts', 0),
            17411: ('Weiche_horizontal_unten_rechts', 0),
            5633: ('Weiche_horizontal_unten_links', 0),
            34864: ('Weiche_vertikal_oben_links', 0),
            32872: ('Weiche_vertikal_oben_rechts', 0),
            49186: ('Weiche_vertikal_unten_rechts', 0),
            37408: ('Weiche_vertikal_unten_links', 0),
            33825: ('Gleis_Diamond_Crossing', 0),
            35889: ('Weiche_Single_Slip', 270),
            33897: ('Weiche_Single_Slip', 180),
            50211: ('Weiche_Single_Slip', 90),
            38433: ('Weiche_Single_Slip', 0),
            52275: ('Weiche_Double_Slip', 90),
            38505: ('Weiche_Double_Slip', 0),
            2136: ('Weiche_Symetrical', 180),
            16458: ('Weiche_Symetrical', 90),
            20994: ('Weiche_Symetrical', 0),
            6672: ('Weiche_Symetrical', 270),
        }
        return dictionary

    def load_images(self):
        """Load the images from image_dict to the image cache.

        Rotate according to the rotation parameter in the dictionary.
        """
        for key, (filename, rotation) in self.image_dict.items():
            try:
                image = Image.open(f'data/png/{filename}.png')
                rotated_image = image.rotate(rotation)
                self.image_cache[key] = rotated_image
            except FileNotFoundError:
                print(f"Warning: Image {filename}.png not found.")
                self.image_cache[key] = None

    def start_pan(self, event):
        """Get the initial mouse position when panning.

         Args:
            event (tk.Event):
                event generated by the canvas when left mouse button is pressed.
        """
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        """Calculate new offset and moves the grid and image.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse is moved while holding
                the left mouse button.
        """
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        self.canvas.move("track_image", dx, dy)
        self.canvas.move("train_station_image", dx, dy)
        self.canvas.move("grid_line", dx, dy)
        self.canvas.move("grid_label", dx, dy)
        self.canvas.move("id_labels", dx, dy)

    def calculate_initial_pos(self):
        """Calculate the initial position of the grid centred on the canvas."""
        if max(self.rows, self.cols) > 50:
            self.x_offset = 50
            self.y_offset = 50
        elif self.rows > self.cols:
            self.cell_size = (self.canvas.winfo_height() * 0.8) / self.rows
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2
        else:
            self.cell_size = (self.canvas.winfo_width() * 0.8) / self.cols
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2

        self.draw_grid()
        self.resize_images()
        self.draw_images()

    def modify_array(self, event):
        """Modify the environment with the current selection.

        Change the clicked grid cell to the current selection.
        Changes layer: 0 for tracks and eraser, 1 for trains, 2 for stations.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse is moved while holding
                the left mouse button.
        """
        # get the current mouse position
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        # get the grid cell from the mouse position
        row = int(adjusted_y / self.cell_size)
        col = int(adjusted_x / self.cell_size)

        # if position is outside do nothing
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        if self.current_selection is None:
            return

        # erase track
        if self.current_selection == 0:
            self.array[0][row, col] = 0
            self.update_image_storage()
            return

        # place station
        if self.current_selection == 5:

            # remove old station if it exists
            if self.train_data['end_pos'].iloc[self.train_index] != (-1,-1):

                # get list of stations at the same position as the deleted one
                station_count = len(
                    self.train_data[
                        self.train_data['end_pos'] ==
                        self.train_data['end_pos'].iloc[self.train_index]
                    ]
                )

                # if there are no other stations at the grid positon remove the station
                if station_count == 1:
                    self.array[2][self.train_data['end_pos'].iloc[self.train_index]] = 0

            # set the new station coordinates in the train list
            self.train_data.at[self.train_index, 'end_pos'] = (row, col)

            # place station on grid
            self.array[2][row, col] = 5

            # remove old image from the grid and place one on the new position
            self.update_image_storage()
            self.draw_station(self.train_index)

            # reset selections
            self.train_index = None
            self.current_selection = None
            return

        # place train
        if self.current_selection in [1,2,3,4]:
            # add the new train to the train list
            data = {
                'start_pos': (row, col),
                'dir': self.dir[self.current_selection],
                'end_pos': (-1, -1),
                'e_dep': -1,
                'l_arr': -1,
                'speed': 1,
            }
            self.train_data.loc[len(self.train_data)] = data

            # place train on grid
            self.array[1][data['start_pos']] = self.dir[data['dir']]

            # update the TrainListCanvas
            if self.train_list:
                self.train_list.add_widget_row(len(self.train_data)-1)

            # put image on grid
            self.draw_train(len(self.train_data)-1)
            return

        # place track
        self.array[0][row, col] = self.current_selection
        self.put_img_on_canvas(self.current_selection, 0, row, col)
        self.restack_cell(row, col)
        return

    def resize_images(self):
        """Resize the images according to the current zoom level."""
        adjusted_cell_size = int(self.cell_size * self.scale)

        for value, img in self.image_cache.items():
            resized = img.resize((adjusted_cell_size, adjusted_cell_size))
            self.resized_cache[value] = ImageTk.PhotoImage(resized)

    def put_img_on_canvas(self, value, layer, row, col):
        """Place a single image in the grid.

        Args:
            value (int):
                Flatland id of object to place.
            layer (int):
                layer in which to place the image.
            row (int):
                row in which to place the image.
            col (int):
                column in which to place the image.
        """
        adjusted_cell_size = self.cell_size * self.scale

        image = self.resized_cache[value]

        x = self.x_offset + col * adjusted_cell_size
        y = self.y_offset + row * adjusted_cell_size

        # if there is an image already at that position modify it
        if (layer, row, col) in self.canvas_images:
            # if there is a different image change the image to the current one
            if self.image_refs.get((layer, row, col)) != image:
                self.image_refs[(layer, row, col)] = image
            self.canvas.itemconfig(
                self.canvas_images[(layer, row, col)], image=image
            )
            self.canvas.coords(self.canvas_images[(layer, row, col)], x, y)
        else:
            # create an image if there is none yet
            canvas_img = self.canvas.create_image(
                x, y, anchor='nw',image=image,
                tags='track_image' if layer == 0 else 'train_station_image'
            )
            self.canvas_images[(layer, row, col)] = canvas_img
            self.image_refs[(layer, row, col)] = image

    def restack_cell(self, row, col):
        """Redraw all trains and station in the grid.

        Args:
            row (int):
                row index of the cell to reorder.
            col (int):
                col index of the cell to reorder.
        """
        # get all layers present at this cell
        layers = sorted(
            [layer for (layer, r, c) in self.canvas_images.keys()
             if r == row and c == col]
        )

        for layer in layers:
            item_id = self.canvas_images[(layer, row, col)]
            self.canvas.tag_raise(item_id)

        self.draw_id_labels()
        return

    def update_image_storage(self):
        """Check the references are still valid."""
        starts = set(self.train_data['start_pos'])
        ends = set(self.train_data['end_pos'])

        new_canvas_images = {}
        new_image_refs = {}

        # check if the objects in canvas images still exist in the train list
        for (layer, row, col), item_id in self.canvas_images.items():
            keep = (
                    (layer == 0 and self.array[0][row, col] != 0) or
                    (layer == 1 and (row, col) in starts) or
                    (layer == 2 and (row, col) in ends)
            )

            if keep:
                new_canvas_images[(layer, row, col)] = item_id
                new_image_refs[(layer, row, col)] = self.image_refs[(layer, row, col)]
            else:
                self.canvas.delete(item_id)

        self.canvas_images = new_canvas_images
        self.image_refs = new_image_refs

    def draw_train(self, index):
        """Redraw all trains and station in the grid.

        Args:
            index (int):
                index of the train to draw.
        """
        row = self.train_data.iloc[index]
        self.put_img_on_canvas(
            value=self.dir[row['dir']],
            layer=1,
            row=row['start_pos'][0],
            col=row['start_pos'][1]
        )
        self.restack_cell(row['start_pos'][0], row['start_pos'][1])
        self.draw_id_labels()

    def draw_station(self, index):
        """Redraw all trains and station in the grid.

        Args:
            index (int):
                index of the station to draw.
        """
        row = self.train_data.iloc[index]
        if row['end_pos'] != (-1, -1):
            self.put_img_on_canvas(
                5,
                2,
                row=row['end_pos'][0],
                col=row['end_pos'][1]
            )
        self.restack_cell(row['end_pos'][0], row['end_pos'][1])
        self.draw_id_labels()

    def draw_id_labels(self):
        """Draw ID labels on trains and station objects."""
        self.canvas.delete('id_labels')
        adjusted_cell_size = self.cell_size * self.scale

        # manage multiple ids in the same grid cell
        # position label on a 3x3 grid in each cell to avoid overlay
        # 0 is the center position 1 is on the left and then go clockwise
        offset_dict = {
            0: (adjusted_cell_size * 0.5, adjusted_cell_size * 0.5),
            1: (adjusted_cell_size * 0.25, adjusted_cell_size * 0.5),
            2: (adjusted_cell_size * 0.25, adjusted_cell_size * 0.25),
            3: (adjusted_cell_size * 0.5, adjusted_cell_size * 0.25),
            4: (adjusted_cell_size * 0.75, adjusted_cell_size * 0.25),
            5: (adjusted_cell_size * 0.75, adjusted_cell_size * 0.5),
            6: (adjusted_cell_size * 0.75, adjusted_cell_size * 0.75),
            7: (adjusted_cell_size * 0.5, adjusted_cell_size * 0.75),
            8: (adjusted_cell_size * 0.25, adjusted_cell_size * 0.75),
        }

        used = {}

        def assign_offset(pos) -> int:
            """Helper function to find next free position in the cell.

            Args:
                pos (tuple(int,int)):
                    the cell in which to look for a free position.

            Returns:
                chosen (int):
                    chosen position.
            """
            if pos not in used:
                used[pos] = {i: 0 for i in range(9)}

            available_offsets = [i for i in range(9) if i not in used[pos]]

            if available_offsets:
                chosen = available_offsets[0]
            else:
                chosen = min(used[pos], key=used[pos].get)

            used[pos][chosen] += 1
            return chosen

        font = self.id_label_font.copy()

        # double the font size for mac
        sysmod = 2 if sys_platform == 'Darwin' else 1
        font.config(size=int(self.id_label_font.cget("size") * (adjusted_cell_size / 100) * sysmod))

        # draw the ids on all trains and their stations
        for index, row in self.train_data.iterrows():
            train_pos = row['start_pos']
            train_offset = assign_offset(train_pos)

            self.canvas.create_text(
                (self.x_offset + offset_dict[train_offset][0] + train_pos[
                    1] * adjusted_cell_size),
                (self.y_offset + offset_dict[train_offset][1] + train_pos[
                    0] * adjusted_cell_size),
                text=str(index),
                anchor="center",
                font=font,
                fill=self.train_color,
                tags="id_labels"
            )

            station_pos = row['end_pos']

            # if there is a station placed for this train
            if station_pos != (-1, -1):
                station_offset = assign_offset(station_pos)

                self.canvas.create_text(
                    (self.x_offset + offset_dict[station_offset][0] +
                     station_pos[1] * adjusted_cell_size),
                    (self.y_offset + offset_dict[station_offset][1] +
                     station_pos[0] * adjusted_cell_size),
                    text=str(index),
                    anchor="center",
                    font=font,
                    fill=self.station_color,
                    tags="id_labels"
                )

    def draw_images(self):
        """Place all images in the grid and measure timing."""
        self.draw_tracks()
        self.draw_trains()
        self.draw_stations()
        self.draw_id_labels()

    def draw_tracks(self):
        """Draw all tracks in the grid."""
        for row in range(self.rows):
            for col in range(self.cols):
                value = self.array[0][row, col]
                if value == 0:
                    continue
                else:
                    self.put_img_on_canvas(value, 0, row, col)

    def draw_trains(self):
        """Draw all unique train positions in the grid."""
        unique_rows = self.train_data.drop_duplicates(subset='start_pos')
        for _, row in unique_rows.iterrows():
            self.put_img_on_canvas(
                value=self.dir[row['dir']],
                layer=1,
                row=row['start_pos'][0],
                col=row['start_pos'][1]
            )

    def draw_stations(self):
        """Draw all unique station positions in the grid."""
        unique_rows = self.train_data.drop_duplicates(subset='end_pos')
        for _, row in unique_rows.iterrows():
            if row['end_pos'] != (-1, -1):
                self.put_img_on_canvas(
                    5,
                    2,
                    row=row['end_pos'][0],
                    col=row['end_pos'][1]
                )

    def zoom(self, event):
        """Calculate new scale and offset.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse wheel is scrolled.
        """
        scale_factor = 1.2 if event.delta > 0 else 0.8
        new_scale = self.scale * scale_factor

        max_limit = {
            # row/col threshold: zoom limit
            10: 3,
            50: 4.5,
            100: 5,
            200: 30,
            500: 60,
        }

        limit = max_limit[
            next(
                # find zoom limit for rows or cols <= threshold
                (k for k in sorted(max_limit) if max(self.rows, self.cols) <= k),
                max(max_limit)  # fallback if rows > 500
            )
        ]

        new_scale = max(0.1, min(new_scale, min(self.rows / limit, self.cols / limit)))

        grid_mouse_x = (event.x - self.x_offset) / self.scale
        grid_mouse_y = (event.y - self.y_offset) / self.scale

        self.x_offset -= (grid_mouse_x * new_scale - grid_mouse_x * self.scale)
        self.y_offset -= (grid_mouse_y * new_scale - grid_mouse_y * self.scale)

        self.scale = new_scale

        self.draw_grid()
        self.resize_images()
        self.draw_images()


class TrainListCanvas:
    """A custom tkinter Canvas to display a list of trains.

    Attributes:
        root (tk.Frame):
            The parent container of this canvas.
        width (int):
            specify the width of the canvas in pixel.
        height (int):
            specify the height of the canvas in pixel.
        x (int):
            specifies the x position of the canvas in the parent container.
        y (int):
            specifies the y position of the canvas in the parent container.
        base_font_layout (tk.font.Font):
            applied to the train labels and other texts on the canvas.
            Can be font family and font size.
            E.g. (family='Arial', size=20).
        err_font_layout (tk.font.Font):
            applied to the error texts on the canvas.
            Can be font family, font size and font style.
            E.g. (family='Arial', size=20, style='bold').
        title_font_layout (tk.font.Font):
            applied to the title texts on the canvas.
            Can be font family, font size and font style.
            E.g. (family='Arial', size=20, style='bold').
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        label_color (str):
            text color.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        button_color (str):
            background color of buttons
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        entry_color (str):
            background color of entry fields.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        input_color (str):
            color of text entered in the entry field.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        example_color (str):
            color of example text in the entry field.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        bad_status_color (str):
            color of error texts and some button texts.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        base_button_style_map (dict):
            style map for normal buttons.
        selector_button_style_map (dict):
            style map for station selector buttons.
        remove_button_style_map (dict):
            style map for remove buttons.
        border_width (int):
            width of the border around the canvas in pixel.
        grid (custom_canvas.BuildCanvas):
            holds a reference to the builder grid.
        train_data (pd.DataFrame):
            dataframe with all trains in the environment.
        windows (dict):
            holds references to the program window.
        frames (dict):
            holds references to the frames inside the program window.
        station_dict (dict):
            holds references to station selector buttons for each train.
        config_dict (dict):
            holds references to config buttons for each train.
        remove_dict (dict):
            holds references to remove buttons for each train.
        station_img (str):
            path to the image for stations.
        canvas (tk.Canvas):
            the actual canvas that is initialized internally with the
            passed parameters.
        scrollbar (tk.Scrollbar):
            the scrollbar of the list.
        scroll_frame (tk.Frame):
            this frame is made scrollable with the scrollbar.
    """
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            base_font_layout: Tuple[str, int],
            err_font_layout: Tuple[str, int, str],
            title_font_layout: Tuple[str, int, str],
            background_color: str,
            label_color: str,
            button_color: str,
            entry_color: str,
            input_color: str,
            example_color: str,
            bad_status_color: str,
            base_button_style_map: Dict[str, list],
            selector_button_style_map: Dict[str, list],
            remove_button_style_map: Dict[str, list],
            border_width: int,
            grid: BuildCanvas,
            train_data: pd.DataFrame,
            windows: dict,
            frames: dict,
    ):
        """Initializes a custom tkinter Canvas to display a list of trains.

        Displays a list of train labels and buttons to modify the train list.

        Args:
            root (tk.Frame):
                The parent container of this canvas.
            width (int):
                specify the width of the canvas in pixel.
            height (int):
                specify the height of the canvas in pixel.
            x (int):
                specifies the x position of the canvas in the parent container.
            y (int):
                specifies the y position of the canvas in the parent container.
            base_font_layout (tk.font.Font):
                applied to the train labels and other texts on the canvas.
                Can be font family and font size.
                E.g. (family='Arial', size=20).
            err_font_layout (tk.font.Font):
                applied to the error texts on the canvas.
                Can be font family, font size and font style.
                E.g. (family='Arial', size=20, style='bold').
            title_font_layout (tk.font.Font):
                applied to the title texts on the canvas.
                Can be font family, font size and font style.
                E.g. (family='Arial', size=20, style='bold').
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            label_color (str):
                text color.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            button_color (str):
                background color of buttons
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            entry_color (str):
                background color of entry fields.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            input_color (str):
                color of text entered in the entry field.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            example_color (str):
                color of example text in the entry field.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            bad_status_color (str):
                color of error texts and some button texts.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            base_button_style_map (dict):
                style map for normal buttons.
            selector_button_style_map (dict):
                style map for station selector buttons.
            remove_button_style_map (dict):
                style map for remove buttons.
            border_width (int):
                width of the border around the canvas in pixel.
            grid (custom_canvas.BuildCanvas):
                holds a reference to the builder grid.
            train_data (pd.DataFrame):
                dataframe with all trains in the environment.
            windows (dict):
                holds references to the program window.
            frames (dict):
                holds references to the frames inside the program window.
        """
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.base_font_layout = base_font_layout
        self.err_font_layout = err_font_layout
        self.title_font_layout = title_font_layout
        self.background_color = background_color
        self.label_color = label_color
        self.button_color = button_color
        self.entry_color = entry_color
        self.input_color = input_color
        self.example_color = example_color
        self.bad_status_color = bad_status_color
        self.base_button_style_map = base_button_style_map
        self.selector_button_style_map = selector_button_style_map
        self.remove_button_style_map = remove_button_style_map
        self.border_width = border_width
        self.grid = grid
        self.train_data = train_data
        self.windows = windows
        self.frames = frames

        self.train_frames = {}
        self.station_dict = {}
        self.label_dict = {}
        self.config_dict = {}
        self.remove_dict = {}

        self.station_img = 'data/png/Bahnhof_#d50000.png'

        self.canvas = self.create_canvas()
        self.pack_canvas()

        self.scrollbar = tk.Scrollbar(
            self.root, orient='vertical', command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_frame = tk.Frame(self.canvas, bg=self.background_color)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.scroll_frame.bind("<Configure>", self.on_frame_configure)
        self.scroll_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scroll_frame.bind('<Leave>', self._unbound_to_mousewheel)

        self.update_widget_rows()

    def create_canvas(self) -> tk.Canvas:
        """Initializes a tkinter canvas with the current attribute values.

        Returns:
            canvas (tk.Canvas):
                handle for the tkinter canvas.
        """
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def pack_canvas(self):  #
        """Packs canvas on the parent container at the specified position."""
        self.canvas.pack(side='top', padx=self.x, pady=self.y, anchor='nw')

    def update_widget_rows(self):
        """Updates labels and buttons for each train.

        Creates a new frame inside the scroll_frame for each train to hold its
        buttons and labels.

        Adds a station selection button for each train.
        Adds a label for each train.
        Adds a config button for each train.
        Adds a remove button for each train.
        """
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for index, row in self.train_data.iterrows():
            frame = tk.Frame(self.scroll_frame, bg=self.background_color)
            frame.pack(fill='x', pady=5)

            self.station_dict[index] = Button(
                root=frame,
                width=70,
                height=70,
                grid_pos=(index, 0),
                padding=(0, 0),
                command=lambda i=index: self.grid.select_station(i),
                image=self.station_img,
                foreground_color=self.background_color,
                background_color=self.background_color,
                border_width=0,
                visibility=True,
                style={'padding': (0, 0)},
                style_map=self.selector_button_style_map,
            )

            self.label_dict[index] = Label(
                root=frame,
                grid_pos=(index, 1),
                padding=(0, 0),
                text=f' Train {index}:   {row["start_pos"]},  {row["dir"]}',
                font=self.base_font_layout,
                foreground_color=self.label_color,
                background_color=self.background_color,
                visibility=True,
            )

            self.config_dict[index] = Button(
                root=frame,
                width=12,
                height=1,
                grid_pos=(index, 2),
                padding=(20, 0),
                command=lambda i=index: self.open_train_config_frame(i),
                text=f'Configure {index}',
                font=self.base_font_layout,
                foreground_color=self.label_color,
                background_color=self.button_color,
                border_width=0,
                visibility=True,
                style_map=self.base_button_style_map,
            )

            self.remove_dict[index] = Button(
                root=frame,
                width=7,
                height=1,
                grid_pos=(index, 3),
                padding=(0, 0),
                command=lambda i=index: self.remove_train(i),
                text=f'Remove',
                font=self.base_font_layout,
                foreground_color=self.bad_status_color,
                background_color=self.background_color,
                border_width=0,
                visibility=True,
                style_map=self.remove_button_style_map,
            )

    def add_widget_row(self, index):
        frame = tk.Frame(self.scroll_frame, bg=self.background_color)
        frame.pack(fill='x', pady=5)
        self.train_frames[index] = frame

        self.station_dict[index] = Button(
            root=frame,
            width=70,
            height=70,
            grid_pos=(index, 0),
            padding=(0, 0),
            command=lambda i=index: self.grid.select_station(i),
            image=self.station_img,
            foreground_color=self.background_color,
            background_color=self.background_color,
            border_width=0,
            visibility=True,
            style={'padding': (0, 0)},
            style_map=self.selector_button_style_map,
        )

        self.label_dict[index] = Label(
            root=frame,
            grid_pos=(index, 1),
            padding=(0, 0),
            text=f' Train {index}:   '
                 f'{self.train_data["start_pos"].iloc[index]},  '
                 f'{self.train_data["dir"].iloc[index]}',
            font=self.base_font_layout,
            foreground_color=self.label_color,
            background_color=self.background_color,
            visibility=True,
        )

        self.config_dict[index] = Button(
            root=frame,
            width=12,
            height=1,
            grid_pos=(index, 2),
            padding=(20, 0),
            command=lambda i=index: self.open_train_config_frame(i),
            text=f'Configure {index}',
            font=self.base_font_layout,
            foreground_color=self.label_color,
            background_color=self.button_color,
            border_width=0,
            visibility=True,
            style_map=self.base_button_style_map,
        )

        self.remove_dict[index] = Button(
            root=frame,
            width=7,
            height=1,
            grid_pos=(index, 3),
            padding=(0, 0),
            command=lambda i=index: self.remove_train(i),
            text=f'Remove',
            font=self.base_font_layout,
            foreground_color=self.bad_status_color,
            background_color=self.background_color,
            border_width=0,
            visibility=True,
            style_map=self.remove_button_style_map,
        )


    def on_frame_configure(self, event):
        """Configure the scroll_frame for scrolling.

        Args:
            event (tk.Event):
                event generated by the canvas when configured.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        """Bind scrolling to the train list when entering the canvas.

        Args:
            event (tk.Event):
                event generated by the canvas when entering the train list.
        """
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """Unbind scrolling from the train list when exiting the canvas.

        Args:
            event (tk.Event):
                event generated by the canvas when leaving the train list.
        """
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Scroll when using the mouse wheel.

        Args:
            event (tk.Event):
                event generated by the canvas when scrolling with the
                mousewheel.
        """
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def remove_train(self, index):
        """Remove a train from the train list.

        Args:
            index (int):
                index of teh train to be removed.
        """
        # get list of trains at the same grid position as the one to be deleted
        df = self.train_data[
            self.train_data['start_pos'] ==
            self.train_data['start_pos'].iloc[index]
        ]

        if len(df) == 1:
            # remove train from grid
            self.grid.array[1][
                self.train_data['start_pos'].iloc[index]
            ] = 0
        else:
            # drop index to be deleted
            df = df.drop(index)
            # get last index from remaining trains on the same position
            replacement = df.index[-1]
            # get the direction of that train
            new_dir = self.train_data['dir'].iloc[replacement]

            # replace the old trains direction in the grid
            self.grid.array[1][
                self.train_data['start_pos'].iloc[index]
            ] = self.grid.dir[new_dir]
            self.grid.draw_train(replacement)

        # if the train has a station placed
        if self.train_data['end_pos'].iloc[index] != (-1, -1):
            # get list of stations at the same position as the deleted one
            station_count = len(
                self.train_data[
                    self.train_data['end_pos'] ==
                    self.train_data['end_pos'].iloc[index]
                ]
            )

            # if there are no other stations at the grid pos remove the image
            if station_count == 1:
                self.grid.array[2][self.train_data['end_pos'].iloc[index]] = 0

        # update the train list
        self.train_data.drop(index, inplace=True)
        self.train_data.reset_index(drop=True, inplace=True)
        self.update_widget_rows()

        # update the train and station images as well as the id labels on the builder grid
        self.grid.update_image_storage()
        self.grid.draw_id_labels()

    def open_train_config_frame(self, index):
        """Builds the config frame for a single train.

        Args:
            index (int):
                index of the train to be configured.
        """
        config_frame = Frame(
            root=self.windows['flatland_window'].window,
            width=self.frames['train_builder_menu_frame'].width,
            height=self.frames['train_builder_menu_frame'].height,
            grid_pos=(0, 1),
            padding=(0, 0),
            sticky='nesw',
            background_color=self.background_color,
            border_width=0,
            visibility=True
        )

        Label(
            root=config_frame.frame,
            grid_pos=(0,0),
            padding=(100,(125,0)),
            columnspan=2,
            sticky='sw',
            text=f'Train {index}',
            font=self.title_font_layout,
            foreground_color=self.label_color,
            background_color=self.background_color,
            visibility=True,
        )

        Label(
            root=config_frame.frame,
            grid_pos=(1, 0),
            padding=(100, 0),
            sticky='sw',
            text=f'Earliest Departure:',
            font=self.base_font_layout,
            foreground_color=self.label_color,
            background_color=self.background_color,
            visibility=True,
        )

        ed_entry = EntryField(
            root=config_frame.frame,
            width=10,
            height=1,
            grid_pos=(1, 0),
            padding=(0, 0),
            sticky='se',
            text=f'e.g. 1',
            font=self.base_font_layout,
            foreground_color=self.input_color,
            background_color=self.entry_color,
            example_color=self.example_color,
            border_width=0,
            visibility=True,
        )

        # if there is already an earliest departure load the current value
        if self.train_data.loc[index, 'e_dep'] != -1:
            ed_entry.insert_string(str(self.train_data.loc[index, 'e_dep']))

        ed_err_label = Label(
            root=config_frame.frame,
            grid_pos=(1,1),
            padding=((50,0),0),
            sticky='sw',
            text='',
            font=self.err_font_layout,
            foreground_color=self.bad_status_color,
            background_color=self.background_color,
            visibility=True,
        )

        Label(
            root=config_frame.frame,
            grid_pos=(2, 0),
            padding=(100, 20),
            sticky='w',
            text=f'Latest Arrival:',
            font=self.base_font_layout,
            foreground_color=self.label_color,
            background_color=self.background_color,
            visibility=True,
        )

        la_entry = EntryField(
            root=config_frame.frame,
            width=10,
            height=1,
            grid_pos=(2, 0),
            padding=(0, 20),
            sticky='e',
            text=f'e.g. 200',
            font=self.base_font_layout,
            foreground_color=self.input_color,
            background_color=self.entry_color,
            example_color=self.example_color,
            border_width=0,
            visibility=True,
        )

        # if there is already a latest arrival load the current value
        if self.train_data.loc[index, 'l_arr'] != -1:
            la_entry.insert_string(str(self.train_data.loc[index, 'l_arr']))

        la_err_label = Label(
            root=config_frame.frame,
            grid_pos=(2,1),
            padding=((50,0),20),
            sticky='w',
            text='',
            font=self.err_font_layout,
            foreground_color=self.bad_status_color,
            background_color=self.background_color,
            visibility=True,
        )

        Label(
            root=config_frame.frame,
            grid_pos=(3, 0),
            padding=(100, (0,20)),
            sticky='w',
            text=f'Speed:',
            font=self.base_font_layout,
            foreground_color=self.label_color,
            background_color=self.background_color,
            visibility=True,
        )

        speed_entry = EntryField(
            root=config_frame.frame,
            width=10,
            height=1,
            grid_pos=(3, 0),
            padding=(0, (0,20)),
            sticky='e',
            text=f'e.g. 1',
            font=self.base_font_layout,
            foreground_color=self.input_color,
            background_color=self.entry_color,
            example_color=self.example_color,
            border_width=0,
            visibility=True,
        )

        # if there is already a speed load the current value
        if self.train_data.loc[index, 'speed'] != -1:
            speed_entry.insert_string(str(self.train_data.loc[index, 'speed']))

        speed_err_label = Label(
            root=config_frame.frame,
            grid_pos=(3, 1),
            padding=((50, 0), (0,20)),
            sticky='w',
            text='',
            font=self.err_font_layout,
            foreground_color=self.bad_status_color,
            background_color=self.background_color,
            visibility=True,
        )

        Button(
            root=config_frame.frame,
            width=20,
            height=1,
            grid_pos=(4, 0),
            padding=(100, 40),
            sticky='nw',
            columnspan=2,
            command=lambda: self.save_ed_la(
                index,
                ed_entry,
                la_entry,
                speed_entry,
                ed_err_label,
                la_err_label,
                speed_err_label,
                config_frame,
                True
            ),
            text='Save',
            font=self.base_font_layout,
            foreground_color=self.label_color,
            background_color=self.button_color,
            border_width=0,
            visibility=True,
            style_map=self.base_button_style_map,
        )

        config_frame.frame.rowconfigure((0, 4),weight=10)
        config_frame.frame.rowconfigure((1, 2), weight=1)
        config_frame.frame.columnconfigure((0, 1),weight=1)
        config_frame.frame.grid_propagate(False)

        self.windows['flatland_window'].window.update_idletasks()

    def save_ed_la(
            self,
            index,
            ed_entry,
            la_entry,
            speed_entry,
            ed_err_label,
            la_err_label,
            speed_err_label,
            config_frame,
            save
    ):
        """save the data entered in the config frame.

        Args:
            index (int):
                index of the configured train.
            ed_entry (custom_widgets.EntryField):
                reference to the entry field for earliest departure.
            la_entry (custom_widgets.EntryField):
                reference to the entry field for latest arrival.
            speed_entry (custom_widgets.EntryField):
                reference to the entry field for speed.
            ed_err_label (custom_widgets.Label):
                reference to the label for earliest departure errors.
            la_err_label (custom_widgets.Label):
                reference to the label for latest arrival errors.
            speed_err_label (custom_widgets.Label):
                reference to the label for speed errors.
            config_frame (custom_widgets.Frame):
                reference to the config_frame.
            save (bool):
                whether to save the entered parameters

        Returns:
            int: -1 if an error was registered, otherwise 0.
        """

        if not save:
            config_frame.destroy_frame()
            return 0

        # get the data from the entry field
        ed = ed_entry.entry_field.get()
        la = la_entry.entry_field.get()
        speed = speed_entry.entry_field.get()

        err_count = 0

        try:
            if ed.startswith('e.g.') or ed == '' or ed is None:
                ed = None
            else:
                ed = int(ed)

            # hide label if there was no problem with the data conversion
            ed_err_label.hide_label()
        except ValueError:
            # register the error and display corresponding error message
            ed_err_label.label.config(
                text='needs int > 0',
                fg=self.bad_status_color,
            )
            ed_err_label.place_label()
            err_count += 1

        try:
            if la.startswith('e.g.') or la == '' or la is None:
                la = None
            else:
                la = int(la)

            # hide label if there was no problem with the data conversion
            la_err_label.hide_label()
        except ValueError:
            # register the error and display corresponding error message
            la_err_label.label.config(
                text='needs int > 0',
                fg=self.bad_status_color,
            )
            la_err_label.place_label()
            err_count += 1

        try:
            if speed.startswith('e.g.') or speed == '' or speed is None:
                speed = None
            else:
                speed = int(speed)

            # hide label if there was no problem with the data conversion
            speed_err_label.hide_label()
        except ValueError:
            # register the error and display corresponding error message
            speed_err_label.label.config(
                text='needs int > 0',
                fg=self.bad_status_color,
            )
            speed_err_label.place_label()
            err_count += 1

        if err_count:
            return -1

        if ed is not None:
            # check for additional constrains and display error when violated
            if ed < 1:
                ed_err_label.label.config(
                    text='needs int > 0',
                    fg=self.bad_status_color,
                )
                ed_err_label.place_label()
                err_count += 1
            else:
                self.train_data.loc[index, 'e_dep'] = ed
        else:
            self.train_data.loc[index, 'e_dep'] = -1

        if la is not None:
            # check for additional constrains and display error when violated
            if la < 1:
                la_err_label.label.config(
                    text='needs int > 0',
                    fg=self.bad_status_color,
                )
                la_err_label.place_label()
                err_count += 1
            else:
                self.train_data.loc[index, 'l_arr'] = la
        else:
            self.train_data.loc[index, 'l_arr'] = -1

        if speed is not None:
            # check for additional constrains and display error when violated
            if speed < 1:
                speed_err_label.label.config(
                    text='needs int > 0',
                    fg=self.bad_status_color,
                )
                speed_err_label.place_label()
                err_count += 1
            else:
                self.train_data.loc[index, 'speed'] = speed
        else:
            self.train_data.loc[index, 'speed'] = -1

        if err_count:
            return -1

        config_frame.destroy_frame()


class ResultCanvas:
    """A custom tkinter Canvas to display solved environments.

    Attributes:
        root (tk.Frame):
            The parent container of this canvas.
        width (int):
            specify the width of the canvas in pixel.
        height (int):
            specify the height of the canvas in pixel.
        x (int):
            specifies the x position of the canvas in the parent container.
        y (int):
            specifies the y position of the canvas in the parent container.
        font (tk.font.Font):
            applied to the grid label and mouse text on the canvas.
            Can be font family and font size.
            E.g. (family='Arial', size=20).
        path_label_font (tk.font.Font):
            applied to the path labels the canvas.
            Can be font family and font size.
            E.g. (family='Arial', size=20).
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        grid_color (str):
            is applied t o the grid lines and if enabled the grid labels.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the canvas in pixel.
        image (str):
            path to an image file. Will be displayed on the canvas.
        display_image (ImageTk.PhotoImage):
            holds the image that is displayed on the canvas.
        canvas_image (int):
            holds the object id of the image on the canvas.
        canvas (tk.Canvas):
            the actual canvas that is initialized internally with the
            passed parameters.
        rows (int):
            specifies how many rows the grid should have.
        cols (int):
            specifies how many columns the grid should have.
        pan_start (tuple(int,int)):
            holds the initial mouse position when panning.
        x_offset (int):
            grid and image offset in x direction on the canvas.
        y_offset (int):
            grid and image offset in y direction on the canvas.
        cell_size (int):
            holds the current cell_size of the grid.
        scale (float):
            holds the current zoom level.
        buffer_factor(float):
            holds the factor of how much the buffer is larger than
            the visible area of the canvas image.
        self.buffer_x(int):
            holds the x coordinate of the top left corner of the
            buffer area.
        self.buffer_y(int):
            holds the y coordinate of the top left corner of the
            buffer area.
        text_label (int):
            holds the object id of the mouse coordinates text.
        high_quality_render(int):
            Holds the Tkinter id of the scheduled high-quality image update.
        draw_grid_numbers(bool):
            whether to draw row and col numbers on the outside of the canvas.
        paths_df (pd.DataFrame):
            dataframe holding the locations of each train at each time step.
        show_df (pd.DataFrame):
            subset dataframe of paths_df holding only the trains to be shown.
        show_list (list(bool)):
            keeps track which trains to show.
    """
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            font: Tuple[str, int],
            path_label_font: Tuple[str, int],
            background_color: str,
            grid_color: str,
            border_width: int,
            image: str,
            rows: int,
            cols: int,
            paths_df: pd.DataFrame,
    ):
        """Initializes a custom tkinter Canvas to display solved environments.

        Draws the grid and environment image on the initial position.
        Draw Paths from the solution.

        Args:
            root (tk.Frame):
                The parent container of this canvas.
            width (int):
                specify the width of the canvas in pixel.
            height (int):
                specify the height of the canvas in pixel.
            x (int):
                specifies the x position of the canvas in the parent container.
            y (int):
                specifies the y position of the canvas in the parent container.
            font (tk.font.Font):
                applied to the grid label and mouse text on the canvas.
                Can be font family and font size.
                E.g. (family='Arial', size=20).
            path_label_font (tk.font.Font):
                applied to the path labels the canvas.
                Can be font family and font size.
                E.g. (family='Arial', size=20).
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            grid_color (str):
                is applied t o the grid lines and if enabled the grid labels.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the canvas in pixel.
            image (str):
                path to an image file. Will be displayed on the canvas.
            rows (int):
                specifies how many rows the grid should have.
            cols (int):
                specifies how many columns the grid should have.
            paths_df (pd.DataFrame):
                dataframe holding the locations of each train at each time step.
        """
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.font = font
        self.path_label_font = path_label_font
        self.background_color = background_color
        self.grid_color = grid_color
        self.border_width = border_width

        self.image = self.get_image(image)
        self.display_image = None
        self.canvas_image = None

        self.canvas = self.create_canvas()
        self.place_canvas()

        # populate canvas
        self.rows = rows
        self.cols = cols
        self.pan_start = (0, 0)
        self.x_offset = 0
        self.y_offset = 0
        self.cell_size = 50
        self.scale = 1.0
        self.buffer_factor = 0.5
        self.buffer_x = 0
        self.buffer_y = 0
        self.text_label = None
        self.high_quality_render = None

        # draw grid labels
        self.draw_grid_numbers = False

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.root.after(100, self.initial_zoom)

        self.paths_df = paths_df
        self.show_df = pd.DataFrame(
            columns=['trainID','start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
        )
        self.show_list = []

    def create_canvas(self) -> tk.Canvas:
        """Initializes a tkinter canvas with the current attribute values.

        Returns:
            canvas (tk.Canvas):
                handle for the tkinter canvas.
        """
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def place_canvas(self):  #
        """Places canvas on the parent container at the specified position."""
        self.canvas.place(x=self.x, y=self.y)

    @staticmethod
    def get_image(image_path) -> Image.Image:
        """Load an image and convert it to a format usable by tkinter.

        Crops out the white border created automatically by Flatland.

        Args:
            image_path (str):
                file path to the image.

        Returns:
            image (Image.Image):
                processed image, formatted for use in Tkinter widgets.
        """
        image = Image.open(image_path)
        crop_box = (0, 0, image.width - 4, image.height - 4)
        image = image.crop(crop_box)
        return image

    def draw_mouse_symbols(self, event):
        """Draw the coordinates of the current grid cell next to the cursor.

        Args:
            event (tk.Event):
                event generated by the canvas when the mouse is inside its
                boundaries.
        """
        # get the dimensions of the grid
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # if inside the grid place the text next to the cursor
        if 0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height:
            row = int(adjusted_y / self.cell_size)
            col = int(adjusted_x / self.cell_size)
            coords_text = f"[{row}, {col}]"

            # place or move the text label
            if self.text_label is None:
                self.text_label = self.canvas.create_text(
                    event.x + 10, event.y + 10,  # Position next to the cursor
                    text=coords_text,
                    font=self.font,
                    fill="#000000",  # Text color
                    anchor="nw"
                )
            else:
                self.canvas.itemconfig(self.text_label, text=coords_text)
                self.canvas.coords(self.text_label, event.x + 10, event.y + 10)
        else:
            # remove the coordinates on leaving the canvas
            self.canvas.delete(self.text_label)
            self.text_label = None

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse leaves the canvas
                boundaries.
        """
        self.canvas.delete(self.text_label)
        self.text_label = None

    def draw_grid(self):
        """Draw the grid lines on the canvas."""
        self.canvas.delete("grid_line")
        adjusted_cell_size = self.cell_size * self.scale

        if adjusted_cell_size < 8:
            return

        for row in range(self.rows + 1):
            self.canvas.create_line(
                self.x_offset,
                self.y_offset + row * adjusted_cell_size,
                self.x_offset + self.cols * adjusted_cell_size,
                self.y_offset + row * adjusted_cell_size,
                fill=self.grid_color,
                width=(adjusted_cell_size / 100) * (1 / self.scale),
                tags='grid_line',
            )

        for col in range(self.cols + 1):
            self.canvas.create_line(
                self.x_offset + col * adjusted_cell_size,
                self.y_offset,
                self.x_offset + col * adjusted_cell_size,
                self.y_offset + self.rows * adjusted_cell_size,
                fill=self.grid_color,
                width=(adjusted_cell_size / 100) * (1 / self.scale),
                tags='grid_line',
            )

        if self.draw_grid_numbers:
            self.draw_grid_labels()

    def draw_grid_labels(self):
        """Draw the row and column labels next to the grid."""
        self.canvas.delete("grid_label")
        adjusted_cell_size = self.cell_size * self.scale

        font = self.font.copy()
        font.config(size=int(self.font.cget("size") * adjusted_cell_size * 0.02))

        for row in range(self.rows):
            self.canvas.create_text(
                self.x_offset - 10,
                (self.y_offset + row * adjusted_cell_size) +
                adjusted_cell_size / 2,
                text=str(row),
                anchor="e",
                font=font,
                fill=self.grid_color,
                tags="grid_label"
            )

        for col in range(self.cols):
            self.canvas.create_text(
                (self.x_offset + col * adjusted_cell_size) +
                adjusted_cell_size,
                self.y_offset - adjusted_cell_size,
                text=str(col),
                angle=90,
                anchor="s",
                font=font,
                fill=self.grid_color,
                tags="grid_label"
            )

    def initial_zoom(self):
        """Calculate the initial position of the image centred on the canvas."""
        if self.rows > self.cols:
            self.cell_size = (self.canvas.winfo_height() * 0.8) / self.rows
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2
            self.draw_grid()
            self.draw_image()
        else:
            self.cell_size = (self.canvas.winfo_width() * 0.8) / self.cols
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2
            self.draw_grid()
            self.draw_image()

    def zoom(self, event):
        """Calculate new scale and offset.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse wheel is scrolled.
        """
        scale_factor = 1.2 if event.delta > 0 else 0.8
        new_scale = self.scale * scale_factor

        new_scale  = max(1/2, min(new_scale, max(self.rows/3, self.cols/3)))

        grid_mouse_x = (event.x - self.x_offset) / self.scale
        grid_mouse_y = (event.y - self.y_offset) / self.scale

        self.x_offset -= (grid_mouse_x * new_scale - grid_mouse_x * self.scale)
        self.y_offset -= (grid_mouse_y * new_scale - grid_mouse_y * self.scale)

        self.scale = new_scale

        self.draw_image()
        self.draw_paths()

    def start_pan(self, event):
        """Get the initial mouse position when panning.

         Args:
            event (tk.Event):
                event generated by the canvas when left mouse button is pressed.
        """
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        """Calculate new offset and moves the grid and image.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse is moved while holding
                the left mouse button.
        """
        # compute the mouse movement
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        # shift the offsets and update the pan_start location
        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        # move the canvas objects
        self.canvas.move("env_image", dx, dy)
        self.canvas.move("grid_line", dx, dy)
        self.canvas.move("grid_label", dx, dy)
        self.canvas.move("path_labels", dx, dy)

        # re-render the visible area if the new area is outside the buffer zone
        if self._check_buffer_boundary():
            self.draw_image()

    def _check_buffer_boundary(self) -> bool:
        """Check if the visible area is still within the buffer zone.

        Returns:
            bool (boolean):
                whether the visible area is outside the buffer zone.
        """

        env_width, env_height = self.get_env_size()

        # check if the image is not loaded yet
        if env_width == -1:
            return False

        # get canvas size
        canvas_width, canvas_height = self.get_canvas_size()

        # check if canvas is not loaded
        if canvas_width == -1:
            return False

        # determine corner points of the visible area
        view_left, view_top, view_right, view_bottom = self.get_visible_area(
            env_width, env_height, canvas_width, canvas_height
        )

        # stop if the visible area is flipped or non-existing
        if view_left == -1:
            return False

        # compute buffer zone
        buf_left = self.buffer_x
        buf_top = self.buffer_y
        buf_right = buf_left + int(canvas_width * self.buffer_factor)
        buf_bottom = buf_top + int(canvas_height * self.buffer_factor)

        # check if the visible area is outside the buffer zone
        margin = 10
        if view_left < buf_left + margin:
            return True
        if view_top < buf_top + margin:
            return True
        if view_right > buf_right - margin:
            return True
        if view_bottom > buf_bottom - margin:
            return True

        return False

    def get_env_size(self) -> Tuple[int, int]:
        """Calculate the width and height of the environment grid.

        Returns:
            env_width (int):
                width of the environment grid. -1 if the image is not yet loaded.
            env_height (int):
                height of the environment grid. -1 if the image is not yet loaded.
        """
        # compute environment grid size
        env_width = int(self.cols * self.cell_size * self.scale)
        env_height = int(self.rows * self.cell_size * self.scale)

        # reload if the image is not loaded yet
        if env_width <= 0 or env_height <= 0:
            self.root.after(100, self.initial_zoom)
            return -1, -1
        else:
            return env_width, env_height

    def get_canvas_size(self) -> Tuple[int, int]:
        """Calculate the width and height of the canvas.

        Returns:
            canvas_width (int):
                width of the canvas. -1 if the canvas is not yet loaded.
            canvas_height (int):
                height of the canvas. -1 if the canvas is not yet loaded.
        """
        # get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # reload if canvas is not loaded
        if canvas_width <= 0 or canvas_height <= 0:
            return -1, -1
        else:
            return canvas_width, canvas_height

    def get_visible_area(self, env_width, env_height, canvas_width, canvas_height) -> Tuple[int, int, int, int]:
        """Calculate the corner points of the visible area.

        Args:
            env_width (int):
                width of the environment grid.
            env_height (int):
                height of the environment grid.
            canvas_width (int):
                width of the canvas.
            canvas_height (int):
                height of the canvas.

        Returns:
            vis_left (int):
                x coordinate of the top left corner of the visible area.
                -1 if the visible area is flipped or non-existing.
            vis_top (int):
                y coordinate of the top left corner of the visible area.
                -1 if the visible area is flipped or non-existing.
            vis_right (int):
                x coordinate of the bottom right corner of the visible area.
                -1 if the visible area is flipped or non-existing.
            vis_bottom (int):
                y coordinate of the bottom right corner of the visible area.
                -1 if the visible area is flipped or non-existing.
        """
        # determine corner points of the visible area
        vis_left = max(0, -int(self.x_offset))
        vis_top = max(0, -int(self.y_offset))
        vis_right = min(env_width, canvas_width - int(self.x_offset))
        vis_bottom = min(env_height, canvas_height - int(self.y_offset))

        # stop if the visible area is flipped or non-existing
        if vis_left >= vis_right or vis_top >= vis_bottom:
            return -1, -1, -1, -1
        else:
            return vis_left, vis_top, vis_right, vis_bottom

    def get_visible_projection_on_image(
            self,
            env_width,
            env_height,
            vis_left,
            vis_top,
            vis_right,
            vis_bottom
    ) -> Tuple[Union[Image.Image, None], int, int]:
        """Calculate the projection of the visible area on the original image.

        Args:
            env_width (int):
                width of the environment grid.
            env_height (int):
                height of the environment grid.
            vis_left (int):
                x coordinate of the top left corner of the visible area.
            vis_top (int):
                y coordinate of the top left corner of the visible area.
            vis_right (int):
                x coordinate of the bottom right corner of the visible area.
            vis_bottom (int):
                y coordinate of the bottom right corner of the visible area.

        Returns:
            region (Image.Image):
                projection of the visible area on the original image.
                None if the visible area is non-existing.
            vis_width (int):
                width of the visible area.
                -1 if the visible area is non-existing.
            vis_height (int):
                height of the visible area.
                -1 if the visible area is non-existing.
        """
        # get original image dimensions and get the scale factor relative to the modified image
        base_w, base_h = self.image.size
        sx = env_width / base_w
        sy = env_height / base_h

        # calculate visible are projected onto original image
        src_left = int(vis_left / sx)
        src_top = int(vis_top / sy)
        src_right = int(vis_right / sx)
        src_bottom = int(vis_bottom / sy)

        # crop the original image to the visible area projected onto it
        region = self.image.crop((src_left, src_top, src_right, src_bottom))

        # get the width and height of the visible area
        vis_width = int(vis_right - vis_left)
        vis_height = int(vis_bottom - vis_top)

        # stop if the new visible area is non-existing
        if vis_width <= 0 or vis_height <= 0:
            return None, -1, -1
        else:
            return region, vis_width, vis_height

    def draw_image(self):
        """Display the image on the canvas and adjust to the current scale"""

        # compute environment size
        env_width, env_height = self.get_env_size()

        # reload if the image is not loaded yet
        if env_width == -1:
            return

        # get canvas size
        canvas_width, canvas_height = self.get_canvas_size()

        # reload if canvas is not loaded
        if canvas_width == -1:
            return

        # determine corner points of the visible area
        vis_left, vis_top, vis_right, vis_bottom = self.get_visible_area(
            env_width, env_height, canvas_width, canvas_height
        )

        # stop if the visible area is flipped or non-existing
        if vis_left == -1:
            return

        # calculate buffer zone size
        buf_w = int(canvas_width * self.buffer_factor)
        buf_h = int(canvas_height * self.buffer_factor)

        # center the buffer around the visible area
        center_x = (vis_left + vis_right) // 2
        center_y = (vis_top + vis_bottom) // 2
        buf_left = max(0, center_x - buf_w // 2)
        buf_top = max(0, center_y - buf_h // 2)
        buf_right = min(env_width, buf_left + buf_w)
        buf_bottom = min(env_height, buf_top + buf_h)

        # update buffer x and y anchor to the centered coordinates of the top left corner
        self.buffer_x = buf_right - buf_w if buf_right - buf_w > 0 else buf_left
        self.buffer_y = buf_bottom - buf_h if buf_bottom - buf_h > 0 else buf_top

        # get cropped region and the dimensions of the visible are projected on the original image
        region, vis_width, vis_height = self.get_visible_projection_on_image(
            env_width, env_height, vis_left, vis_top, vis_right, vis_bottom
        )

        # stop if the new visible area is non-existing
        if vis_width == -1:
            return

        # resize the cropped image to the visible area using NEAREST interpolation
        visible_img = region.resize((vis_width, vis_height), Image.NEAREST)
        self.display_image = ImageTk.PhotoImage(visible_img)

        # determine location of top left corner for the resized image
        canvas_x = max(int(self.x_offset), 0)
        canvas_y = max(int(self.y_offset), 0)

        if self.canvas_image is None:
            # place the image object on the canvas
            self.canvas_image = self.canvas.create_image(
                canvas_x,
                canvas_y,
                anchor="nw",
                image=self.display_image,
                tags='env_image'
            )
        else:
            # update the image object on the canvas and move it to the correct coordinates
            self.canvas.itemconfig(self.canvas_image, image=self.display_image)
            self.canvas.coords(self.canvas_image, canvas_x, canvas_y)

        # update the size of the interactive area of the canvas
        self.canvas.config(scrollregion=(0, 0, env_width, env_height))
        self.draw_grid()

        # schedule high quality render or reschedule on new zoom command
        if self.high_quality_render:
            self.root.after_cancel(self.high_quality_render)
        self.high_quality_render = self.root.after(
            500, self.render_image_high_quality
        )

    def render_image_high_quality(self):
        """Render the full image with high quality."""
        # start worker thread to resize the original image
        threading.Thread(
            target=self._hq_resize_thread,
            args=(),
            daemon=True
        ).start()

    def _hq_resize_thread(self):
        """Resize the image to the new size according to the current zoom level."""
        # compute environment size
        env_width, env_height = self.get_env_size()

        # get canvas size
        canvas_width, canvas_height = self.get_canvas_size()

        # determine corner points of the visible area
        vis_left, vis_top, vis_right, vis_bottom = self.get_visible_area(
            env_width, env_height, canvas_width, canvas_height
        )

        if vis_left == -1:
            return

        # get cropped region and the dimensions of the visible are projected on the original image
        region, vis_width, vis_height = self.get_visible_projection_on_image(
            env_width, env_height, vis_left, vis_top, vis_right, vis_bottom
        )

        # stop if the new visible area is non-existing
        if vis_width == -1:
            return

        # resize the image with LANCZOS interpolation
        hq_image = region.resize((vis_width, vis_height), Image.LANCZOS)

        # determine location of top left corner for the resized image
        canvas_x = max(int(self.x_offset), 0)
        canvas_y = max(int(self.y_offset), 0)

        # change to main thread and place the high quality image on the canvas
        self.root.after(
            10,
            lambda: self._place_hq_image(hq_image, canvas_x, canvas_y, env_width, env_height),
        )

    def _place_hq_image(self, hq_image, canvas_x, canvas_y, env_width, env_height):
        """Place the high quality image on the canvas.

        Args:
            hq_image (Image.Image):
                image to be placed.
            canvas_x (int):
                x coordinate of the top left corner of the canvas.
            canvas_y (int):
                y coordinate of the top left corner of the canvas.
            env_width (int):
                width of the environment grid.
            env_height (int):
                height of the environment grid.
        """
        # convert image to tk format
        self.display_image = ImageTk.PhotoImage(hq_image)

        # update the image object on the canvas and move it to the correct coordinates
        self.canvas.itemconfig(self.canvas_image, image=self.display_image)
        self.canvas.coords(self.canvas_image, canvas_x, canvas_y)

        # update the size of the interactive area of the canvas
        self.canvas.config(scrollregion=(0, 0, env_width, env_height))
        self.draw_grid()

    def update_paths(self):
        """Update what paths to show based on the show-list.

        PathListCanvas updates show_list and calls this function.
        """
        show_dict = dict(zip(self.paths_df['trainID'].unique(), self.show_list))

        self.show_df = (self.paths_df[self.paths_df['trainID'].map(show_dict)]
                        .copy())

        self.show_df['count'] = (self.show_df.groupby(['x', 'y'])['x']
                                 .transform('count'))

        self.show_df['cell_offset'] = (self.show_df.groupby(['x', 'y'])
                                       .cumcount()
                                       .where(self.show_df['count'] > 1, 0) % 9)

        self.show_df.drop(columns=['count'], inplace=True)

        self.draw_paths()

    def draw_paths(self):
        """Draw the paths calculated in the solution."""
        self.canvas.delete("path_labels")
        adjusted_cell_size = self.cell_size * self.scale

        # manage multiple ids in the same grid cell
        # position label on a 3x3 grid in each cell to avoid overlay
        # 0 is the center position 1 is on the left and then go clockwise
        offset_dict = {
            0: (adjusted_cell_size * 0.5, adjusted_cell_size * 0.5),
            1: (adjusted_cell_size * 0.2, adjusted_cell_size * 0.5),
            2: (adjusted_cell_size * 0.2, adjusted_cell_size * 0.2),
            3: (adjusted_cell_size * 0.5, adjusted_cell_size * 0.2),
            4: (adjusted_cell_size * 0.8, adjusted_cell_size * 0.2),
            5: (adjusted_cell_size * 0.8, adjusted_cell_size * 0.5),
            6: (adjusted_cell_size * 0.8, adjusted_cell_size * 0.8),
            7: (adjusted_cell_size * 0.5, adjusted_cell_size * 0.8),
            8: (adjusted_cell_size * 0.2, adjusted_cell_size * 0.8),
        }

        colors = (
                AGENT_COLORS * ((len(self.paths_df) // len(AGENT_COLORS)) + 1)
        )
        train_colors = dict(zip(self.paths_df['trainID'].unique(), colors))

        font = self.path_label_font.copy()
        sysmod = 2 if sys_platform == 'Darwin' else 1   # double the font size for mac

        # if there is more than one path displayed shrink the font by  2/3
        if len(self.show_df['trainID'].unique()) > 1:
            font.config(size=int(self.path_label_font.cget("size") * (adjusted_cell_size / 100) * (2/3) * sysmod))
        else:
            font.config(size=int(self.path_label_font.cget("size") * (adjusted_cell_size / 100) * sysmod))

        # draw each train position for each timestep
        for _, row in self.show_df.iterrows():
            self.canvas.create_text(
                (self.x_offset + row['x'] * adjusted_cell_size +
                 offset_dict[row['cell_offset']][0]),
                (self.y_offset + row['y'] * adjusted_cell_size +
                 offset_dict[row['cell_offset']][1]),
                text=row['timestep'],
                anchor="center",
                font=font,
                fill=train_colors[row['trainID']],
                tags="path_labels"
            )


class PathListCanvas:
    """A custom tkinter Canvas to display a list of trains.

    Attributes:
        root (tk.Frame):
            The parent container of this canvas.
        width (int):
            specify the width of the canvas in pixel.
        height (int):
            specify the height of the canvas in pixel.
        x (int):
            specifies the x position of the canvas in the parent container.
        y (int):
            specifies the y position of the canvas in the parent container.
        font (tk.font.Font):
            applied to the train labels and other texts on the canvas.
            Can be font family and font size.
            E.g. (family='Arial', size=20).
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        on_color (str):
            on color for switch
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        off_color (str):
            off color for switch.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        handle_color (str):
            handle color for the switch.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        label_color (str):
            text color.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the canvas in pixel.
        train_data (pd.DataFrame):
            dataframe with all trains in the environment.
        grid (custom_canvas.ResultCanvas):
            holds a reference to the result grid.
        show_button_dict (dict):
            holds references to switches for each train to show or hide their
            paths.
        show_list (list(bool)):
            keeps track which trains to show.
        current_all (bool):
            determines if to show or hide all trains when toggle all is called.
        canvas (tk.Canvas):
            the actual canvas that is initialized internally with the
            passed parameters.
        scrollbar (tk.Scrollbar):
            the scrollbar of the list.
        scroll_frame (tk.Frame):
            this frame is made scrollable with the scrollbar.
    """
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            font: Tuple[str, int],
            background_color: str,
            on_color: str,
            off_color: str,
            handle_color: str,
            label_color: str,
            border_width: int,
            train_data: pd.DataFrame,
            grid: ResultCanvas,
    ):
        """Initializes a custom tkinter Canvas to display a list of trains.

        Displays a list of train labels and buttons to show their paths on the
        Result canvas.

        Args:
            root (tk.Frame):
                The parent container of this canvas.
            width (int):
                specify the width of the canvas in pixel.
            height (int):
                specify the height of the canvas in pixel.
            x (int):
                specifies the x position of the canvas in the parent container.
            y (int):
                specifies the y position of the canvas in the parent container.
            font (tk.font.Font):
                applied to the train labels and other texts on the canvas.
                Can be font family and font size.
                E.g. (family='Arial', size=20).
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            on_color (str):
                on color for switch
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            off_color (str):
                off color for switch.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            handle_color (str):
                handle color for the switch.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            label_color (str):
                text color.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the canvas in pixel.
            train_data (pd.DataFrame):
                dataframe with all trains in the environment.
            grid (custom_canvas.ResultCanvas):
                holds a reference to the result grid.
        """
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.font = font
        self.background_color = background_color
        self.on_color = on_color
        self.off_color = off_color
        self.handle_color = handle_color
        self.label_color = label_color
        self.border_width = border_width
        self.train_data = train_data
        self.grid = grid

        self.show_button_dict = {}
        self.show_list = [False] * len(self.train_data)
        self.current_all = False

        self.canvas = self.create_canvas()
        self.pack_canvas()

        self.scrollbar = tk.Scrollbar(
            self.root, orient='vertical', command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_frame = tk.Frame(self.canvas, bg=self.background_color)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.scroll_frame.bind("<Configure>", self.on_frame_configure)
        self.scroll_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scroll_frame.bind('<Leave>', self._unbound_to_mousewheel)

        self.add_labels()

    def create_canvas(self) -> tk.Canvas:
        """Initializes a tkinter canvas with the current attribute values.

        Returns:
            canvas (tk.Canvas):
                handle for the tkinter canvas.
        """
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def pack_canvas(self):  #
        """Packs canvas on the parent container at the specified position."""
        self.canvas.pack(side='top', padx=self.x, pady=self.y, anchor='nw')

    def add_labels(self):
        """Updates labels and switches for each train.

        Creates a new frame inside the scroll_frame for each train to hold its
        label and switch.

        Adds a label for each train.
        Adds a switch for each train.
        """
        colors = (
                AGENT_COLORS *
                ((len(self.train_data) // len(AGENT_COLORS)) + 1)
        )

        for index, (idx, row) in enumerate(self.train_data.iterrows()):
            frame = tk.Frame(self.scroll_frame, bg=self.background_color)
            frame.pack(fill='x', pady=5)

            self.show_button_dict[index] = ToggleSwitch(
                frame,
                width=70, height=30,
                on_color=self.on_color, off_color=self.off_color,
                handle_color=self.handle_color,
                background_color=self.background_color,
                command=lambda i=index: self.toggle_path(i)
            )
            self.show_button_dict[index].pack(side='left', padx=0)

            label = tk.Label(
                frame,
                width=20, font=self.font,
                fg=colors[index], bg=self.background_color,
                text=f'Train {idx}: {row["start_pos"]}, {row["dir"]}',
                anchor='w',
            )
            label.pack(side='left', padx=10)

    def on_frame_configure(self, event):
        """Configure the scroll_frame for scrolling.

        Args:
            event (tk.Event):
                event generated by the canvas when configured.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        """Bind scrolling to the train list when entering the canvas.

        Args:
            event (tk.Event):
                event generated by the canvas when entering the train list.
        """
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """Unbind scrolling from the train list when exiting the canvas.

        Args:
            event (tk.Event):
                event generated by the canvas when leaving the train list.
        """
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Scroll when using the mouse wheel.

        Args:
            event (tk.Event):
                event generated by the canvas when scrolling with the
                mousewheel.
        """
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def toggle_all_paths(self):
        """Toggle all paths according to current_all.

        Update show_list and the paths in the result canvas.
        """
        if len(self.show_list) == 0:
            return

        self.current_all = all(self.show_list)

        if self.current_all:
            for i in self.show_button_dict:
                self.show_list = [False] * len(self.show_list)
                # set all switches to false
                self.show_button_dict[i].set_state(False)
            self.current_all = False
        else:
            for i in self.show_button_dict:
                self.show_list = [True] * len(self.show_list)
                # set all switches to true
                self.show_button_dict[i].set_state(True)
            self.current_all = True

        self.grid.show_list = self.show_list
        self.grid.update_paths()

    def toggle_path(self, index):
        """Toggle a single train path.

        Update show_list and the paths in the result canvas.

        Args:
            index (int):
                the index of the train whose path to show.
        """
        if self.show_list[index]:
            self.show_list[index] = False
        else:
            self.show_list[index] = True

        self.grid.show_list = self.show_list
        self.grid.update_paths()
