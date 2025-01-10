import tkinter as tk
from PIL import Image, ImageTk
import warnings

class Window:
    def __init__(
            self,
            width: int | None,
            height: int | None,
            title: str,
            background_color: str,
            fullscreen: bool = False,
    ):
        self.width = width
        self.height = height#
        self.title = title
        self.background_color = background_color
        self.fullscreen = fullscreen

        self.window = self.create_window()

    def create_window(self):
        window = tk.Tk()
        window.title(self.title)
        window.configure(bg=self.background_color)
        window.bind('<Escape>', self.close_window)

        if self.fullscreen is False:
            if self.width is None and self.height is None:
                window.geometry(f"500x500")
            else:
                window.geometry(f"{self.width}x{self.height}")
        else:
            window.attributes("-fullscreen", self.fullscreen)

        return window

    def close_window(self, event=None):
        self.window.quit()

    def run(self):
        self.window.mainloop()


class Frame:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            background_color: str,
            border_width: int,
            visibility: bool,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background_color = background_color
        self.border_width = border_width
        self.visibility = visibility

        self.frame = self.create_frame()

        if visibility:
            self.place_frame()

    def create_frame(self):
        frame = tk.Frame(
            self.root,
            bg=self.background_color,
            bd=self.border_width,
            width=self.width,
            height=self.height,
        )
        return  frame

    def place_frame(self):
        self.frame.place(x=self.x, y=self.y)
        self.visibility = True

    def hide_frame(self):
        self.frame.place_forget()
        self.visibility = False

    def destroy_frame(self):
        self.visibility = False
        self.frame.destroy()

    def toggle_visibility(self):
        if self.visibility:
            self.frame.place_forget()
            self.visibility = False
        else:
            self.frame.place(x=self.x, y=self.y)
            self.visibility = True
        return

    def switch_to_frame(self, new_frame):
        self.frame.destroy()
        new_frame.place_frame()
        new_frame.visibility = True


class Button:
    def __init__(
            self,
            root,
            width: int,
            height: int,
            x: int,
            y: int,
            command: callable,
            foreground_color: str,
            background_color: str,
            border_width: int,
            visibility: bool,
            text: str | None = None,
            font: [[str, int], [str, int, str, ...], None]  = None,
            image: str | None = None,
            rotation: int| None = 0,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.command = command
        self.font = font
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.border_width = border_width
        self.visibility = visibility
        self.text = text
        self.image = image
        self.rotation = rotation

        if self.image:
             self.image = self.get_image(self.image)

        self.button = self.create_button()

        if visibility:
            self.place_button()

    def create_button(self):
        if self.text:
            button = tk.Button(
                self.root, command=self.command,
                width=self.width, height=self.height,
                text=self.text, font=self.font,
                fg=self.foreground_color, bg=self.background_color,
                bd=self.border_width
            )
            return button
        elif self.image:
            button = tk.Button(
                self.root, command=self.command,
                width=self.width, height=self.height,
                image=self.image,
                fg=self.foreground_color, bg=self.background_color,
                bd=self.border_width
            )
            return button
        else:
            warnings.warn('No text or image given to Button', UserWarning)

    def place_button(self):
        self.button.place(x=self.x, y=self.y)
        self.visibility = True

    def hide_button(self):
        if self.visibility:
            self.button.place_forget()
            self.visibility = False

    def toggle_visibility(self):
        if self.visibility:
            self.button.place_forget()
            self.visibility = False
        else:
            self.button.place(x=self.x, y=self.y)
            self.visibility = True
        return

    def get_image(self, image_path):
        image = Image.open(image_path)
        image = image.resize(size=(self.width, self.height))
        image = image.rotate(angle=self.rotation)
        image = ImageTk.PhotoImage(image)
        return image


class Label:
    def __init__(
            self,
            root,
            x: int,
            y: int,
            text: str,
            font: [[str, int],[str, int, str,...]],
            foreground_color: str,
            background_color: str,
            visibility: bool,
    ):
        self.root = root
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.visibility = visibility

        self.label = self.create_label()

        if visibility:
            self.place_label()

    def create_label(self):
        label = tk.Label(
            self.root,
            text=self.text, font=self.font,
            fg=self.foreground_color, bg=self.background_color
        )
        return label

    def place_label(self):
        self.label.place(x=self.x, y=self.y)
        self.visibility = True

    def hide_label(self):
        self.label.place_forget()
        self.visibility = False

    def toggle_visibility(self):
        if self.visibility:
            self.label.place_forget()
            self.visibility = False
        else:
            self.label.place(x=self.x, y=self.y)
            self.visibility = True
        return


class Picture:
    def __init__(
            self,
            root,
            width: int,
            height: int,
            x: int,
            y: int,
            image: str,
            foreground_color: str,
            background_color: str,
            visibility: bool,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.visibility = visibility

        self.image = self.get_image(image)
        self.label = self.create_label()

        if visibility:
            self.place_label()

    def create_label(self):
        label = tk.Label(
            self.root,
            image=self.image,
            width=self.width, height=self.height,
            fg=self.foreground_color, bg=self.background_color
        )
        return label

    def place_label(self):
        self.label.place(x=self.x, y=self.y)
        self.visibility = True

    def hide_label(self):
        self.label.place_forget()
        self.visibility = False

    def toggle_visibility(self):
        if self.visibility:
            self.label.place_forget()
            self.visibility = False
        else:
            self.label.place(x=self.x, y=self.y)
            self.visibility = True
        return

    @staticmethod
    def get_image(image_path):
        image = Image.open(image_path)
        crop_box = (0, 0, image.width - 4, image.height - 4)
        image = image.crop(crop_box)
        image = ImageTk.PhotoImage(image)
        return image


class EntryField:
    def __init__(
            self,
            root,
            width: int,
            height: int,
            x: int,
            y: int,
            text: str,
            font: [[str, int],[str, int, str,...]],
            foreground_color: str,
            background_color: str,
            example_color: str,
            border_width: int,
            visibility: bool,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
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

    def create_entry_field(self):
        entry_field = tk.Entry(
            self.root,
            width=self.width, font=self.font,
            fg=self.foreground_color, bg=self.background_color,
        )
        return entry_field

    def add_example_text(self):
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
        if self.entry_field.get() == self.text:
            # Delete the placeholder text
            self.entry_field.delete(0, tk.END)
            # Change text color to black
            self.entry_field.config(fg=self.foreground_color)

    def on_focusout(self, event):
        if self.entry_field.get() == '':
            # Restore placeholder text if empty
            self.entry_field.insert(0, self.text)
            # Change text color to grey
            self.entry_field.config(fg=self.example_color)

    def place_entry_field(self):
        self.entry_field.place(x=self.x, y=self.y)
        self.visibility = True

    def hide_entry_field(self):
        self.entry_field.place_forget()
        self.visibility = False

    def toggle_visibility(self):
        if self.visibility:
            self.entry_field.place_forget()
            self.visibility = False
        else:
            self.entry_field.place(x=self.x, y=self.y)
            self.visibility = True
        return


class Popup:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            title: str,
            background_color: str,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.title = title
        self.background_color = background_color

        self.popup = self.create_popup()

    def create_popup(self):
        popup = tk.Toplevel(self.root, bg=self.background_color)
        popup.title(self.title)
        popup.geometry(f"{self.width}x{self.height}")
        return popup


class Text:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            text: str,
            font: [[str, int],[str, int, str,...]],
            wrap: str,
            foreground_color: str,
            background_color: str,
            border_width: int,
            state: str,
            visibility: bool,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
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

    def create_text(self):
        text = tk.Text(
            self.root,
            font=self.font, wrap=self.wrap,
            fg=self.foreground_color, bg=self.background_color,
            bd=self.border_width
        )
        text.insert("1.0", self.text_data)  # Insert text at the beginning
        text.config(state=self.state)  # Make the text widget read-only
        return text

    def place_text(self):
        self.text.place(width=self.width, height=self.height,x=self.x, y=self.y)
        self.visibility = True

    def hide_text(self):
        self.text.place_forget()
        self.visibility = False

    def toggle_visibility(self):
        if self.visibility:
            self.text.place_forget()
            self.visibility = False
        else:
            self.text.place(
                width=self.width, height=self.height, x=self.x, y=self.y
            )
            self.visibility = True
        return
