import numpy as np
import pandas as pd

from custom_widgets import *


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
            32800: ('Gleis_horizontal', 0),
            1025: ('Gleis_vertikal', 0),
            2064: ('Gleis_kurve_oben_links', 0),
            72: ('Gleis_kurve_oben_rechts', 0),
            16386: ('Gleis_kurve_unten_rechts', 0),
            4608: ('Gleis_kurve_unten_links', 0),
            3089: ('Weiche_horizontal_oben_links', 0),
            32872: ('Weiche_horizontal_oben_rechts', 0),
            17411: ('Weiche_horizontal_unten_rechts', 0),
            38408: ('Weiche_horizontal_unten_links', 0),
            34864: ('Weiche_vertikal_oben_links', 0),
            1097: ('Weiche_vertikal_oben_rechts', 0),
            49186: ('Weiche_vertikal_unten_rechts', 0),
            5633: ('Weiche_vertikal_unten_links', 0),
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
            image = f'../png/{image}.png'
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
                    self.array[2][row, col] = self.current_selection
                    self.train_data.at[
                        self.train_index, 'end_pos'
                    ] = (row, col)
                else:
                    # train
                    self.array[1][row, col] = self.current_selection

                    data = {
                        'start_pos': (row, col),
                        'dir': self.dir[self.current_selection],
                        'end_pos': (np.nan, np.nan),
                        'e_dep': np.nan,
                        'l_arr': np.nan,
                    }
                    self.train_data.loc[len(self.train_data)] = data
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

        for i in range(3):
            for row in range(self.rows):
                for col in range(self.cols):
                    value = self.array[i][row, col]
                    if value:
                        image, rotation = self.img_dict[value]

                        image = f'../png/{image}.png'
                        image = Image.open(image).resize(
                            (int(self.cell_size * self.scale),
                             int(self.cell_size * self.scale))
                        ).rotate(rotation)
                        image = ImageTk.PhotoImage(image)

                        self.image_refs.append(image)

                        x1 = self.x_offset + col * self.cell_size * self.scale
                        y1 = self.y_offset + row * self.cell_size * self.scale
                        self.canvas.create_image(
                            x1, y1, anchor="nw", image=image,
                            tags="grid_image"
                        )


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

        self.config_dict = {}
        self.remove_dict = {}

        self.station_img = Image.open('../png/Bahnhof_#d50000.png')
        self.station_img = self.station_img.resize(size=(60, 60))
        self.station_img = ImageTk.PhotoImage(self.station_img)

        self.canvas = self.create_canvas()
        self.pack_canvas()

        self.scrollbar = tk.Scrollbar(
            self.root, orient='vertical', command=self.canvas.yview
        )
        self.scrollbar.pack(side='right', fill='y')

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
                width=20, font=('Arial', 20),
                fg='#FFFFFF', bg='#000000',
                text=f'Train {idx}: {row["start_pos"]}, {row["dir"]}',
            )
            label.pack(side='left', padx=0)

            self.config_dict[idx] = tk.Button(
                frame,
                width=7,height=1,
                font=('Arial', 20),
                fg='#FFFFFF', bg='#333333',
                text='configure',
                command=lambda index=idx: self.open_train_config_frame(index)
            )
            self.config_dict[idx].pack(side='left', padx=10)

            self.remove_dict[idx] = tk.Button(
                frame,
                width=7, height=1,
                font=('Arial', 20),
                fg='#FFFFFF', bg='#333333',
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

        # get number of trains at the same position as the deleted one
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
            ] = next(k for k, d in self.grid.dir.items() if d == new_dir)

        self.train_data.drop(index, inplace=True)
        self.train_data.reset_index(drop=True, inplace=True)
        self.update_labels()
        self.grid.draw_images()
        return

    def open_train_config_frame(self, index):
        config_frame = Frame(
            root=self.root,
            width=self.root.winfo_width(),
            height=self.root.winfo_height(),
            x=0,
            y=0,
            background_color='#000000',
            border_width=0,
            visibility=True
        )

        self.grid.current_selection = None
        self.grid.train_index = index

        config_label = tk.Label(
            config_frame.frame,
            text=f'Configure: Train {index}', font=('Arial', 40),
            foreground='#FFFFFF', background='#000000', bd=0,
        )
        config_label.place(
            x=config_frame.width * 0.2, y=config_frame.height * 0.3
        )

        ed_label = tk.Label(
            config_frame.frame,
            text='Earliest Departure:', font=('Arial', 20),
            foreground='#FFFFFF', background='#000000', bd=0,
        )
        ed_label.place(
            x=config_frame.width * 0.2, y=config_frame.height * 0.4
        )

        la_label = tk.Label(
            config_frame.frame,
            text='Latest Arrival:', font=('Arial', 20),
            foreground='#FFFFFF', background='#000000',
            bd=0,
        )
        la_label.place(
            x=config_frame.width * 0.2, y=config_frame.height * 0.45
        )

        ed_entry = tk.Entry(
            config_frame.frame,
            width=5, font=('Arial', 20),
            foreground='#FFFFFF', background='#333333', bd=1,
        )
        ed_entry.place(
            x=config_frame.width * 0.5, y=config_frame.height * 0.4
        )

        la_entry = tk.Entry(
            config_frame.frame,
            width=5, font=('Arial', 20),
            foreground='#FFFFFF', background='#333333', bd=1,
        )
        la_entry.place(
            x=config_frame.width * 0.5, y=config_frame.height * 0.45
        )

        station_label = tk.Label(
            config_frame.frame,
            text='Place Station:', font=('Arial', 20),
            foreground='#FFFFFF', background='#000000',
            bd=0,
        )
        station_label.place(
            x=config_frame.width * 0.2, y=config_frame.height * 0.5
        )

        place_station = tk.Button(
            config_frame.frame,
            width=60, height=60,
            command=lambda: self.grid.select(5),
            image=self.station_img,
            foreground='#000000', background='#000000', bd=0
        )
        place_station.place(
            x=config_frame.width * 0.51, y=config_frame.height * 0.49
        )

        save = tk.Button(
            config_frame.frame,
            width=5, height=1,
            command=lambda: self.save_ed_la(
                index, ed_entry, la_entry, config_frame
            ),
            text='Save', font=('Arial', 20),
            foreground='#000000', background='#777777', bd=0
        )
        save.place(
            x=config_frame.width * 0.5, y=config_frame.height * 0.55
        )


    def save_ed_la(self, index, ed_entry, la_entry, config_frame):
        try:
            ed = int(ed_entry.get())
            la = int(la_entry.get())
        except ValueError:
            # TODO: show error message in config window ?
            print('Only Integers allowed in '
                  'Earliest Departure and Latest Arrival')
            ed = np.nan
            la = np.nan

        self.train_data.loc[index, 'e_dep'] = ed
        self.train_data.loc[index, 'l_arr'] = la
        self.grid.current_selection = None
        self.grid.train_index = None
        self.grid.array[2] = np.zeros(self.grid.array[2].shape)
        self.grid.draw_images()
        config_frame.destroy_frame()

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
