"""Provides custom variations of standard Tkinter classes.

Includes custom variations of Window, Frame, Button, Label, Entry and Text.

Example usage:
    import custom_widgets

    window = custom_widgets.Window(
        width=10,
        height=10,
        title='Window',
        background_color='#000000',
        fullscreen=False
    )
"""

import platform
import warnings
import tkinter as tk
from tkinter import ttk
from typing import Union, Tuple, Dict, List

from PIL import Image, ImageTk, ImageDraw, ImageSequence


# Platform:
sys_platform = platform.system()


class Window:
    """A customized Tkinter Window.

    Attributes:
        width (int):
            specify the width of the window in pixel.
        height (int):
            specify the height of the window in pixel.
        title (str):
            title of th window. will also be displayed on the window border when
            not in fullscreen.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        fullscreen (bool):
            whether to display the window in fullscreen mode or not.
        window (tk.Tk):
            the actual tkinter window that is initialized internally with the
            passed parameters.
        screenwidth (int):
            width of the screen the window is displayed on in pixel.
        screenheight (int):
            height of the screen the window is displayed on in pixel.
    """
    def __init__(
            self,
            width: Union[int, None],
            height: Union[int, None],
            title: str,
            background_color: str,
            fullscreen: bool = False,
    ):
        """Initializes a custom window with the passed parameters.

        Creates a fullscreen window if called with fullscreen = True otherwise
        creates a window with the specified width and height or with half the
        screenwidth and screenheight if width and height are not specified.

        Args:
            width (int):
                specify the width of the window in pixel.
            height (int):
                specify the height of the window in pixel.
            title (str):
                title of th window. will also be displayed on the window border when
                not in fullscreen.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            fullscreen (bool):
                whether to display the window in fullscreen mode or not.
        """
        self.width = width
        self.height = height#
        self.title = title
        self.background_color = background_color
        self.fullscreen = fullscreen

        self.window = self.create_window()

        self.window.update_idletasks()

        self.screenwidth = self.window.winfo_screenwidth()
        self.screenheight = self.window.winfo_screenheight()

        if self.fullscreen:
            # set window to fullscreen
            self.window.attributes("-fullscreen", self.fullscreen)
        elif self.width is None or self.height is None:
            # if no width or height is given use half the screenwidth and height
            self.window.geometry(
                f'{self.screenwidth//2}x{self.screenheight//2}'
            )
        else:
            # use specified width and height
            self.window.geometry(f'{self.width}x{self.height}')

    def create_window(self) -> tk.Tk:
        """Initializes a tkinter window with the current attribute values.

        Returns:
            window (tk.TK):
                the handle of the tkinter window.
        """
        window = tk.Tk()
        window.title(self.title)
        window.configure(bg=self.background_color)
        return window

    def close_window(self):
        """Closes the window and all contained objects."""
        self.window.quit()

    def run(self):
        """Start the main event loop of the window."""
        self.window.mainloop()

    def toggle_fullscreen(self):
        """Toggle the state of the window between fullscreen and windowed mode.

        Sets the fullscreen attribute to the opposite of its current value.
        For the windowed mode use either the width and height or screenwidth and
        screenheight if one or both are unspecified.
        """
        self.fullscreen = not self.fullscreen
        self.window.attributes("-fullscreen", self.fullscreen)
        if not self.fullscreen:
            if self.width is None or self.height is None:
                # if no width or height is given use screenwidth and height
                self.window.geometry(
                    f"{self.screenwidth // 2}x{self.screenheight // 2}"
                )
            else:
                # use specified width and height
                self.window.geometry(f"{self.width}x{self.height}")


class Frame:
    """A customized Tkinter Frame.

    Attributes:
        root (tk.Tk):
            The parent container of this frame.
        width (int):
            specify the width of the frame in pixel.
        height (int):
            specify the height of the frame in pixel.
        grid_pos (tuple[int,int]): the position, as row and column, of the frame
            in the parent container.
        padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
            additional padding on the horizontal and vertical axis,
            either a single int or a tuple of ints. A single int will
            be applied to both sides of the object while a tuple
            allows for different a paddings on either side,
            e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
            5 pixel above and below the object.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the frame in pixel.
        visibility (bool):
            whether to display the frame on initialization or not.
        sticky (str):
            specify the directions the frame should stick to. E.g. 'ew' will
            stretch the frame from east to west. Use cardinal directions.
        columnspan (int):
            specify over how many grid columns this object can be placed.
        frame (tk.Frame):
            the actual tkinter frame that is initialized internally with the
            passed parameters.
    """
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            grid_pos: Tuple[int, int],
            padding: Union[
                Tuple[int, int],
                Tuple[Tuple[int, int], Tuple[int, int]],
                Tuple[int, Tuple[int, int]],
                Tuple[Tuple[int, int], int]
            ],
            background_color: str,
            border_width: int,
            visibility: bool,
            sticky: Union[str, None] = None,
            columnspan: Union[int, None] = None,
    ):
        """Initializes a custom frame with the passed parameters.

        Puts the frame on the parent container if visibility is True.

        Args:
            root (tk.Tk):
                The parent container of this frame.
            width (int):
                specify the width of the frame in pixel.
            height (int):
                specify the height of the frame in pixel.
            grid_pos (tuple[int,int]): the position, as row and column, of the
                frame in the parent container.
            padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
                additional padding on the horizontal and vertical axis,
                either a single int or a tuple of ints. A single int will
                be applied to both sides of the object while a tuple
                allows for different a paddings on either side,
                e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
                5 pixel above and below the object.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the frame in pixel.
            visibility (bool):
                whether to display the frame on initialization or not.
            sticky (str):
                specify the directions the frame should stick to. E.g. 'ew' will
                stretch the frame from east to west. Use cardinal directions.
            columnspan (int):
                specify over how many grid columns this object can be placed.
        """
        self.root = root
        self.width = width
        self.height = height
        self.grid_pos = grid_pos
        self.padding = padding
        self.sticky = sticky
        self.columnspan = columnspan
        self.background_color = background_color
        self.border_width = border_width
        self.visibility = visibility

        self.frame = self.create_frame()

        if visibility:
            self.place_frame()

    def create_frame(self) -> tk.Frame:
        """Initializes a tkinter Frame with the current attribute values.

        Returns:
            frame (tk.Frame):
                handle for the tkinter frame.
        """
        frame = tk.Frame(
            self.root,
            bg=self.background_color,
            bd=self.border_width,
            width=self.width,
            height=self.height,
        )
        return frame

    def place_frame(self):
        """Places the frame on the parent container at the specified position.

        Sets the visibility attribute to true.
        Uses current grid_pos, padding, sticky and columnspan attribute values.
        """
        self.frame.grid(
            row=self.grid_pos[0], column=self.grid_pos[1],
            padx=self.padding[0], pady=self.padding[1],
            sticky=self.sticky, columnspan=self.columnspan,
        )
        self.visibility = True

    def destroy_frame(self):
        """Destroys the tkinter frame object.

        Sets the visibility attribute to False.
        """
        self.visibility = False
        self.frame.destroy()

    def toggle_visibility(self):
        """Places the frame with the current attribute values or hides it.

        Depends on current visibility value.
        Sets visibility attribute to the opposite of its current value.
        """
        if self.visibility:
            self.frame.grid_forget()
            self.visibility = False
        else:
            self.frame.grid(
                row=self.grid_pos[0], column=self.grid_pos[1],
                padx=self.padding[0], pady=self.padding[1],
                sticky=self.sticky, columnspan=self.columnspan,
            )
            self.visibility = True


class Button:
    """A custom tkinter Button.

    Attributes:
        root (tk.Frame):
            The parent container of this button.
        width (int):
            specify the width of the button in pixel.
        height (int):
            specify the height of the button in pixel.
        grid_pos (tuple[int,int]): the position, as row and column, of the
            button in the parent container.
        padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
            additional padding on the horizontal and vertical axis,
            either a single int or a tuple of ints. A single int will
            be applied to both sides of the object while a tuple
            allows for different a paddings on either side,
            e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
            5 pixel above and below the object.
        command (callable):
            executed on button press.
        foreground_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the button in pixel.
        visibility (bool):
            whether to display the button on initialization or not.
        sticky (str):
            specify the directions the button should stick to. E.g. 'ew' will
            stretch the button from east to west. Use cardinal directions.
        columnspan (int):
            specify over how many grid columns this object can be placed.
        text (str):
            displayed on the button.
        font (tk.font.Font):
            applied to the text on the button. Can be font family and font size
            or font family, font size, and font style.
            E.g. (family='Arial', size=20, style='bold').
        image (str):
            path to an image file. Will be displayed on the button.
        rotation (int):
            rotation in degrees (0-360) of the image on the button.
        style_config (Union[Dict[str, Union[str, int, Tuple]]]):
            dictionary with ttk.Button style options that will be applied to
            the button.
        style_map_config (Union[Dict[str, list]]):
            dictionary with ttk.Button style map options that will be applied to
            the button.
        button (ttk.Button):
            the actual ttk.Button that is initialized internally with the
            passed parameters.
    """
    def __init__(
            self,
            root,
            width: int,
            height: int,
            grid_pos: Tuple[int, int],
            padding: Union[
                Tuple[int, int],
                Tuple[Tuple[int, int], Tuple[int, int]],
                Tuple[int, Tuple[int, int]],
                Tuple[Tuple[int, int], int]
            ],
            command: callable,
            foreground_color: str,
            background_color: str,
            border_width: int,
            visibility: bool,
            sticky: Union[str, None] = None,
            columnspan: Union[int, None] = None,
            text: Union[str, None] = None,
            font: Union[
                Tuple[str, int],
                Tuple[str, int, str],
                None
            ] = None,
            image: Union[str, None] = None,
            rotation: Union[int, None] = 0,
            style: Union[Dict[str, Union[str, int, Tuple]], None] = None,
            style_map: Union[Dict[str, list], None] = None
    ):
        """Initializes a custom button with the passed parameters.

        Puts the button on the parent container if visibility is True.

        Args:
            root (tk.Frame):
                The parent container of this button.
            width (int):
                specify the width of the button in pixel.
            height (int):
                specify the height of the button in pixel.
            grid_pos (tuple[int,int]): the position, as row and column, of the
                button in the parent container.
            padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
                additional padding on the horizontal and vertical axis,
                either a single int or a tuple of ints. A single int will
                be applied to both sides of the object while a tuple
                allows for different a paddings on either side,
                e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
                5 pixel above and below the object.
            command (callable):
                executed on button press.
            foreground_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the button in pixel.
            visibility (bool):
                whether to display the button on initialization or not.
            sticky (str):
                specify the directions the button should stick to. E.g. 'ew'
                will stretch the frame from east to west. Use cardinal
                directions.
            columnspan (int):
                specify over how many grid columns this object can be placed.
            text (str):
                displayed on the button.
            font (tk.font.Font):
                applied to the text on the button. Can be font family and font size
                or font family, font size, and font style.
                E.g. (family='Arial', size=20, style='bold').
            image (str):
                path to an image file. Will be displayed on the button.
            rotation (int):
                rotation in degrees (0-360) of the image on the button.
            style (Union[Dict[str, Union[str, int, Tuple]]]):
                dictionary with ttk.Button style options that will be applied to
                the button.
            style_map (Union[Dict[str, list]]):
                dictionary with ttk.Button style map options that will be applied to
                the button.
        """
        self.root = root
        self.width = width
        self.height = height
        self.grid_pos = grid_pos
        self.padding = padding
        self.sticky = sticky
        self.columnspan = columnspan
        self.command = command
        self.font = font
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.border_width = border_width
        self.visibility = visibility
        self.text = text
        self.image = image
        self.rotation = rotation
        self.style_config = style if style else {}
        self.style_map_config = style_map if style_map else {}

        if self.image:
            self.image = self.get_image(self.image)

        self.button = self.create_button()

        if visibility:
            self.place_button()

    def create_button(self) -> ttk.Button:
        """Initializes a tkinter ttk.Button with the current attribute values.

        Returns:
            button (ttk.Button):
                handle for the ttk.button.
        """
        # Create a custom style for the button
        style = ttk.Style()
        style.theme_use('clam')
        style_name = f"Custom.TButton.{id(self)}"

        style.configure(
            style_name,
            foreground=self.foreground_color,
            background=self.background_color,
            borderwidth=self.border_width
        )

        # Use style and style map to configure the button if they are given
        for key, value in self.style_config.items():
            style.configure(style_name, **{key: value})

        for key, value in self.style_map_config.items():
            style.map(style_name, **{key: value})

        # Use the standard layout of the ttk.Button
        style.layout(style_name, style.layout("TButton"))

        if self.text:
            # Text configuration

            # apply font config if given
            if self.font:
                style.configure(style_name, font=self.font)

            style.configure(
                style_name,
                padding=(self.width * 2, self.height * 10)
            )

            button = ttk.Button(
                self.root,
                text=self.text,
                command=self.command,
                style=style_name
            )
        elif self.image:
            # Image configuration

            button = ttk.Button(
                self.root,
                image=self.image,
                command=self.command,
                style=style_name
            )
        else:
            # Raise a warning if neither image nor text is provided
            warnings.warn('No text or image given to Button', UserWarning)
            return None
        return button

    def place_button(self):
        """Places the button on the parent container at the specified position.

        Sets the visibility attribute to true.
        Uses current grid_pos, padding, sticky and columnspan attribute values.
        """
        self.button.grid(
            row=self.grid_pos[0],
            column=self.grid_pos[1],
            padx=self.padding[0],
            pady=self.padding[1],
            sticky=self.sticky,
            columnspan=self.columnspan,
        )
        self.visibility = True

    def toggle_visibility(self):
        """Places the button with the current attribute values or hides it.

        Depends on current visibility value.
        Sets visibility attribute to the opposite of its current value.
        """
        if self.visibility:
            self.button.grid_forget()
            self.visibility = False
        else:
            self.button.grid(
                row=self.grid_pos[0],
                column=self.grid_pos[1],
                padx=self.padding[0],
                pady=self.padding[1],
                sticky=self.sticky,
                columnspan=self.columnspan,
            )
            self.visibility = True

    def get_image(self, image_path) -> ImageTk.PhotoImage:
        """Load an image and convert it to a format usable by tkinter.

        Rotates and resizes the image to the button width and height.

        Args:
            image_path (str):
                file path to the image.

        Returns:
            image (ImageTk.PhotoImage):
                processed image, formatted for use in Tkinter widgets.
        """
        image = Image.open(image_path)
        image = image.resize(size=(self.width, self.height))
        image = image.rotate(angle=self.rotation)
        image = ImageTk.PhotoImage(image)
        return image


class Label:
    """A custom tkinter Label.

    Attributes:
        root (tk.Frame):
            The parent container of this label.
        grid_pos (tuple[int,int]): the position, as row and column, of the label
            in the parent container.
        padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
            additional padding on the horizontal and vertical axis,
            either a single int or a tuple of ints. A single int will
            be applied to both sides of the object while a tuple
            allows for different a paddings on either side,
            e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
            5 pixel above and below the object.
        text (str):
            displayed on the label.
        font (tk.font.Font):
            applied to the text on the label. Can be font family and font size
            or font family, font size, and font style.
            E.g. (family='Arial', size=20, style='bold').
        foreground_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        visibility (bool):
            whether to display the label on initialization or not.
        sticky (str):
            specify the directions the label should stick to. E.g. 'ew' will
            stretch the label from east to west. Use cardinal directions.
        columnspan (int):
            specify over how many grid columns this object can be placed.
        label (tk.Label):
            the actual label that is initialized internally with the
            passed parameters.
    """
    def __init__(
            self,
            root,
            grid_pos: Tuple[int, int],
            padding: Union[
                Tuple[int, int],
                Tuple[Tuple[int, int], Tuple[int, int]],
                Tuple[int, Tuple[int, int]],
                Tuple[Tuple[int, int], int]
            ],
            text: str,
            font: Union[
                Tuple[str, int],
                Tuple[str, int, str],
            ],
            foreground_color: str,
            background_color: str,
            visibility: bool,
            sticky: Union[str, None] = None,
            columnspan: Union[int, None] = None,
    ):
        """Initializes a custom tkinter Label.

        Puts the label on the parent container if visibility is True.

        Args:
            root (tk.Frame):
                The parent container of this label.
            grid_pos (tuple[int,int]): the position, as row and column, of the
                label in the parent container.
            padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
                additional padding on the horizontal and vertical axis,
                either a single int or a tuple of ints. A single int will
                be applied to both sides of the object while a tuple
                allows for different a paddings on either side,
                e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
                5 pixel above and below the object.
            text (str):
                displayed on the label.
            font (tk.font.Font):
                applied to the text on the label. Can be font family and font size
                or font family, font size, and font style.
                E.g. (family='Arial', size=20, style='bold').
            foreground_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            visibility (bool):
                whether to display the label on initialization or not.
            sticky (str):
                specify the directions the label should stick to. E.g. 'ew' will
                stretch the label from east to west. Use cardinal directions.
            columnspan (int):
                specify over how many grid columns this object can be placed.
        """
        self.root = root
        self.grid_pos = grid_pos
        self.padding = padding
        self.sticky = sticky
        self.columnspan = columnspan
        self.text = text
        self.font = font
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.visibility = visibility

        self.label = self.create_label()

        if visibility:
            self.place_label()

    def create_label(self) -> tk.Label:
        """Initializes a tkinter label with the current attribute values.

        Returns:
            label (tk.Label):
                handle for the tkinter label.
        """
        label = tk.Label(
            self.root,
            text=self.text, font=self.font,
            fg=self.foreground_color, bg=self.background_color
        )
        return label

    def place_label(self):
        """Places the label on the parent container at the specified position.

        Sets the visibility attribute to true.
        Uses current grid_pos, padding, sticky and columnspan attribute values.
        """
        self.label.grid(
            row=self.grid_pos[0], column=self.grid_pos[1],
            padx=self.padding[0], pady=self.padding[1],
            sticky=self.sticky, columnspan=self.columnspan,
        )
        self.visibility = True

    def hide_label(self):
        """Hides the label and sets the visibility attribute to False."""
        self.label.grid_forget()
        self.visibility = False

    def toggle_visibility(self):
        """Places the label with the current attribute values or hides it.

        Depends on current visibility value.
        Sets visibility attribute to the opposite of its current value.
        """
        if self.visibility:
            self.label.grid_forget()
            self.visibility = False
        else:
            self.label.grid(
                row=self.grid_pos[0], column=self.grid_pos[1],
                padx=self.padding[0], pady=self.padding[1],
                sticky=self.sticky, columnspan=self.columnspan,
            )
            self.visibility = True


class GIF:
    """A custom GIF class based on a tkinter Label.

    Attributes:
        root (tk.Frame):
            The parent container of this GIF.
        width (int):
            specify the width of the GIF in pixel.
        height (int):
            specify the height of the GIF in pixel.
        grid_pos (tuple[int,int]): the position, as row and column, of the GIF
            in the parent container.
        padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
            additional padding on the horizontal and vertical axis,
            either a single int or a tuple of ints. A single int will
            be applied to both sides of the object while a tuple
            allows for different a paddings on either side,
            e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
            5 pixel above and below the object.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        visibility (bool):
            whether to display the GIF on initialization or not.
        sticky (str):
            specify the directions the GIF should stick to. E.g. 'ew' will
            stretch the GIF from east to west. Use cardinal directions.
        columnspan (int):
            specify over how many grid columns this object can be placed.
        corner_radius (int):
            specifies the radius of the corners of the GIF in pixel.
        frames (list[ImageTk.PhotoImage]):
            holds the individual images of the GIF.
        delay (int):
            the delay between frames in milliseconds.
        frame_index (int):
            holds the current frame index.
        label (tk.Label):
            the actual GIF that is initialized internally with the
            passed parameters.
    """
    def __init__(
            self,
            root,
            width: int,
            height: int,
            grid_pos: Tuple[int, int],
            padding: Union[
                Tuple[int, int],
                Tuple[Tuple[int, int], Tuple[int, int]],
                Tuple[int, Tuple[int, int]],
                Tuple[Tuple[int, int], int]
            ],
            gif: str,
            background_color: str,
            visibility: bool,
            sticky: Union[str, None] = None,
            columnspan: Union[int, None] = None,
    ):
        """Initializes a custom GIF class based on a tkinter Label.

        Puts the GIF on the parent container and starts the animation
        if visibility is True.

        Args:
            root (tk.Frame):
                The parent container of this GIF.
            width (int):
                specify the width of the GIF in pixel.
            height (int):
                specify the height of the GIF in pixel.
            grid_pos (tuple[int,int]): the position, as row and column, of the GIF
                in the parent container.
            padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
                additional padding on the horizontal and vertical axis,
                either a single int or a tuple of ints. A single int will
                be applied to both sides of the object while a tuple
                allows for different a paddings on either side,
                e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
                5 pixel above and below the object.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            visibility (bool):
                whether to display the GIF on initialization or not.
            sticky (str):
                specify the directions the GIF should stick to. E.g. 'ew' will
                stretch the GIF from east to west. Use cardinal directions.
            columnspan (int):
                specify over how many grid columns this object can be placed.
        """
        self.root = root
        self.width = width
        self.height = height
        self.grid_pos = grid_pos
        self.padding = padding
        self.sticky = sticky
        self.columnspan = columnspan
        self.background_color = background_color
        self.visibility = visibility

        self.corner_radius = 20
        self.frames, self.delay = self.get_gif(gif)
        self.frame_index = 0

        self.label = self.create_label()

        if visibility:
            self.place_label()
            self.update_animation()

    def create_label(self) -> tk.Label:
        """Initializes a tkinter label with the current attribute values.

        Returns:
            label (tk.Label):
                handle for the tkinter label.
        """
        label = tk.Label(
            self.root,
            image=self.frames[0],
            width=self.width, height=self.height,
            bg=self.background_color
        )
        return label

    def place_label(self):
        """Places the label on the parent container at the specified position.

        Sets the visibility attribute to true.
        Uses current grid_pos, padding, sticky and columnspan attribute values.
        """
        self.label.grid(
            row=self.grid_pos[0], column=self.grid_pos[1],
            padx=self.padding[0], pady=self.padding[1],
            sticky=self.sticky, columnspan=self.columnspan,
        )
        self.visibility = True

    def hide_label(self):
        """Hides the label and sets the visibility attribute to False."""
        self.label.grid_forget()
        self.visibility = False

    def toggle_visibility(self):
        """Places the label with the current attribute values or hides it.

        Depends on current visibility value.
        Sets visibility attribute to the opposite of its current value.
        """
        if self.visibility:
            self.label.grid_forget()
            self.visibility = False
        else:
            self.label.grid(
                row=self.grid_pos[0], column=self.grid_pos[1],
                padx=self.padding[0], pady=self.padding[1],
                sticky=self.sticky, columnspan=self.columnspan,
            )
            self.visibility = True
        return

    def get_gif(self, gif_path: str) -> Tuple[List[ImageTk.PhotoImage], int]:
        """Extracts individual frames and delay from the original GIF.

        Extracts individual frames, rescales them to the size specified by the
        current attributes and rounds off the corners.

        Args:
            gif_path (str):
                path to the GIF.

        Returns:
            frames (list[ImageTk.PhotoImage]):
                list of the individual images of the GIF.
            delay (int):
                the delay between frames in milliseconds.
        """
        gif = Image.open(gif_path)
        frames = []
        delay = gif.info.get("duration", 100)

        # rescale the GIF to the size specified by the current attributes
        original_width, original_height = gif.size
        scale = min(self.width / original_width, self.height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        try:
            while True:
                # extract the individual frames
                frame = gif.copy().convert("RGBA")
                frame = frame.resize(
                    (new_width, new_height),
                    Image.Resampling.LANCZOS
                )
                # round off corners
                frame = self.round_corners(frame, self.corner_radius)

                # add to list of frames
                frames.append(ImageTk.PhotoImage(frame))

                # Move to the next frame
                gif.seek(len(frames))
        except EOFError:
            pass
        return frames, delay

    @staticmethod
    def round_corners(img: Image.Image, radius: int) -> Image.Image:
        """Rounds off the corners of an image.

        Args:
            img (Image.Image):
                the image whose corner should be rounded off.
            radius (int):
                the radius of the corners.

        Returns:
            img (Image.Image):
                the image with its corners rounded off.
        """
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)

        draw.rounded_rectangle((0, 0, img.width, img.height), radius=radius,
                               fill=255)
        img.putalpha(mask)
        return img

    def update_animation(self):
        """Start the animation of the GIF.

        Put the first frame with the current index in the Label.
        Increment the index by one unless the last frame is reached then go back
        to 0. After the delay time, specified by the delay attribute call this
        function again.
        """
        if self.frames:
            self.label.config(image=self.frames[self.frame_index])
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.label.after(self.delay, self.update_animation)


class ZoomableGIF:
    """A custom zoomable GIF class based on a tkinter Canvas.

    Attributes:
        root (tk.Frame):
            The parent container of this GIF.
        width (int):
            specify the width of the GIF in pixel.
        height (int):
            specify the height of the GIF in pixel.
        grid_pos (tuple[int,int]): the position, as row and column, of the GIF
            in the parent container.
        padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
            additional padding on the horizontal and vertical axis,
            either a single int or a tuple of ints. A single int will
            be applied to both sides of the object while a tuple
            allows for different a paddings on either side,
            e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
            5 pixel above and below the object.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        visibility (bool):
            whether to display the GIF on initialization or not.
        sticky (str):
            specify the directions the GIF should stick to. E.g. 'ew' will
            stretch the GIF from east to west. Use cardinal directions.
        columnspan (int):
            specify over how many grid columns this object can be placed.
        canvas (tk.Canvas):
            the actual GIF that is initialized internally with the
            passed parameters.
        gif (Image.Image):
            the displayed GIF
        rows (int):
            specifies how many rows the GIF has.
        cols (int):
            specifies how many columns the GIF has.
        pan_start_coord (tuple(int,int)):
            holds the initial mouse position when panning.
        scale (float):
            holds the current zoom level.
        offset_x (int):
            GIF offset in x direction on the canvas.
        offset_y (int):
            GIF offset in y direction on the canvas.
        zooming (bool):
            keeps track if currently a zoom process is in action.
        zoom_end (int):
            holds an event id when zooming to end the zoom process.
        cached_frames (dict[float, List[ImageTk.PhotoImage]]):
            holds scale values as a key for the individually cached GIF images.
        frames (list[ImageTk.PhotoImage]):
            holds the individual images of the GIF.
        durations (list[int]):
            the delays between frames in milliseconds.
        current_frame_index (int):
            holds the current frame index.
        animate_id (int):
            holds an event id when animating to end the animation.
        orig_size (tuple(int,int)):
            keeps track of the original GIF size.
        image (int):
            holds the id of the image object on the canvas where the GIF is
            placed.
    """
    def __init__(
        self,
        root,
        width: int,
        height: int,
        grid_pos: Tuple[int, int],
        padding: Union[
            Tuple[int, int],
            Tuple[Tuple[int, int], Tuple[int, int]],
            Tuple[int, Tuple[int, int]],
            Tuple[Tuple[int, int], int]
        ],
        gif: str,
        rows: int,
        cols: int,
        background_color: str,
        visibility: bool,
        sticky: Union[str, None] = None,
        columnspan: Union[int, None] = None,
    ):
        """Initializes a custom GIF class based on a tkinter Canvas.

        Puts the GIF on the internal canvas and puts the canvas on the
        parent container.
        Also starts the animation if visibility is True.

        Args:
            root (tk.Frame):
                The parent container of this GIF.
            width (int):
                specify the width of the GIF in pixel.
            height (int):
                specify the height of the GIF in pixel.
            grid_pos (tuple[int,int]): the position, as row and column, of the GIF
                in the parent container.
            padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
                additional padding on the horizontal and vertical axis,
                either a single int or a tuple of ints. A single int will
                be applied to both sides of the object while a tuple
                allows for different a paddings on either side,
                e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
                5 pixel above and below the object.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            visibility (bool):
                whether to display the GIF on initialization or not.
            sticky (str):
                specify the directions the GIF should stick to. E.g. 'ew' will
                stretch the GIF from east to west. Use cardinal directions.
            columnspan (int):
                specify over how many grid columns this object can be placed.
        """
        self.root = root
        self.width = width
        self.height = height
        self.grid_pos = grid_pos
        self.padding = padding
        self.sticky = sticky
        self.columnspan = columnspan
        self.background_color = background_color
        self.visibility = visibility

        self.canvas = self.create_canvas()
        self.gif = Image.open(gif)

        self.rows = rows
        self.cols = cols
        self.pan_start_coord = (0, 0)
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.zooming = False
        self.zoom_end = None
        self.zoom_index = 0
        self.zoom_levels = []
        self.zoom_factors = [1, 1.5, 2] # discrete zoom levels
        self.modify_zoom_levels()

        self.cached_frames = {}
        self.frames = []
        self.durations = []
        self.current_frame_index = 0
        self.animate_id = None

        # Load frames with their duration
        for frame in ImageSequence.Iterator(self.gif):
            self.frames.append(frame.convert("RGBA"))
            self.durations.append(frame.info.get("duration", 100))
        self.orig_size = self.frames[0].size

        # Ensure the GIF will not run when quitting the program
        self.gif.close()
        self.image = self.canvas.create_image(self.offset_x, self.offset_y, anchor="nw")

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)

        if sys_platform == "Darwin":
            # different right mouse button labeling
            self.canvas.bind("<ButtonPress-2>", self.pan_start_event)
            self.canvas.bind("<B2-Motion>", self.pan)

            # back-up using control and left mouse click
            self.canvas.bind("<Control-ButtonPress-1>", self.pan_start_event)
            self.canvas.bind("<Control-B1-Motion>", self.pan)
        else:
            self.canvas.bind("<ButtonPress-3>", self.pan_start_event)
            self.canvas.bind("<B3-Motion>", self.pan)

        if visibility:
            self.place_canvas()
            self.calculate_initial_pos()

    def create_canvas(self) -> tk.Canvas:
        """Initializes a tkinter canvas with the current attribute values.

        Returns:
            canvas (tk.Canvas):
                handle for the tkinter canvas.
        """
        canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.background_color,
            highlightthickness=0
        )
        return canvas

    def place_canvas(self):
        """Places the canvas on the parent container at the specified position.

        Sets the visibility attribute to true.
        Uses current grid_pos, padding, sticky and columnspan attribute values.
        """
        self.canvas.grid(
            row=self.grid_pos[0],
            column=self.grid_pos[1],
            padx=self.padding[0],
            pady=self.padding[1],
            sticky=self.sticky,
            columnspan=self.columnspan,
        )
        self.visibility = True

    def _center_gif(self, scale: float):
        """Centers the GIF on the canvas for a given scale."""
        orig_width, orig_height = self.orig_size
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        self.offset_x = (self.canvas.winfo_width() - new_width) // 2
        self.offset_y = (self.canvas.winfo_height() - new_height) // 2

    def calculate_initial_pos(self):
        """Calculates the initial GIF position base on its size."""
        self.root.update_idletasks()

        orig_width, orig_height = self.orig_size
        scale_x = self.canvas.winfo_width() * 0.8 / orig_width
        scale_y = self.canvas.winfo_height() * 0.8 / orig_height
        self.scale = min(scale_x, scale_y)

        self._center_gif(self.scale)

        # Build absolute zoom levels from standard view
        self.zoom_levels = [self.scale * f for f in self.zoom_factors]
        self.zoom_index = 0

        self.update_image()
        self.animate()

    def animate(self):
        """Animate the GIF."""
        # go to next frame and update the canvas with this frame
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
        self.update_image()

        # Delay to ensure correct durations
        delay = self.durations[self.current_frame_index]
        self.animate_id = self.root.after(delay, self.animate)

    def stop(self):
        """Stop animation and cancel all pending after calls."""
        if self.zoom_end is not None:
            self.root.after_cancel(self.zoom_end)
            self.zoom_end = None
        if self.animate_id is not None:
            self.root.after_cancel(self.animate_id)
            self.animate_id = None

    def zoom(self, event):
        """Calculate new scale and offset.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse wheel is scrolled.
        """
        if getattr(event, "delta", 0) != 0:
            # Check direction for Windows/Mac
            direction = 1 if event.delta > 0 else -1
        else:
            # Check direction for Linux
            direction = 1 if event.num == 4 else -1

        new_index = self.zoom_index + direction

        # no zooming out beyond full env view
        new_index = max(0, min(new_index, len(self.zoom_levels) - 1))

        # if at max zoom level
        if new_index == self.zoom_index:
            return

        new_scale = self.zoom_levels[new_index]

        if new_index == 0:
            # recenter if at max zoom level
            self.scale = new_scale
            self._center_gif(new_scale)
        else:
            # zoom centered on curser
            mouse_x = (event.x - self.offset_x) / self.scale
            mouse_y = (event.y - self.offset_y) / self.scale

            self.offset_x = event.x - mouse_x * new_scale
            self.offset_y = event.y - mouse_y * new_scale

            self.scale = new_scale

        self.zoom_index = new_index

        # set zooming to True for 200 milliseconds
        # this will make update_image() use a faster resampling method
        self.zooming = True
        if self.zoom_end is not None:
            self.root.after_cancel(self.zoom_end)
        self.zoom_end = self.root.after(200, self.end_zoom)
        
        self.update_image()

    def modify_zoom_levels(self):
        """Add and Remove zoom levels if the environment is larger than a certain threshold."""
        # rows/cols threshold: new zoom factor
        possible_additions = {
            10: 4,
            30: 8,
            200: 16,
            800: 32,
        }
        possible_removal_thresholds = [30, 200]

        max_dim = max(self.rows, self.cols)

        # add zoom levels
        self.zoom_factors.extend(
            factor for threshold, factor in possible_additions.items() if max_dim > threshold
        )

        #remove zoom levels
        [self.zoom_factors.pop(1) for threshold in possible_removal_thresholds if max_dim > threshold]

    def end_zoom(self):
        """End the zooming state."""
        self.zooming = False
        self.zoom_end = None
        self.update_image()

    def pan_start_event(self, event):
        """Get the initial mouse position when panning.

         Args:
            event (tk.Event):
                event generated by the canvas when left mouse button is pressed.
        """
        self.pan_start_coord = (event.x, event.y)

    def pan(self, event):
        """Calculate new offset and move the GIF image.

        Args:
            event (tk.Event):
                event generated by the canvas when mouse is moved while holding
                the left mouse button.
        """
        dx = event.x - self.pan_start_coord[0]
        dy = event.y - self.pan_start_coord[1]
        self.offset_x += dx
        self.offset_y += dy
        # update coords to the end coordinates of the panning
        self.pan_start_coord = (event.x, event.y)
        self.update_image()

    def update_image(self):
        """Updates the currently displayed image on the canvas."""
        key = round(self.scale, 4)

        # if the frames don't exist in the current zoom level resizes them
        if key not in self.cached_frames:
            resized_frames = []
            # use a faster resampling method while actively zooming
            resample_method = Image.Resampling.NEAREST \
                if self.zooming else Image.Resampling.LANCZOS

            # resize the frames in the GIF to the specified size
            for frame in self.frames:
                new_width = int(frame.width * self.scale)
                new_height = int(frame.height * self.scale)
                resized_frame = frame.resize((new_width, new_height), resample=resample_method)
                resized_frames.append(ImageTk.PhotoImage(resized_frame))

            # cache the resized frames
            self.cached_frames[key] = resized_frames

        # display the current frame on the canvas
        canvas_gif = self.cached_frames[key][self.current_frame_index]
        self.canvas.itemconfig(self.image, image=canvas_gif)
        self.canvas.coords(self.image, self.offset_x, self.offset_y)


class EntryField:
    """A custom tkinter Entry.

    Attributes:
        root (tk.Frame):
            The parent container of this entry field.
        width (int):
            specify the width of the entry field in pixel.
        height (int):
            specify the height of the entry field in pixel.
        grid_pos (tuple[int,int]): the position, as row and column, of the
            entry field in the parent container.
        padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
            additional padding on the horizontal and vertical axis,
            either a single int or a tuple of ints. A single int will
            be applied to both sides of the object while a tuple
            allows for different a paddings on either side,
            e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
            5 pixel above and below the object.
        text (str):
            displayed on the entry field as an example. Will be removed once
            the entry filed is selected. Will be replaced if the entry field
            is unselected and no text is entered.
        font (tk.font.Font):
            applied to the text on the entry field. Can be font family and
            font size or font family, font size, and font style.
            E.g. (family='Arial', size=20, style='bold').
        foreground_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        example_color (str):
            Will be applied to the example text when nothing is entered.
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the entry field in pixel.
        visibility (bool):
            whether to display the entry field on initialization or not.
        sticky (str):
            specify the directions the entry field should stick to. E.g.
            'ew' will stretch the label from east to west. Use cardinal
            directions.
        columnspan (int):
            specify over how many grid columns this object can be placed.
        entry_field (tk.Entry):
            the actual entry field that is initialized internally with the
            passed parameters.
    """
    def __init__(
            self,
            root,
            width: int,
            height: int,
            grid_pos: Tuple[int, int],
            padding: Union[
                Tuple[int, int],
                Tuple[Tuple[int, int], Tuple[int, int]],
                Tuple[int, Tuple[int, int]],
                Tuple[Tuple[int, int], int]
            ],
            text: str,
            font: Union[
                Tuple[str, int],
                Tuple[str, int, str],
            ],
            foreground_color: str,
            background_color: str,
            example_color: str,
            border_width: int,
            visibility: bool,
            sticky: Union[str, None] = None,
            columnspan: Union[int, None] = None,
    ):
        """Initializes a custom tkinter Entry.

        Puts the entry field on the parent container if visibility is True.

        Args:
            root (tk.Frame):
                The parent container of this entry field.
            width (int):
                specify the width of the entry field in pixel.
            height (int):
                specify the height of the entry field in pixel.
            grid_pos (tuple[int,int]): the position, as row and column, of the
                entry field in the parent container.
            padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
                additional padding on the horizontal and vertical axis,
                either a single int or a tuple of ints. A single int will
                be applied to both sides of the object while a tuple
                allows for different a paddings on either side,
                e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
                5 pixel above and below the object.
            text (str):
                displayed on the entry field as an example. Will be removed once
                the entry filed is selected. Will be replaced if the entry field
                is unselected and no text is entered.
            font (tk.font.Font):
                applied to the text on the entry field. Can be font family and
                font size or font family, font size, and font style.
                E.g. (family='Arial', size=20, style='bold').
            foreground_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            example_color (str):
                Will be applied to the example text when nothing is entered.
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the entry field in pixel.
            visibility (bool):
                whether to display the entry field on initialization or not.
            sticky (str):
                specify the directions the entry field should stick to. E.g.
                'ew' will stretch the label from east to west. Use cardinal
                directions.
            columnspan (int):
                specify over how many grid columns this object can be placed.
        """
        self.root = root
        self.width = width
        self.height = height
        self.grid_pos = grid_pos
        self.padding = padding
        self.sticky = sticky
        self.columnspan = columnspan
        self.text = text
        self.font = font
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.example_color = example_color
        self.border_width = border_width
        self.visibility = visibility

        self.entry_field = self.create_entry_field()
        self.add_example_text()

        if visibility:
            self.place_entry_field()

    def create_entry_field(self) -> tk.Entry:
        """Initializes a tkinter entry with the current attribute values.

        Returns:
            entry_field (tk.Entry):
                handle for the tkinter entry.
        """
        entry_field = tk.Entry(
            self.root,
            width=self.width, font=self.font,
            fg=self.example_color, bg=self.background_color,
        )
        return entry_field

    def add_example_text(self):
        """Handles the example text.

        Focus in:
            If the user did not input anything and the entry field is
            deselected the example text is replaced.

        Focus out:
            When the entry filed is selected the example text is removed.
        """
        self.entry_field.insert(0, self.text)
        self.entry_field.bind(
            "<FocusIn>",
            lambda event: self.on_entry_click(event)
        )
        self.entry_field.bind(
            "<FocusOut>",
            lambda event: self.on_focusout(event)
        )

    def on_entry_click(self, event):
        """Removes the example text from the entry field.

        Args:
            event (tk.Event):
                event generated by the entry field when selecting the
                entry filed.
        """
        if self.entry_field.get() == self.text:
            # Delete the placeholder text
            self.entry_field.delete(0, tk.END)
            # Change text color to black
            self.entry_field.config(fg=self.foreground_color)

    def on_focusout(self, event):
        """Inserts the example text into the entry field.

        Args:
            event (tk.Event):
                event generated by the entry field when deselecting the
                entry field.
        """
        if self.entry_field.get() == '':
            # Restore placeholder text if empty
            self.entry_field.insert(0, self.text)
            # Change text color to grey
            self.entry_field.config(fg=self.example_color)

    def place_entry_field(self):
        """Places the entry on the parent container at the specified position.

        Sets the visibility attribute to true.
        Uses current grid_pos, padding, sticky and columnspan attribute values.
        """
        self.entry_field.grid(
            row=self.grid_pos[0], column=self.grid_pos[1],
            padx=self.padding[0], pady=self.padding[1],
            sticky=self.sticky, columnspan=self.columnspan,
        )
        self.visibility = True

    def toggle_visibility(self):
        """Places the entry with the current attribute values or hides it.

        Depends on current visibility value.
        Sets visibility attribute to the opposite of its current value.
        """
        if self.visibility:
            self.entry_field.grid_forget()
            self.visibility = False
        else:
            self.entry_field.grid(
                row=self.grid_pos[0], column=self.grid_pos[1],
                padx=self.padding[0], pady=self.padding[1],
                sticky=self.sticky, columnspan=self.columnspan,
            )
            self.visibility = True
        return

    def insert_string(self, string):
        """Inserts a text into the entry field.

        Args:
            string (str):
                string to insert into the entry field.
        """
        self.entry_field.delete(0, tk.END)
        self.entry_field.insert(0, string)
        self.entry_field.config(fg=self.foreground_color)


class Text:
    """A custom tkinter Text.

    Attributes:
        root (tk.Frame):
            The parent container of this text.
        width (int):
            specify the width of the text in pixel.
        height (int):
            specify the height of the text in pixel.
        grid_pos (tuple[int,int]): the position, as row and column, of the
            text in the parent container.
        padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
            additional padding on the horizontal and vertical axis,
            either a single int or a tuple of ints. A single int will
            be applied to both sides of the object while a tuple
            allows for different a paddings on either side,
            e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
            5 pixel above and below the object.
        text_data (str):
            displayed on the text.
        font (tk.font.Font):
            applied to the text on the entry field. Can be font family and
            font size or font family, font size, and font style.
            E.g. (family='Arial', size=20, style='bold').
        wrap (int):
            text will insert a linebreak after this many text symbols.
        foreground_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        border_width (int):
            width of the border around the entry field in pixel.
        state (str):
            determines if it is read only or editable.
        visibility (bool):
            whether to display the entry field on initialization or not.
        sticky (str):
            specify the directions the entry field should stick to. E.g.
            'ew' will stretch the label from east to west. Use cardinal
            directions.
        columnspan (int):
            specify over how many grid columns this object can be placed.
        text (tk.Text):
            the actual entry field that is initialized internally with the
            passed parameters.
    """
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            grid_pos: Tuple[int, int],
            padding: Union[
                Tuple[int, int],
                Tuple[Tuple[int, int], Tuple[int, int]],
                Tuple[int, Tuple[int, int]],
                Tuple[Tuple[int, int], int]
            ],
            text: str,
            font: Union[
                Tuple[str, int],
                Tuple[str, int, str],
            ],
            wrap: str,
            foreground_color: str,
            background_color: str,
            border_width: int,
            state: str,
            visibility: bool,
            sticky: Union[str, None] = None,
            columnspan: Union[int, None] = None,
    ):
        """Initializes a custom tkinter Text.

        Puts the text on the parent container if visibility is True.

        Args:
            root (tk.Frame):
                The parent container of this text.
            width (int):
                specify the width of the text in pixel.
            height (int):
                specify the height of the text in pixel.
            grid_pos (tuple[int,int]): the position, as row and column, of the
                text in the parent container.
            padding (Union[Tuple[int,int], Tuple[Tuple[int,int],Tuple[int,int]], Tuple[int,Tuple[int,int]], Tuple[Tuple[int,int],int]):
                additional padding on the horizontal and vertical axis,
                either a single int or a tuple of ints. A single int will
                be applied to both sides of the object while a tuple
                allows for different a paddings on either side,
                e.g ((5,10), 5) will add 5 pixel left 10 pixel right and
                5 pixel above and below the object.
            text (str):
                displayed on the text.
            font (tk.font.Font):
                applied to the text on the entry field. Can be font family and
                font size or font family, font size, and font style.
                E.g. (family='Arial', size=20, style='bold').
            wrap (int):
                text will insert a linebreak after this many text symbols.
            foreground_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            border_width (int):
                width of the border around the entry field in pixel.
            state (str):
                determines if it is read only or editable.
            visibility (bool):
                whether to display the entry field on initialization or not.
            sticky (str):
                specify the directions the entry field should stick to. E.g.
                'ew' will stretch the label from east to west. Use cardinal
                directions.
            columnspan (int):
                specify over how many grid columns this object can be placed.
        """
        self.root = root
        self.width = width
        self.height = height
        self.grid_pos = grid_pos
        self.padding = padding
        self.sticky = sticky
        self.columnspan = columnspan
        self.text_data = text
        self.font = font
        self.wrap = wrap
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.border_width = border_width
        self.state = state
        self.visibility = visibility

        self.text = self.create_text()

        if visibility:
            self.place_text()

    def create_text(self) -> tk.Text:
        """Initializes a tkinter text with the current attribute values.

        Returns:
            text (tk.Text):
                handle for the tkinter text.
        """
        text = tk.Text(
            self.root,
            font=self.font, wrap=self.wrap,
            fg=self.foreground_color, bg=self.background_color,
            bd=self.border_width
        )
        text.insert("1.0", self.text_data)
        text.config(state=self.state)
        return text

    def place_text(self):
        """Places the text on the parent container at the specified position.

        Sets the visibility attribute to true.
        Uses current grid_pos, padding, sticky and columnspan attribute values.
        """
        self.text.grid(
            row=self.grid_pos[0], column=self.grid_pos[1],
            padx=self.padding[0], pady=self.padding[1],
            sticky=self.sticky, columnspan=self.columnspan,
        )
        self.visibility = True

    def hide_text(self):
        """Hides the text and sets the visibility attribute to False."""
        self.text.grid_forget()
        self.visibility = False

    def toggle_visibility(self):
        """Places the text with the current attribute values or hides it.

        Depends on current visibility value.
        Sets visibility attribute to the opposite of its current value.
        """
        if self.visibility:
            self.text.grid_forget()
            self.visibility = False
        else:
            self.text.grid(
                row=self.grid_pos[0], column=self.grid_pos[1],
                padx=self.padding[0], pady=self.padding[1],
                sticky=self.sticky, columnspan=self.columnspan,
            )
            self.visibility = True
        return

    def change_text(self, new_text):
        """Replaces the text.

        Args:
            new_text (str):
                the new text to be inserted.
        """
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, new_text)
        self.text.config(state='disabled')


class ToggleSwitch(tk.Canvas):
    """A custom switch based on a tkinter canvas.

    Attributes:
        root (tk.Frame):
            The parent container of this switch.
        width (int):
            specify the width of the switch in pixel.
        height (int):
            specify the height of the switch in pixel.
        on_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        off_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        handle_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        background_color (str):
            hex color code e.g. '#00FF00' or a color name e.g. 'red'.
        command (callable):
            executed on switch press.
        state (bool):
            keeps track of the state of the switch.
    """
    def __init__(
            self,
            root: tk.Frame,
            width: int,
            height: int,
            on_color: str,
            off_color: str,
            handle_color: str,
            background_color: str,
            command: callable
    ):
        """Initializes a custom switch based on a tkinter canvas.

        Puts the switch on the parent container if visibility is True.

        Args:
            root (tk.Frame):
                The parent container of this switch.
            width (int):
                specify the width of the switch in pixel.
            height (int):
                specify the height of the switch in pixel.
            on_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            off_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            handle_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            background_color (str):
                hex color code e.g. '#00FF00' or a color name e.g. 'red'.
            command (callable):
                executed on switch press.
        """
        self.root = root
        self.width = width
        self.height = height
        self.on_color = on_color
        self.off_color = off_color
        self.handle_color = handle_color  #
        self.background_color = background_color
        self.command = command
        self.state = False

        super().__init__(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, highlightthickness=0
        )

        self.draw_switch()
        self.bind("<Button-1>", self.toggle)

    def draw_switch(self):
        """Draw the switch in its current state."""
        self.delete("all")

        bg = self.on_color if self.state else self.off_color

        self.create_oval(
            2,
            2,
            self.height - 2,
            self.height - 2,
            fill=bg,
            outline=bg
        )
        self.create_oval(
            self.width - self.height + 2,
            2,
            self.width - 2,
            self.height - 2,
            fill=bg,
            outline=bg
        )
        self.create_rectangle(
            self.height / 2,
            2,
            self.width - self.height / 2,
            self.height - 2,
            fill=bg,
            outline=bg
        )

        if self.state:
            handle_x = self.width - self.height + 2
        else:
            handle_x = 2

        self.create_oval(
            handle_x,
            2,
            handle_x + self.height - 4,
            self.height - 2,
            fill=self.handle_color,
            outline=self.handle_color
        )

    def toggle(self, event=None):
        """Toggle the state of the switch and change the appearance to match.

        Args:
            event (tk.Event):
                event generated by the underlying canvas when left mouse button
                is pressed.
        """
        self.state = not self.state
        self.draw_switch()
        self.command()

    def set_state(self, state):
        """Set the state to a desired state.

        Args:
            state (bool):
                the desired state.
        """
        self.state = state
        self.draw_switch()
