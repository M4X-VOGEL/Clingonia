import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import colors as mcolors

from code.custom_widgets import *


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
            image: str,
            rows: int,
            cols: int,
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
        self.rows = rows
        self.cols = cols
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
                    font=("Arial", 20),
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
        self.cell_size = self.image.height / self.rows
        width = int(self.cols * self.cell_size * self.scale)
        height = int(self.rows * self.cell_size * self.scale)
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
            array: np.ndarray,
            train_data: pd.DataFrame,
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

        self.img_dict = self.set_img_dict()

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

        self.current_selection = None
        self.image_refs = []
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

        self.draw_images()



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

        self.draw_images()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def pan(self, event):
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.x_offset += dx
        self.y_offset += dy
        self.pan_start = (event.x, event.y)

        self.draw_images()

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
                font=("Arial", 20),
                fill="#FFFFFF",
                anchor="nw"
            )
        else:
            self.canvas.itemconfig(self.text_label, text=coords_text)
            self.canvas.coords(self.text_label, event.x + 10, event.y + 10)

        if self.current_selection is not None:
            image, rotation = self.img_dict[self.current_selection]
            image = f'data/png/{image}.png'
            image = Image.open(image).resize((30, 30)).rotate(rotation)
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

    def select(self, selection):
        self.current_selection = selection

    def modify_array(self, event):
        adjusted_x = (event.x - self.x_offset) / self.scale
        adjusted_y = (event.y - self.y_offset) / self.scale
        row = int(adjusted_y / self.cell_size)
        col = int(adjusted_x / self.cell_size)
        if self.current_selection:
            # place object
            if self.current_selection in [1,2,3,4,5]:
                # place train or station
                if self.current_selection == 5:
                    # station
                    self.array[2] = np.zeros(self.array[2].shape)
                    self.train_data.at[self.train_index, 'end_pos'] = (row, col)
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
            else:
                # place track
                self.array[0][row, col] = self.current_selection
        elif self.current_selection == 0:
            # erase track
            self.array[0][row, col] = 0
        self.draw_images()

    def draw_images(self):
        self.draw_grid()
        self.canvas.delete("grid_image")
        self.canvas.delete("id_labels")

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

        for i in range(3):
            for row in range(self.rows):
                for col in range(self.cols):
                    value = self.array[i][row, col]
                    if value:
                        image, rotation = self.img_dict[value]

                        image = f'data/png/{image}.png'
                        image = Image.open(image).resize(
                            (int(adjusted_cell_size),
                             int(adjusted_cell_size))
                        ).rotate(rotation)
                        image = ImageTk.PhotoImage(image)

                        self.image_refs.append(image)

                        x1 = self.x_offset + col * adjusted_cell_size
                        y1 = self.y_offset + row * adjusted_cell_size
                        self.canvas.create_image(
                            x1, y1, anchor="nw", image=image,
                            tags="grid_image"
                        )

            # draw id on trains
            if i == 1:
                self.train_data['count'] = (
                    self.train_data.groupby('start_pos')['end_pos']
                    .transform('count')
                )
                self.train_data['cell_offset'] = (
                        self.train_data.groupby('start_pos')
                        .cumcount()
                        .where(self.train_data['count'] > 1,0) % 9
                )

                for index, row in self.train_data.iterrows():
                    self.canvas.create_text(
                        (self.x_offset + offset_dict[row['cell_offset']][0] +
                         row['start_pos'][1] * adjusted_cell_size),
                        (self.y_offset + offset_dict[row['cell_offset']][1] +
                        row['start_pos'][0] * adjusted_cell_size),
                        text=str(index),
                        anchor="center",
                        font=("Courier", 15, 'bold'),
                        fill='#000000',
                        tags="id_labels"
                    )

                self.train_data.drop(columns=['count'], inplace=True)
                self.train_data.drop(columns=['cell_offset'], inplace=True)

            # draw id on station
            if i == 2:
                self.train_data['count'] = (
                    self.train_data.groupby('end_pos')['end_pos']
                    .transform('count')
                )
                self.train_data['cell_offset'] = (
                        self.train_data.groupby('end_pos')
                        .cumcount()
                        .where(self.train_data['count'] > 1,0) % 9
                )

                for index, row in self.train_data.iterrows():
                    if row['end_pos'] != (-1, -1):
                        self.canvas.create_text(
                            (self.x_offset + offset_dict[row['cell_offset']][0] +
                             row['end_pos'][1] * adjusted_cell_size),
                            (self.y_offset + offset_dict[row['cell_offset']][1] +
                            row['end_pos'][0] * adjusted_cell_size),
                            text=str(index),
                            anchor="center",
                            font=("Courier", 15, 'bold'),
                            fill='#000000',
                            tags="id_labels"
                        )

                self.train_data.drop(columns=['count'], inplace=True)
                self.train_data.drop(columns=['cell_offset'], inplace=True)


class TrainListCanvas:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            background_color: str,
            border_width: int,
            grid: BuildCanvas,
            train_data: pd.DataFrame,
            outer_frame: tk.Tk,
            base_font: int,
            font_scale: float,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background_color = background_color
        self.border_width = border_width
        self.grid = grid
        self.train_data = train_data
        self.outer_frame = outer_frame
        self.base_font = base_font
        self.font_scale = font_scale

        self.config_dict = {}
        self.remove_dict = {}

        self.station_img = Image.open('data/png/Bahnhof_#d50000.png')
        self.station_img = self.station_img.resize(size=(60, 60))
        self.station_img = ImageTk.PhotoImage(self.station_img)

        self.canvas = self.create_canvas()
        self.pack_canvas()

        self.scrollbar = tk.Scrollbar(
            self.root, orient='vertical', command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_frame = tk.Frame(self.canvas, bg='#000000')
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

        for idx, row in self.train_data.iterrows():
            frame = tk.Frame(self.scroll_frame, bg='#000000')
            frame.pack(fill='x', pady=5)

            label = tk.Label(
                frame,
                width=25,
                font=('Arial', int(self.font_scale * self.base_font)),
                fg='#FFFFFF', bg='#000000',
                text=f'Train {idx}: {row["start_pos"]}, {row["dir"]}',
            )
            label.pack(side='left', padx=0)

            self.config_dict[idx] = tk.Button(
                frame,
                width=8,height=1,
                font=('Arial', int(self.font_scale * self.base_font)),
                fg='#FFFFFF', bg='#333333',
                text='configure',
                command=lambda index=idx: self.open_train_config_frame(index)
            )
            self.config_dict[idx].pack(side='left', padx=15)

            self.remove_dict[idx] = tk.Button(
                frame,
                width=7, height=1,
                font=('Arial', int(self.font_scale * self.base_font)),
                fg='#FF0000', bg='#000000', bd=0,
                text='remove',
                command=lambda index=idx: self.remove_train(index)
            )
            self.remove_dict[idx].pack(side='left', padx=10)

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
        self.grid.draw_images()
        return

    def open_train_config_frame(self, index):
        config_frame = tk.Frame(
            self.outer_frame,
            width=self.outer_frame.winfo_width(),
            height=self.outer_frame.winfo_height(),
            bg='#000000',
            bd=0,
        )
        config_frame.place(x=0, y=0)

        self.grid.current_selection = None
        self.grid.train_index = index

        config_label = tk.Label(
            config_frame,
            text=f'Configure: Train {index}',
            font=('Arial', int(self.font_scale * self.base_font * 2)),
            foreground='#FFFFFF', background='#000000', bd=0,
        )
        config_label.place(
            x=self.outer_frame.winfo_width() * 0.1,
            y=self.outer_frame.winfo_height() * 0.3
        )

        ed_label = tk.Label(
            config_frame,
            text='Earliest Departure:',
            font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#FFFFFF', background='#000000', bd=0,
        )
        ed_label.place(
            x=self.outer_frame.winfo_width() * 0.1,
            y=self.outer_frame.winfo_height() * 0.4
        )

        ed_entry = tk.Entry(
            config_frame,
            width=5, font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#FFFFFF', background='#333333', bd=1,
        )
        ed_entry.place(
            x=self.outer_frame.winfo_width() * 0.4,
            y=self.outer_frame.winfo_height() * 0.4
        )

        if self.train_data.loc[index, 'e_dep'] != -1:
            ed_entry.insert(
                0,
                str(int(self.train_data.loc[index, 'e_dep']))
            )

        ed_err_label = tk.Label(
            config_frame,
            text='',
            font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#FF0000', background='#000000',
            bd=0,
        )
        ed_err_label.place(
            x=self.outer_frame.winfo_width() * 0.1,
            y=self.outer_frame.winfo_height() * 0.45
        )

        la_label = tk.Label(
            config_frame,
            text='Latest Arrival:',
            font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#FFFFFF', background='#000000',
            bd=0,
        )
        la_label.place(
            x=self.outer_frame.winfo_width() * 0.1,
            y=self.outer_frame.winfo_height() * 0.5
        )

        la_entry = tk.Entry(
            config_frame,
            width=5, font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#FFFFFF', background='#333333', bd=1,
        )
        la_entry.place(
            x=self.outer_frame.winfo_width() * 0.4,
            y=self.outer_frame.winfo_height() * 0.5
        )
        if self.train_data.loc[index, 'l_arr'] != -1:
            la_entry.insert(
                0,
                str(int(self.train_data.loc[index, 'l_arr']))
            )

        la_err_label = tk.Label(
            config_frame,
            text='',
            font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#FF0000', background='#000000',
            bd=0,
        )

        station_label = tk.Label(
            config_frame,
            text='Place Station:',
            font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#FFFFFF', background='#000000',
            bd=0,
        )
        station_label.place(
            x=self.outer_frame.winfo_width() * 0.1,
            y=self.outer_frame.winfo_height() * 0.6
        )

        place_station = tk.Button(
            config_frame,
            width=45, height=45,
            command=lambda: self.grid.select(5),
            image=self.station_img,
            foreground='#000000', background='#000000', bd=0
        )
        place_station.place(
            x=self.outer_frame.winfo_width() * 0.41,
            y=self.outer_frame.winfo_height() * 0.59
        )
        if self.train_data.loc[index, 'end_pos'][0] != -1:
            row, col = self.train_data.loc[index, 'end_pos']
            self.grid.array[2][row, col] = 5
            self.grid.draw_images()

        save = tk.Button(
            config_frame,
            width=5, height=1,
            command=lambda: self.save_ed_la(
                index,
                ed_entry,
                la_entry,
                ed_err_label,
                la_err_label,
                config_frame
            ),
            text='Save', font=('Arial', int(self.font_scale * self.base_font)),
            foreground='#000000', background='#777777', bd=0
        )
        save.place(
            x=self.outer_frame.winfo_width() * 0.4,
            y=self.outer_frame.winfo_height() * 0.65
        )

    def save_ed_la(
            self,
            index,
            ed_entry,
            la_entry,
            ed_err_label,
            la_err_label,
            config_frame
    ):
        err_count = 0
        ed = ed_entry.get()
        la = la_entry.get()
        if ed == '':
            ed = -1
        else:
            try:
                ed = int(ed)
                ed_err_label.place_forget()
            except ValueError:
                ed_err_label.config(text='has to be an integer > 0')
                la_err_label.place(
                    x=self.outer_frame.winfo_width() * 0.1,
                    y=self.outer_frame.winfo_height() * 0.45
                )
                err_count += 1

        if la == '':
            la = -1
        else:
            try:
                la = int(la)
                la_err_label.place_forget()
            except ValueError:
                la_err_label.config(text='has to be an integer > 0')
                la_err_label.place(
                    x=self.outer_frame.winfo_width() * 0.1,
                    y=self.outer_frame.winfo_height() * 0.55
                )
                err_count += 1

        if err_count:
            return -1

        self.train_data.loc[index, 'e_dep'] = ed
        self.train_data.loc[index, 'l_arr'] = la
        self.grid.current_selection = None
        self.grid.train_index = None
        self.grid.draw_images()
        config_frame.destroy()


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
            rows: int,
            cols: int,
            paths_df: pd.DataFrame,
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
        self.rows = rows
        self.cols = cols
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

        self.draw_image()
        self.draw_paths()

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
                    font=("Arial", 20),
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
        self.cell_size = self.image.height / self.rows
        width = int(self.cols * self.cell_size * self.scale)
        height = int(self.rows * self.cell_size * self.scale)
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

    def update_paths(self):
        show_dict = {idx: val for idx, val in enumerate(self.show_list)}

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

        unique_trains = self.show_df['trainID'].unique()
        n = len(unique_trains)

        # custom colors (if not long enough it gets repeated)
        custom_colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c',
                         '#fb9a99','#e31a1c','#fdbf6f','#ff7f00',
                         '#cab2d6','#6a3d9a','#ffff99','#b15928']
        custom_colors = (custom_colors * ((n // len(custom_colors)) + 1))

        # get n colors from the color palette
        # good palettes are tab20, dark or other qualitative palettes
        # or use a custom palette by using palette=custom_colors
        colors = sns.color_palette(
            # palette=custom_colors,
            palette='dark',
            n_colors=n
        )

        # convert colors to hex code
        colors = [mcolors.to_hex(color) for color in colors]

        # make dict with train id and corresponding color
        train_colors = dict(zip(unique_trains, colors))

        for _, row in self.show_df.iterrows():
            self.canvas.create_text(
                (self.x_offset + row['x'] * adjusted_cell_size +
                 offset_dict[row['cell_offset']][0]),
                (self.y_offset + row['y'] * adjusted_cell_size +
                 offset_dict[row['cell_offset']][1]),
                text=row['timestep'],
                anchor="center",
                font=("Courier", int(20 * (adjusted_cell_size/100)), 'bold'),
                fill=train_colors[row['trainID']],
                tags="path_labels"
            )


class PathListCanvas:
    def __init__(
            self,
            root: tk.Tk,
            width: int,
            height: int,
            x: int,
            y: int,
            background_color: str,
            border_width: int,
            train_data: pd.DataFrame,
            grid: ResultCanvas,
            base_font: int,
            font_scale: float,
    ):
        self.root = root
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background_color = background_color
        self.border_width = border_width
        self.train_data = train_data
        self.grid = grid
        self.base_font = base_font
        self.font_scale = font_scale

        self.show_button_dict = {}
        self.show_list = [False] * len(self.train_data)
        self.current_all = False

        self.canvas = self.create_canvas()
        self.pack_canvas()

        self.scrollbar = tk.Scrollbar(
            self.root, orient='vertical', command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_frame = tk.Frame(self.canvas, bg='#000000')
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
        for idx, row in self.train_data.iterrows():
            frame = tk.Frame(self.scroll_frame, bg='#000000')
            frame.pack(fill='x', pady=5)

            label = tk.Label(
                frame,
                width=20, font=('Arial', int(self.font_scale * self.base_font)),
                fg='#FFFFFF', bg='#000000',
                text=f'Train {idx}: {row["start_pos"]}, {row["dir"]}',
            )
            label.pack(side='left', padx=0)

            self.show_button_dict[idx] = tk.Button(
                frame,
                width=7,height=1,
                font=('Arial', int(self.font_scale * self.base_font)),
                fg='#000000', bg='#008800',
                text='show',
                command=lambda index=idx: self.toggle_path(index)
            )
            self.show_button_dict[idx].pack(side='left', padx=10)

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

        if self.current_all:
            for i in self.show_button_dict:
                self.show_list = [False] * len(self.show_list)
                self.show_button_dict[i].config(bg='#008800', text='show')
            self.current_all = False
        else:
            for i in self.show_button_dict:
                self.show_list = [True] * len(self.show_list)
                self.show_button_dict[i].config(bg='#880000', text='hide')
            self.current_all = True

        self.grid.show_list = self.show_list
        self.grid.update_paths()

    def toggle_path(self, index):
        if self.show_list[index]:
            self.show_button_dict[index].config(bg='#008800', text='show')
            self.show_list[index] = False
        else:
            self.show_button_dict[index].config(bg='#880000', text='hide')
            self.show_list[index] = True

        self.grid.show_list = self.show_list
        self.grid.update_paths()
