from typing import Tuple

import numpy as np
import pandas as pd
import platform

from code.custom_widgets import *


# Platform: 
sys_platform = platform.system()

class EnvCanvas:
    def __init__(
            self,
            root: tk.Tk,
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
        self.text_label = None

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.root.after(100, self.initial_zoom)

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

        self.canvas.move("env_image", dx, dy)
        self.canvas.move("grid_line", dx, dy)
        self.canvas.move("grid_label", dx, dy)

    def draw_mouse_symbols(self, event):
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        if 0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height:
            row = int(adjusted_y / self.cell_size )
            col = int(adjusted_x / self.cell_size )
            coords_text = f"[{row}, {col}]"

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
            self.canvas.delete(self.text_label)
            self.text_label = None

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas."""
        self.canvas.delete(self.text_label)
        self.text_label = None

    def draw_image(self):
        width = int(self.cols * self.cell_size * self.scale)
        height = int(self.rows * self.cell_size * self.scale)

        if width <= 0 or height <= 0:
            self.root.after(100, self.initial_zoom)
            return

        self.display_image = ImageTk.PhotoImage(
            self.image.resize((width, height))
        )

        if self.canvas_image is None:
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2

            self.canvas_image = self.canvas.create_image(
                self.x_offset,
                self.y_offset,
                anchor="nw",
                image=self.display_image,
                tags='env_image'
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

        # Uncomment to draw row and column labels on the canvas
        # self.draw_grid_labels()

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
                font=(self.font[0], int(self.font[1] * self.scale)),
                fill=self.grid_color,
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
                font=(self.font[0], int(self.font[1] * self.scale)),
                fill=self.grid_color,
                tags="grid_label"
            )

    def initial_zoom(self):
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


class BuildCanvas:
    def __init__(
            self,
            root: tk.Tk,
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

        # populate canvas
        self.pan_start = (0, 0)
        self.x_offset = 0
        self.y_offset = 0
        self.cell_size = 50
        self.scale = 1.0
        self.text_label = None
        self.current_selection_image = None
        self.mouse_image = None

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.modify_array)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<Leave>", self.remove_mouse_symbols)
        self.canvas.bind("<Motion>", self.draw_mouse_symbols)

        self.image_refs = {}
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

    def select(self, selection):
        self.current_selection = selection

    def select_station(self, index):
        self.current_selection = 5
        self.train_index = index

    def calculate_initial_pos(self):
        if max(self.rows, self.cols) > 50:
            self.x_offset = 50
            self.y_offset = 50
            self.draw_grid()
            self.draw_images()
        elif self.rows > self.cols:
            self.cell_size = (self.canvas.winfo_height() * 0.8) / self.rows
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2
            self.draw_grid()
            self.draw_images()
        else:
            self.cell_size = (self.canvas.winfo_width() * 0.8) / self.cols
            width = self.cell_size * self.cols
            height = self.cell_size * self.rows
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2
            self.draw_grid()
            self.draw_images()

    def modify_array(self, event):
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        row = int(adjusted_y / self.cell_size)
        col = int(adjusted_x / self.cell_size)
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return
        if self.current_selection:
            # place object
            if self.current_selection in [1,2,3,4,5]:
                # place train or station
                if self.current_selection == 5:
                    # station
                    self.array[2] = np.zeros(self.array[2].shape)
                    self.train_data.at[self.train_index, 'end_pos'] = (row, col)
                    self.train_index = None
                    self.current_selection = None
                    for r,c in self.train_data['end_pos']:
                        if r != -1:
                            self.array[2][r, c] = 5
                else:
                    # train
                    self.array[1] = np.zeros(self.array[1].shape)
                    data = {
                        'start_pos': (row, col),
                        'dir': self.dir[self.current_selection],
                        'end_pos': (-1, -1),
                        'e_dep': -1,
                        'l_arr': -1,
                    }
                    self.train_data.loc[len(self.train_data)] = data
                    for _,r in self.train_data.iterrows():
                            self.array[1][r['start_pos']] = self.dir[r['dir']]
                    if self.train_list:
                        self.train_list.update_labels()
                self.update_image_storage()
                self.draw_trains()
            else:
                # place track
                self.array[0][row, col] = self.current_selection
                self.update_image_storage()
                self.put_img_on_canvas(self.current_selection, 0, row, col)
        elif self.current_selection == 0:
            # erase track
            self.array[0][row, col] = 0
            self.update_image_storage()

    def draw_grid(self):
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

        # Uncomment to draw row and column labels on the canvas
        # self.draw_grid_labels()

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
                font=(self.font[0], int(self.font[1] * self.scale)),
                fill=self.grid_color,
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
                font=(self.font[0], int(self.font[1] * self.scale)),
                fill=self.grid_color,
                tags="grid_label"
            )

    def draw_images(self):
        self.update_image_storage()
        self.draw_tracks()
        self.draw_trains()

    def put_img_on_canvas(self, value, layer, row, col):
        adjusted_cell_size = self.cell_size * self.scale

        image = self.image_cache[value].resize(
            (int(adjusted_cell_size), int(adjusted_cell_size))
        )
        image = ImageTk.PhotoImage(image)

        x = self.x_offset + col * adjusted_cell_size
        y = self.y_offset + row * adjusted_cell_size

        if (layer, row, col) in self.canvas_images:
            if self.image_refs.get((layer, row, col)) != image:
                self.image_refs[(layer, row, col)] = image  # Update reference
            self.canvas.itemconfig(
                self.canvas_images[(layer, row, col)], image=image
            )
            self.canvas.coords(self.canvas_images[(layer, row, col)], x, y)
        else:
            canvas_img = self.canvas.create_image(
                x, y, anchor='nw',image=image,
                tags='track_image' if layer == 0 else 'train_station_image'
            )
            self.canvas_images[(layer, row, col)] = canvas_img
            self.image_refs[(layer, row, col)] = image

    def update_image_storage(self):
        starts = set(self.train_data['start_pos'])
        ends = set(self.train_data['end_pos'])

        self.canvas_images = {
            (layer, row, col): v
            for (layer, row, col), v in self.canvas_images.items()
            if (layer == 0 and self.array[0][row, col] != 0) or
               (layer == 1 and (row, col) in starts) or
               (layer == 2 and (row, col) in ends)
        }

        self.image_refs = {
            (layer, row, col): v
            for (layer, row, col), v in self.image_refs.items()
            if (layer == 0 and self.array[0][row, col] != 0) or
               (layer == 1 and (row, col) in starts) or
               (layer == 2 and (row, col) in ends)
        }

    def draw_tracks(self):
        for row in range(self.rows):
            for col in range(self.cols):
                value = self.array[0][row, col]
                if value == 0:
                    continue
                else:
                    self.put_img_on_canvas(value, 0, row, col)

    def draw_trains(self):
        for _, row in self.train_data.iterrows():
            self.put_img_on_canvas(
                value=self.dir[row['dir']],
                layer=1,
                row=row['start_pos'][0],
                col=row['start_pos'][1]
            )

            if row['end_pos'] != (-1, -1):
                self.put_img_on_canvas(
                    5,
                    2,
                    row=row['end_pos'][0],
                    col=row['end_pos'][1]
                )

        self.canvas.delete('id_labels')
        self.draw_id_labels()

    def draw_id_labels(self):
        adjusted_cell_size = self.cell_size * self.scale
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

        def assign_offset(pos):
            if pos not in used:
                used[pos] = {i: 0 for i in range(9)}

            available_offsets = [i for i in range(9) if i not in used[pos]]

            if available_offsets:
                chosen = available_offsets[0]
            else:
                chosen = min(used[pos], key=used[pos].get)

            used[pos][chosen] += 1
            return chosen

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
                font=(
                    self.id_label_font[0],
                    int(self.id_label_font[1] * (adjusted_cell_size / 100)),
                    self.id_label_font[2]
                ),
                fill=self.train_color,
                tags="id_labels"
            )

            station_pos = row['end_pos']

            if station_pos != (-1, -1):
                station_offset = assign_offset(station_pos)

                self.canvas.create_text(
                    (self.x_offset + offset_dict[station_offset][0] +
                     station_pos[1] * adjusted_cell_size),
                    (self.y_offset + offset_dict[station_offset][1] +
                     station_pos[0] * adjusted_cell_size),
                    text=str(index),
                    anchor="center",
                    font=(
                        self.id_label_font[0],
                        int(self.id_label_font[1] * (adjusted_cell_size / 100)),
                        self.id_label_font[2]
                    ),
                    fill=self.station_color,
                    tags="id_labels"
                )

    def draw_mouse_symbols(self, event):
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        if not (0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height):
            self.canvas.delete(self.text_label)
            self.canvas.delete(self.mouse_image)
            self.text_label = None
            self.mouse_image = None
            return

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
        """Clear the coordinates label when the mouse leaves the canvas."""
        self.canvas.delete(self.text_label)
        self.text_label = None

    @staticmethod
    def set_img_dict():
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
        for key, (filename, rotation) in self.image_dict.items():
            try:
                image = Image.open(f'data/png/{filename}.png')
                rotated_image = image.rotate(rotation)
                self.image_cache[key] = rotated_image
            except FileNotFoundError:
                print(f"Warning: Image {filename}.png not found.")
                self.image_cache[key] = None

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
        self.draw_images()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def pan(self, event):
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


class TrainListCanvas:
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
            border_width: int,
            grid: BuildCanvas,
            train_data: pd.DataFrame,
            windows: dict,
            frames: dict,
    ):
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
        self.border_width = border_width
        self.grid = grid
        self.train_data = train_data
        self.windows = windows
        self.frames = frames


        self.station_dict = {}
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

        self.update_labels()

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def pack_canvas(self):  #
        self.canvas.pack(side='top', padx=self.x, pady=self.y, anchor='nw')

    def update_labels(self):
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
            )

            Label(
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
                padding=(0, 0),
                command=lambda i=index: self.open_train_config_frame(i),
                text=f'Configure {index}',
                font=self.base_font_layout,
                foreground_color=self.label_color,
                background_color=self.button_color,
                border_width=0,
                visibility=True,
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
            )

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def remove_train(self, index):

        # get list of trains at the same position as the deleted one
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
            # get first index from remaining trains on the same position
            replacement = df.index[0]
            # get the direction of that train
            new_dir = self.train_data['dir'].iloc[replacement]

            # replace the old trains direction in the grid
            self.grid.array[1][
                self.train_data['start_pos'].iloc[index]
            ] = self.grid.dir[new_dir]

        if self.train_data['end_pos'].iloc[index] != (-1, -1):
            # get list of stations at the same position as the deleted one
            station_count = self.train_data[
                self.train_data['end_pos'] ==
                self.train_data['end_pos'].iloc[index]
                ].count()

            if station_count['end_pos'] == 1:
                self.grid.array[2][self.train_data['end_pos'].iloc[index]] = 0

        self.train_data.drop(index, inplace=True)
        self.train_data.reset_index(drop=True, inplace=True)
        self.update_labels()
        self.grid.update_image_storage()
        self.grid.draw_trains()
        return

    def open_train_config_frame(self, index):
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

        Button(
            root=config_frame.frame,
            width=20,
            height=1,
            grid_pos=(3, 0),
            padding=(100, 40),
            sticky='nw',
            columnspan=2,
            command=lambda: self.save_ed_la(
                index,
                ed_entry,
                la_entry,
                ed_err_label,
                la_err_label,
                config_frame,
                True
            ),
            text='Save',
            font=self.base_font_layout,
            foreground_color=self.label_color,
            background_color=self.button_color,
            border_width=0,
            visibility=True,
        )

        config_frame.frame.rowconfigure((0, 3),weight=10)
        config_frame.frame.rowconfigure((1, 2), weight=1)
        config_frame.frame.columnconfigure((0, 1),weight=1)
        config_frame.frame.grid_propagate(False)

    def save_ed_la(
            self,
            index,
            ed_entry,
            la_entry,
            ed_err_label,
            la_err_label,
            config_frame,
            save
    ):

        if not save:
            config_frame.destroy_frame()
            return 0

        ed = ed_entry.entry_field.get()
        la = la_entry.entry_field.get()

        err_count = 0

        try:
            if ed.startswith('e.g.') or ed == '' or ed is None:
                ed = -1
            else:
                ed = int(ed)
                ed_err_label.hide_label()
        except ValueError:
            ed_err_label.label.config(
                text='needs int > 0',
                fg=self.bad_status_color,
            )
            ed_err_label.place_label()
            err_count += 1

        try:
            if la.startswith('e.g.') or la == '' or la is None:
                la = -1
            else:
                la = int(la)
                la_err_label.hide_label()
        except ValueError:
            la_err_label.label.config(
                text='needs int > 0',
                fg=self.bad_status_color,
            )
            la_err_label.place_label()
            err_count += 1

        if err_count:
            return -1

        if ed < 1:
            ed_err_label.label.config(
                text='needs int > 0',
                fg=self.bad_status_color,
            )
            ed_err_label.place_label()
            err_count += 1

        if la < 1:
            la_err_label.label.config(
                text='needs int > 0',
                fg=self.bad_status_color,
            )
            la_err_label.place_label()
            err_count += 1

        if err_count:
            return -1

        self.train_data.loc[index, 'e_dep'] = ed
        self.train_data.loc[index, 'l_arr'] = la
        config_frame.destroy_frame()


class ResultCanvas:
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
        self.text_label = None

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
        self.draw_paths()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        self.canvas.move("env_image", dx, dy)
        self.canvas.move("grid_line", dx, dy)
        self.canvas.move("grid_label", dx, dy)
        self.canvas.move("path_labels", dx, dy)

    def draw_mouse_symbols(self, event):
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        if 0 <= adjusted_x < grid_width and 0 <= adjusted_y < grid_height:
            row = int(adjusted_y / self.cell_size)
            col = int(adjusted_x / self.cell_size)
            coords_text = f"[{row}, {col}]"

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
            self.canvas.delete(self.text_label)
            self.text_label = None

    def remove_mouse_symbols(self, event):
        """Clear the coordinates label when the mouse leaves the canvas."""
        self.canvas.delete(self.text_label)
        self.text_label = None

    def draw_image(self):
        width = int(self.cols * self.cell_size * self.scale)
        height = int(self.rows * self.cell_size * self.scale)

        if width <= 0 or height <= 0:
            self.root.after(100, self.initial_zoom)
            return

        self.display_image = ImageTk.PhotoImage(
            self.image.resize((width, height))
        )

        if self.canvas_image is None:
            self.x_offset = (self.canvas.winfo_width() - width) // 2
            self.y_offset = (self.canvas.winfo_height() - height) // 2

            self.canvas_image = self.canvas.create_image(
                self.x_offset,
                self.y_offset,
                anchor="nw",
                image=self.display_image,
                tags='env_image',
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

        # Uncomment to draw row and column labels on the canvas
        # self.draw_grid_labels()

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
                font=(self.font[0], int(self.font[1] * self.scale)),
                fill=self.grid_color,
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
                font=(self.font[0], int(self.font[1] * self.scale)),
                fill=self.grid_color,
                tags="grid_label"
            )

    def update_paths(self):
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
        self.canvas.delete("path_labels")
        adjusted_cell_size = self.cell_size * self.scale

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

        colors = [
            "#d50000", "#c51162", "#aa00ff", "#6200ea", "#304ffe", "#2962ff",
            "#0091ea", "#00b8d4", "#00bfa5", "#00c853", "#64dd17", "#aeea00",
            "#ffd600", "#ffab00", "#ff6d00", "#ff3d00", "#5d4037", "#455a64"
        ]
        colors = (colors * ((len(self.paths_df) // len(colors)) + 1))
        train_colors = dict(zip(self.paths_df['trainID'].unique(), colors))

        for _, row in self.show_df.iterrows():
            self.canvas.create_text(
                (self.x_offset + row['x'] * adjusted_cell_size +
                 offset_dict[row['cell_offset']][0]),
                (self.y_offset + row['y'] * adjusted_cell_size +
                 offset_dict[row['cell_offset']][1]),
                text=row['timestep'],
                anchor="center",
                font=(
                    self.path_label_font[0],
                    int(self.path_label_font[1] * (adjusted_cell_size/100)),
                    self.path_label_font[2]
                ),
                fill=train_colors[row['trainID']],
                tags="path_labels"
            )

    def initial_zoom(self):
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


class PathListCanvas:
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

    def create_canvas(self):
        canvas = tk.Canvas(
            self.root,
            width=self.width, height=self.height,
            bg=self.background_color, bd=self.border_width,
            highlightthickness=0
        )
        return canvas

    def pack_canvas(self):  #
        self.canvas.pack(side='top', padx=self.x, pady=self.y, anchor='nw')

    def add_labels(self):
        colors = [
            "#d50000", "#c51162", "#aa00ff", "#6200ea", "#304ffe", "#2962ff",
            "#0091ea", "#00b8d4", "#00bfa5", "#00c853", "#64dd17", "#aeea00",
            "#ffd600", "#ffab00", "#ff6d00", "#ff3d00", "#5d4037", "#455a64"
        ]
        colors = (colors * ((len(self.train_data) // len(colors)) + 1))

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
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def toggle_all_paths(self):
        if len(self.show_list) == 0:
            return

        self.current_all = all(self.show_list)

        if self.current_all:
            for i in self.show_button_dict:
                self.show_list = [False] * len(self.show_list)
                self.show_button_dict[i].set_state(False)
            self.current_all = False
        else:
            for i in self.show_button_dict:
                self.show_list = [True] * len(self.show_list)
                self.show_button_dict[i].set_state(True)
            self.current_all = True

        self.grid.show_list = self.show_list
        self.grid.update_paths()

    def toggle_path(self, index):
        if self.show_list[index]:
            self.show_list[index] = False
        else:
            self.show_list[index] = True

        self.grid.show_list = self.show_list
        self.grid.update_paths()
