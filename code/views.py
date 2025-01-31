import os
import ast
import json
from tkinter import filedialog

from code.build_png import create_custom_env, save_png
from code.custom_canvas import *
from code.env import save_env, delete_tmp_lp, delete_tmp_png
from code.gen_png import gen_env
from code.lp_to_env import lp_to_env
from code.positions import position_df

# Base style parameters
SCREENWIDTH, SCREENHEIGHT = 1920, 1080
BASE_FONT = 20
FONT_SCALE = 1


# Widget handlers
WINDOWS, FRAMES, BUTTONS, LABELS, CANVASES, ENTRY_FIELDS, PICTURES, TEXTS = (
    {}, {}, {}, {}, {}, {}, {}, {}
)
BUILD_MODE = None
LAST_MENU = None


# Data storages
DEFAULT_PARAMS = {
    'rows': 40,
    'cols': 40,
    'agents': 4,
    'cities': 4,
    'seed': 1,
    'grid': False,
    'intercity': 2,
    'incity': 2,
    'remove': True,
    'speed': {1 : 1},
    'malfunction': (0, 30),
    'min': 2,
    'max': 6,
    'answer': 1,
    'clingo': 'clingo',
    'lpFiles': []
}
USER_PARAMS = {
    'rows': None,
    'cols': None,
    'agents': None,
    'cities': None,
    'seed': None,
    'grid': None,
    'intercity': None,
    'incity': None,
    'remove': None,
    'speed': None,
    'malfunction': None,
    'min': None,
    'max': None,
    'answer': None,
    'clingo': None,
    'lpFiles': [],
}
ERR_DICT = {
    'rows': {ValueError: 'has to be an integer > 0',},
    'cols': {ValueError: 'has to be an integer > 0'},
    'agents': {ValueError: 'has to be an integer > 0'},
    'cities': {ValueError: 'has to be an integer > 0'},
    'seed': {ValueError: 'has to be an integer > 0'},
    'grid': {ValueError: 'has to be true or false'},
    'intercity': {ValueError: 'has to be an integer > 0'},
    'incity': {ValueError: 'has to be an integer > 0'},
    'remove': {ValueError: 'has to be true or false'},
    'speed': {ValueError: 'has to be a dictionary like: {integer > 0 : integer > 0, ...}',
              SyntaxError: 'has to be a dictionary like: {integer > 0 : integer > 0, ...}'},
    'malfunction': {ValueError: 'has to be a fraction like: integer / integer',
                    IndexError: 'has to be a fraction like: integer / integer'},
    'min': {ValueError: 'has to be an integer > 0'},
    'max': {ValueError: 'has to be an integer > 0'},
    'answer': {ValueError: 'has to be an integer > 0'},
    'clingo': {},
    'lpFiles': {},
}

CURRENT_ARRAY = np.zeros((3,40,40), dtype=int)
CURRENT_DF = pd.DataFrame(
    columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
)
CURRENT_PATHS = pd.DataFrame()
CURRENT_IMG = None

CURRENT_BACKUP_ARRAY = CURRENT_ARRAY.copy()
CURRENT_BACKUP_DF = CURRENT_DF.copy()





# start menu

def build_flatland_window():
    global WINDOWS, SCREENWIDTH, SCREENHEIGHT, FONT_SCALE

    load_user_data_from_file()

    WINDOWS['flatland_window'] = Window(
        width=None,
        height=None,
        fullscreen=True,
        background_color='#000000',
        title='Flatland'
    )
    WINDOWS['flatland_window'].window.bind('<Escape>', exit_gui)

    SCREENWIDTH = WINDOWS['flatland_window'].window.winfo_screenwidth()
    SCREENHEIGHT = WINDOWS['flatland_window'].window.winfo_screenheight()
    FONT_SCALE = ((SCREENWIDTH/1920) ** 0.6) * ((SCREENHEIGHT/1080) ** 0.4)

    WINDOWS['flatland_window'].window.rowconfigure(0, weight=1)
    WINDOWS['flatland_window'].window.columnconfigure((0,1), weight=1)

def create_start_menu():
    global LAST_MENU

    LAST_MENU = 'start'

    build_title_frame()
    build_start_menu_frame()

def build_title_frame():
    global WINDOWS, FRAMES, LABELS, PICTURES, SCREENWIDTH, SCREENHEIGHT, \
        FONT_SCALE
    
    FRAMES['title_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsew',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    LABELS['title_label'] = Label(
        root=FRAMES['title_frame'].frame,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsew',
        text='FLATLAND',
        font=('Arial', int(FONT_SCALE * 80), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    PICTURES['title_image'] = Picture(
        root=FRAMES['title_frame'].frame,
        width=FRAMES['title_frame'].width * 0.5,
        height=FRAMES['title_frame'].width * 0.5,
        grid_pos=(1,0),
        padding=(0, 0),
        sticky='nsew',
        image='../data/png/title_image.png',
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    FRAMES['title_frame'].frame.rowconfigure((0, 1), weight=1)
    FRAMES['title_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['title_frame'].frame.grid_propagate(False)

def build_start_menu_frame():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['start_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['start_help_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_start_menu_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['exit_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 2),
        padding=(0, 0),
        sticky='ne',
        command=lambda: exit_gui(None),
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['random_gen_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(1,1),
        padding=(0,0),
        sticky='n',
        command=switch_start_to_random_gen,
        text='Generate Random Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['build_env_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_start_to_builder,
        text='Build New Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['load_env_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='n',
        command=load_env_from_file,
        text='Load Custom Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    FRAMES['start_menu_frame'].frame.rowconfigure(tuple(range(5)), weight=1)
    FRAMES['start_menu_frame'].frame.columnconfigure(tuple(range(3)), weight=1)
    FRAMES['start_menu_frame'].frame.grid_propagate(False)

def build_start_menu_help_frame():
    global WINDOWS, FRAMES, TEXTS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['start_menu_help_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#00FF00',
        border_width=0,
        visibility=True
    )

    with open("../help_texts/start_menu_help_text.txt", "r") as file:
        # TODO: change help text
        help_displaytext = file.read()

    TEXTS['start_menu_help_frame'] = Text(
        root=FRAMES['start_menu_help_frame'].frame,
        width=FRAMES['start_menu_help_frame'].width,
        height=FRAMES['start_menu_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=("Arial", int(FONT_SCALE * BASE_FONT)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    FRAMES['start_menu_help_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['start_menu_help_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['start_menu_help_frame'].frame.grid_propagate(False)

def toggle_start_menu_help():
    if 'start_menu_help_frame' in FRAMES:
        FRAMES['start_menu_help_frame'].toggle_visibility()
    else:
        build_start_menu_help_frame()

def switch_start_to_random_gen():
    if 'title_frame' in FRAMES:
        FRAMES['title_frame'].destroy_frame()
        del FRAMES['title_frame']
    if 'start_menu_frame' in FRAMES:
        FRAMES['start_menu_frame'].destroy_frame()
        del FRAMES['start_menu_frame']
    if 'start_menu_help_frame' in FRAMES:
        FRAMES['start_menu_help_frame'].destroy_frame()
        del FRAMES['start_menu_help_frame']
    if 'start_menu_env_viewer_frame' in FRAMES:
        FRAMES['start_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['start_menu_env_viewer_frame']

    build_random_gen_para_frame()

def switch_start_to_builder():
    global BUILD_MODE
    BUILD_MODE = 'build'

    if 'title_frame' in FRAMES:
        FRAMES['title_frame'].destroy_frame()
        del FRAMES['title_frame']
    if 'start_menu_frame' in FRAMES:
        FRAMES['start_menu_frame'].destroy_frame()
        del FRAMES['start_menu_frame']
    if 'start_menu_help_frame' in FRAMES:
        FRAMES['start_menu_help_frame'].destroy_frame()
        del FRAMES['start_menu_help_frame']
    if 'start_menu_env_viewer_frame' in FRAMES:
        FRAMES['start_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['start_menu_env_viewer_frame']

    build_builder_para_frame()

def switch_start_to_main():
    if 'title_frame' in FRAMES:
        FRAMES['title_frame'].destroy_frame()
        del FRAMES['title_frame']
    if 'start_menu_frame' in FRAMES:
        FRAMES['start_menu_frame'].destroy_frame()
        del FRAMES['start_menu_frame']
    if 'start_menu_help_frame' in FRAMES:
        FRAMES['start_menu_help_frame'].destroy_frame()
        del FRAMES['start_menu_help_frame']
    if 'start_menu_env_viewer_frame' in FRAMES:
        FRAMES['start_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['start_menu_env_viewer_frame']

    create_main_menu()





# main menu

def create_main_menu():
    global LAST_MENU

    LAST_MENU = 'main'

    build_main_menu()
    build_main_menu_env_viewer()

def build_main_menu():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['main_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['help_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_main_menu_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['exit_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 2),
        padding=(0, 0),
        sticky='ne',
        command=lambda: exit_gui(None),
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['random_gen_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_random_gen,
        text='Generate Random Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['build_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_builder,
        text='Build New Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['modify_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_modify,
        text='Modify Existing Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['load_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='n',
        command=load_env_from_file,
        text='Load Custom Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['save_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='n',
        command=save_env_to_file,
        text='Save Custom Environment',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['run_sim_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(6, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_clingo_para,
        text='Run Simulation',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    FRAMES['main_menu_frame'].frame.rowconfigure(tuple(range(7)), weight=1)
    FRAMES['main_menu_frame'].frame.columnconfigure(tuple(range(3)), weight=1)
    FRAMES['main_menu_frame'].frame.grid_propagate(False)

def build_main_menu_help_frame():
    global WINDOWS, FRAMES, TEXTS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['main_menu_help_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("../help_texts/main_menu_help_text.txt", "r") as file:
        # TODO: change help text
        help_displaytext = file.read()

    TEXTS['main_menu_help_frame'] = Text(
        root=FRAMES['main_menu_help_frame'].frame,
        width=FRAMES['main_menu_help_frame'].width,
        height=FRAMES['main_menu_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=("Arial", int(FONT_SCALE * BASE_FONT)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    FRAMES['main_menu_help_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['main_menu_help_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['main_menu_help_frame'].frame.grid_propagate(False)

def build_main_menu_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT, CURRENT_IMG

    FRAMES['main_menu_env_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    CANVASES['main_menu_env_viewer_canvas'] = EnvCanvas(
        root=FRAMES['main_menu_env_viewer_frame'].frame,
        width=FRAMES['main_menu_env_viewer_frame'].width,
        height=FRAMES['main_menu_env_viewer_frame'].height,
        x=FRAMES['main_menu_env_viewer_frame'].width * 0,
        y=FRAMES['main_menu_env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image=CURRENT_IMG,
        rows=USER_PARAMS['rows'],
        cols=USER_PARAMS['cols'],
    )

def build_clingo_para_frame():
    global FRAMES, LABELS, BUTTONS, USER_PARAMS

    FRAMES['clingo_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['back_button'] = Button(
        root=FRAMES['clingo_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=switch_clingo_para_to_main,
        text='<',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    LABELS['clingo_label'] = Label(
        root=FRAMES['clingo_para_frame'].frame,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='nw',
        text='Clingo Path:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['clingo_entry'] = EntryField(
        root=FRAMES['clingo_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["clingo"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['clingo_error_label'] = Label(
        root=FRAMES['clingo_para_frame'].frame,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='nw',
        columnspan=2,
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['answer_label'] = Label(
        root=FRAMES['clingo_para_frame'].frame,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='nw',
        text='Answer to display:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['answer_entry'] = EntryField(
        root=FRAMES['clingo_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["answer"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['answer_error_label'] = Label(
        root=FRAMES['clingo_para_frame'].frame,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='nw',
        columnspan=2,
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    BUTTONS['select_lp_files_button'] = Button(
        root=FRAMES['clingo_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='n',
        columnspan=2,
        command=load_lp_files,
        text='Select LP Files',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['clingo_paths_label'] = Label(
        root=FRAMES['clingo_para_frame'].frame,
        grid_pos=(6, 1),
        padding=(0, 0),
        sticky='n',
        columnspan=2,
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    BUTTONS['run_sim_button'] = Button(
        root=FRAMES['clingo_para_frame'].frame,
        width=30,
        height=2,
        grid_pos=(7, 1),
        padding=(0, 0),
        sticky='n',
        columnspan=2,
        command=switch_clingo_para_to_result,
        text='Run Simulation',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    FRAMES['clingo_para_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['clingo_para_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['clingo_para_frame'].frame.rowconfigure(
        tuple(range(1,8)), weight=2
    )
    FRAMES['clingo_para_frame'].frame.columnconfigure(
        tuple(range(1,3)), weight=2
    )
    FRAMES['clingo_para_frame'].frame.grid_propagate(False)

    load_clingo_params()

def toggle_main_menu_help():
    if 'main_menu_help_frame' in FRAMES:
        FRAMES['main_menu_help_frame'].toggle_visibility()
    else:
        build_main_menu_help_frame()

def switch_main_to_random_gen():
    if 'main_menu_frame' in FRAMES:
        FRAMES['main_menu_frame'].destroy_frame()
        del FRAMES['main_menu_frame']
    if 'main_menu_help_frame' in FRAMES:
        FRAMES['main_menu_help_frame'].destroy_frame()
        del FRAMES['main_menu_help_frame']
    if 'main_menu_env_viewer_frame' in FRAMES:
        FRAMES['main_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['main_menu_env_viewer_frame']

    build_random_gen_para_frame()

def switch_main_to_builder():
    global BUILD_MODE
    BUILD_MODE = 'build'

    if 'main_menu_frame' in FRAMES:
        FRAMES['main_menu_frame'].destroy_frame()
        del FRAMES['main_menu_frame']
    if 'main_menu_help_frame' in FRAMES:
        FRAMES['main_menu_help_frame'].destroy_frame()
        del FRAMES['main_menu_help_frame']
    if 'main_menu_env_viewer_frame' in FRAMES:
        FRAMES['main_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['main_menu_env_viewer_frame']

    build_builder_para_frame()

def switch_main_to_modify():
    global BUILD_MODE
    BUILD_MODE = 'modify'

    if 'main_menu_frame' in FRAMES:
        FRAMES['main_menu_frame'].destroy_frame()
        del FRAMES['main_menu_frame']
    if 'main_menu_help_frame' in FRAMES:
        FRAMES['main_menu_help_frame'].destroy_frame()
        del FRAMES['main_menu_help_frame']
    if 'main_menu_env_viewer_frame' in FRAMES:
        FRAMES['main_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['main_menu_env_viewer_frame']

    build_builder_para_frame()

def switch_main_to_clingo_para():
    if 'main_menu_frame' in FRAMES:
        FRAMES['main_menu_frame'].destroy_frame()
        del FRAMES['main_menu_frame']
    if 'main_menu_help_frame' in FRAMES:
        FRAMES['main_menu_help_frame'].destroy_frame()
        del FRAMES['main_menu_help_frame']

    build_clingo_para_frame()

def switch_clingo_para_to_main():
    save_clingo_params()

    if 'clingo_para_frame' in FRAMES:
        FRAMES['clingo_para_frame'].destroy_frame()
        del FRAMES['clingo_para_frame']
    if 'main_menu_env_viewer_frame' in FRAMES:
        FRAMES['main_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['main_menu_env_viewer_frame']

    create_main_menu()

def switch_clingo_para_to_result():
    if save_clingo_params() == -1:
        return

    if 'clingo_para_frame' in FRAMES:
        FRAMES['clingo_para_frame'].destroy_frame()
        del FRAMES['clingo_para_frame']
    if 'main_menu_env_viewer_frame' in FRAMES:
        FRAMES['main_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['main_menu_env_viewer_frame']

    run_simulation()
    create_result_menu()

def reload_main_env_viewer():
    global FRAMES

    if 'main_menu_env_viewer_frame' in FRAMES:
        FRAMES['main_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['main_menu_env_viewer_frame']

    build_main_menu_env_viewer()

def load_lp_files():
    files = filedialog.askopenfilenames(
        title="Select LP Files",
        initialdir='../data',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    USER_PARAMS['lpFiles'] = list(files)
    displaytext = "\n".join(files)

    LABELS['clingo_paths_label'].label.config(text=displaytext)

def save_clingo_params():
    global USER_PARAMS, DEFAULT_PARAMS

    err_count = 0

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_PARAMS:
            continue
        elif key not in ['answer', 'clingo']:
            continue

        data = ENTRY_FIELDS[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'clingo':
                data = data
            else:
                data = int(data)

            LABELS[f'{key}_error_label'].hide_label()
        except Exception as e:
            err = type(e)
            LABELS[f'{key}_error_label'].label.config(text=ERR_DICT[key][err])
            LABELS[f'{key}_error_label'].place_label()
            if err not in ERR_DICT[key]:
                print(e)
                print(err)
                print(data)
            err_count += 1

        if type(data) is not str or key == 'clingo':
            USER_PARAMS[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_clingo_params():
    global USER_PARAMS, DEFAULT_PARAMS

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_PARAMS:
            continue
        elif key not in ['answer', 'clingo']:
            continue
        elif USER_PARAMS[key] is None:
            continue
        else:
            ENTRY_FIELDS[field].insert_string(str(USER_PARAMS[key]))

    if USER_PARAMS['lpFiles'] is not None:
        displaytext = "\n".join(USER_PARAMS["lpFiles"])
        LABELS['clingo_paths_label'].label.config(text=displaytext)
    return





# random generation

def random_gen_change_to_start_or_main():
    global LAST_MENU

    save_random_gen_env_params()

    if LAST_MENU == 'start':
        random_gen_para_to_start()
    else:
        random_gen_para_to_main()

def random_gen_para_to_start():
    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].destroy_frame()
        del FRAMES['random_gen_para_frame']

    create_start_menu()

def random_gen_para_to_main():
    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].destroy_frame()
        del FRAMES['random_gen_para_frame']

    create_main_menu()

def build_random_gen_para_frame():
    global WINDOWS, FRAMES, LABELS, ENTRY_FIELDS, SCREENWIDTH, SCREENHEIGHT, \
        DEFAULT_PARAMS

    FRAMES['random_gen_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['back_button'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_change_to_start_or_main,
        text='<',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    LABELS['rows_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='nw',
        text='Environment rows:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['rows_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["rows"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['rows_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(1, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['cols_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='nw',
        text='Environment columns:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['cols_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["cols"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['cols_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(2, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['agents_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='nw',
        text='Number of agents:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['agents_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["agents"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['agents_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(3, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['cities_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of cities:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['cities_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["cities"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['cities_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(4, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['seed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='nw',
        text='Seed:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['seed_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["seed"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['seed_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(5, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['grid_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(6, 1),
        padding=(0, 0),
        sticky='nw',
        text='Use grid mode:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['grid_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["grid"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['grid_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(6, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['intercity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(7, 1),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of rails between cities:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['intercity_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["intercity"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['intercity_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(7, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['incity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(8, 1),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of rail pairs in cities:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['incity_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["incity"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['incity_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(8, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['remove_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(9, 1),
        padding=(0, 0),
        sticky='nw',
        text='Remove agents on arrival:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['remove_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(9, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["remove"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['remove_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(9, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(10, 1),
        padding=(0, 0),
        sticky='nw',
        text='Speed ratio map for trains:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['speed_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(10, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["speed"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['speed_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(10, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(11, 1),
        padding=(0, 0),
        sticky='nw',
        text='Malfunction rate:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['malfunction_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(11, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["malfunction"][0]}/'
             f'{DEFAULT_PARAMS["malfunction"][1]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['malfunction_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(11, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(12, 1),
        padding=(0, 0),
        sticky='nw',
        text='Min. duration for malfunctions:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['min_duration_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(12, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["min"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['min_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(12, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(13, 1),
        padding=(0, 0),
        sticky='nw',
        text='Max. duration for malfunction:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['max_duration_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(13, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["max"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['max_error_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(13, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    BUTTONS['generate_button'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(14, 1),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_para_to_env,
        text='Generate',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['advanced_options'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(14, 2),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_toggle_advanced_para_options,
        text='Advanced Options',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    FRAMES['random_gen_para_frame'].frame.rowconfigure(
        tuple(range(15)), weight=1
    )
    FRAMES['random_gen_para_frame'].frame.columnconfigure(
        tuple(range(4)), weight=1
    )
    FRAMES['random_gen_para_frame'].frame.grid_propagate(False)

    load_random_gen_env_params()

def random_gen_para_to_env():
    global CURRENT_IMG, CURRENT_DF, CURRENT_ARRAY

    if save_random_gen_env_params() == -1:
        return

    tracks, trains = gen_env(USER_PARAMS)

    if len(trains):
        start_pos = list(zip(trains['x'], trains['y']))
        end_pos = list(zip(trains['x_end'], trains['y_end']))

        CURRENT_DF = pd.DataFrame({
            'start_pos': start_pos,
            'dir': trains['dir'],
            'end_pos': end_pos,
            'e_dep': trains['e_dep'],
            'l_arr': trains['l_arr']
        })
    else:
        CURRENT_DF = pd.DataFrame(
            columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
        )

    direction = {
        'n': 1,
        'e': 2,
        's': 3,
        'w': 4,
    }

    tracks = np.array(tracks)
    CURRENT_ARRAY = np.zeros((3, *tracks.shape), dtype=int)
    CURRENT_ARRAY[0] = tracks

    for _, row in CURRENT_DF.iterrows():
        CURRENT_ARRAY[1][row['start_pos']] = direction[row['dir']]
        if row['end_pos'] != (-1, -1):
            CURRENT_ARRAY[2][row['end_pos']] = 5

    CURRENT_IMG = '../data/running_tmp.png'

    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].destroy_frame()
        del FRAMES['random_gen_para_frame']

    build_random_gen_env_viewer()
    build_random_gen_env_menu()

def random_gen_env_to_para():
    if 'random_gen_env_viewer_frame' in FRAMES:
        FRAMES['random_gen_env_viewer_frame'].destroy_frame()
        del FRAMES['random_gen_env_viewer_frame']
    if 'random_gen_env_menu_frame' in FRAMES:
        FRAMES['random_gen_env_menu_frame'].destroy_frame()
        del FRAMES['random_gen_env_menu_frame']

    build_random_gen_para_frame()

def build_random_gen_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT, CURRENT_IMG

    FRAMES['random_gen_env_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    CANVASES['gen_env_viewer_canvas'] = EnvCanvas(
        root=FRAMES['random_gen_env_viewer_frame'].frame,
        width=FRAMES['random_gen_env_viewer_frame'].width,
        height=FRAMES['random_gen_env_viewer_frame'].height,
        x=FRAMES['random_gen_env_viewer_frame'].width * 0,
        y=FRAMES['random_gen_env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image=CURRENT_IMG,
        rows=USER_PARAMS['rows'],
        cols=USER_PARAMS['cols'],
    )

def build_random_gen_env_menu():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT, TEXTS, \
        CURRENT_DF

    FRAMES['random_gen_env_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['back_button'] = Button(
        root=FRAMES['random_gen_env_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_env_to_para,
        text='<',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['return_to_menu_button'] = Button(
        root=FRAMES['random_gen_env_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(2, 0),
        padding=(0, 0),
        sticky='n',
        command=switch_random_gen_to_main,
        text='Return To Main Menu',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    current_df_to_env_text()
    with open("../data/current_df.txt", "r") as file:
        displaytext = file.read()

    TEXTS['random_gen_env_trains'] = Text(
        root=FRAMES['random_gen_env_menu_frame'].frame,
        width=FRAMES['random_gen_env_menu_frame'].width,
        height=FRAMES['random_gen_env_menu_frame'].height * 0.75,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='nesw',
        text=displaytext,
        font=("Courier", int(FONT_SCALE * 15)),
        wrap='word',
        foreground_color='#FFFFFF',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    FRAMES['random_gen_env_menu_frame'].frame.rowconfigure((0,2), weight=1)
    FRAMES['random_gen_env_menu_frame'].frame.rowconfigure(1, weight=15)
    FRAMES['random_gen_env_menu_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['random_gen_env_menu_frame'].frame.grid_propagate(False)

def random_gen_toggle_advanced_para_options():
    LABELS['seed_label'].toggle_visibility()
    ENTRY_FIELDS['seed_entry'].toggle_visibility()
    LABELS['grid_label'].toggle_visibility()
    ENTRY_FIELDS['grid_entry'].toggle_visibility()
    LABELS['intercity_label'].toggle_visibility()
    ENTRY_FIELDS['intercity_entry'].toggle_visibility()
    LABELS['incity_label'].toggle_visibility()
    ENTRY_FIELDS['incity_entry'].toggle_visibility()
    LABELS['remove_label'].toggle_visibility()
    ENTRY_FIELDS['remove_entry'].toggle_visibility()
    LABELS['speed_label'].toggle_visibility()
    ENTRY_FIELDS['speed_entry'].toggle_visibility()
    LABELS['malfunction_label'].toggle_visibility()
    ENTRY_FIELDS['malfunction_entry'].toggle_visibility()
    LABELS['min_duration_label'].toggle_visibility()
    ENTRY_FIELDS['min_duration_entry'].toggle_visibility()
    LABELS['max_duration_label'].toggle_visibility()
    ENTRY_FIELDS['max_duration_entry'].toggle_visibility()
    return

def switch_random_gen_to_main():
    if 'random_gen_env_viewer_frame' in FRAMES:
        FRAMES['random_gen_env_viewer_frame'].destroy_frame()
        del FRAMES['random_gen_env_viewer_frame']
    if 'random_gen_env_menu_frame' in FRAMES:
        FRAMES['random_gen_env_menu_frame'].destroy_frame()
        del FRAMES['random_gen_env_menu_frame']

    create_main_menu()

def save_random_gen_env_params():
    global USER_PARAMS, DEFAULT_PARAMS

    def str_to_bool(s):
        if isinstance(s, str):
            s = s.lower()
            if s == "true":
                return True
            elif s == "false":
                return False
        raise ValueError(f"Invalid boolean string: {s}")

    err_count = 0

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_PARAMS:
            continue
        elif key in ['answer', 'clingo', 'lpFiles']:
            continue

        data = ENTRY_FIELDS[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'grid' or key == 'remove':
                data = str_to_bool(data)
            elif key == 'speed':
                data = ast.literal_eval(data)
            elif key == 'malfunction':
                data = (int(data.split('/')[0]),int(data.split('/')[1]))
            else:
                data = int(data)

            LABELS[f'{key}_error_label'].hide_label()
        except Exception as e:
            err = type(e)
            LABELS[f'{key}_error_label'].label.config(text=ERR_DICT[key][err])
            LABELS[f'{key}_error_label'].place_label()
            if err not in ERR_DICT[key]:
                print(e)
                print(err)
                print(data)
            err_count += 1

        if type(data) is not str:
            USER_PARAMS[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_random_gen_env_params():
    global USER_PARAMS, DEFAULT_PARAMS

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_PARAMS:
            continue
        elif key in ['answer', 'clingo', 'lpFiles']:
            continue
        elif USER_PARAMS[key] is None:
            continue
        elif key == 'malfunction':
            ENTRY_FIELDS[field].insert_string(
                f'{USER_PARAMS["malfunction"][0]}/'
                f'{USER_PARAMS["malfunction"][1]}'
            )
        else:
            ENTRY_FIELDS[field].insert_string(str(USER_PARAMS[key]))





# builder

def builder_change_to_start_or_main():
    global LAST_MENU

    save_builder_env_params()

    if LAST_MENU == 'start':
        builder_para_to_start()
    else:
        builder_para_to_main()

def builder_para_to_start():
    global BUILD_MODE
    BUILD_MODE = None

    if 'builder_para_frame' in FRAMES:
        FRAMES['builder_para_frame'].destroy_frame()
        del FRAMES['builder_para_frame']

    create_start_menu()

def builder_para_to_main():
    global BUILD_MODE
    BUILD_MODE = None

    if 'builder_para_frame' in FRAMES:
        FRAMES['builder_para_frame'].destroy_frame()
        del FRAMES['builder_para_frame']

    create_main_menu()

def build_builder_para_frame():
    global WINDOWS, FRAMES, LABELS, ENTRY_FIELDS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['builder_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['back_button'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command= builder_change_to_start_or_main,
        text='<',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    LABELS['rows_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='nw',
        text='Environment rows:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['rows_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["rows"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['rows_error_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(1, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['cols_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='nw',
        text='Environment columns:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['cols_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["cols"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['cols_error_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(2, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['remove_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='nw',
        text='Remove agents on arrival:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['remove_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["remove"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['remove_error_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(3, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='nw',
        text='Speed ratio map for trains:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['speed_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["speed"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['speed_error_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(4, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='nw',
        text='Malfunction rate:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['malfunction_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["malfunction"][0]}/'
             f'{DEFAULT_PARAMS["malfunction"][1]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['malfunction_error_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(5, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(6, 1),
        padding=(0, 0),
        sticky='nw',
        text='Min. duration for malfunctions:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['min_duration_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["min"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['min_error_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(6, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(7, 1),
        padding=(0, 0),
        sticky='nw',
        text='Max. duration for malfunction:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['max_duration_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_PARAMS["max"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['max_error_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(7, 3),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    BUTTONS['build_button'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(8, 1),
        padding=(0, 0),
        sticky='nw',
        command=builder_para_to_track_grid,
        text='Build',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['advanced_options'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        command=builder_toggle_advanced_para_options,
        text='Advanced Options',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    FRAMES['builder_para_frame'].frame.rowconfigure(
        tuple(range(9)), weight=1
    )
    FRAMES['builder_para_frame'].frame.columnconfigure(
        tuple(range(4)), weight=1
    )
    FRAMES['builder_para_frame'].frame.grid_propagate(False)

    load_builder_env_params()

def builder_para_to_track_grid():
    global BUILD_MODE, CURRENT_ARRAY, CURRENT_DF, DEFAULT_PARAMS, \
        USER_PARAMS, CURRENT_BACKUP_ARRAY, CURRENT_BACKUP_DF

    if save_builder_env_params() == -1:
        return

    if 'builder_para_frame' in FRAMES:
        FRAMES['builder_para_frame'].destroy_frame()
        del FRAMES['builder_para_frame']

    if USER_PARAMS['rows'] is not None:
        rows = USER_PARAMS['rows']
    else:
        rows = DEFAULT_PARAMS['rows']

    if USER_PARAMS['cols'] is not None:
        cols = USER_PARAMS['cols']
    else:
        cols = DEFAULT_PARAMS['cols']

    if BUILD_MODE == 'build':
        CURRENT_ARRAY = np.zeros((3,rows,cols), dtype=int)
        CURRENT_DF = pd.DataFrame(
            columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
        )
    else:
        current_rows, current_cols = CURRENT_ARRAY.shape[1:3]

        if (rows,cols) != (current_rows,current_cols):
            if current_rows < rows:
                # add array rows
                CURRENT_ARRAY = np.pad(
                    CURRENT_ARRAY,
                    pad_width=[(0, 0), (0, rows-current_rows), (0, 0)],
                    mode='constant',
                    constant_values=0
                )
            elif current_rows > rows:
                # remove array rows
                CURRENT_ARRAY = CURRENT_ARRAY[:, :rows, :]

            if current_cols < cols:
                # add array cols
                CURRENT_ARRAY = np.pad(
                    CURRENT_ARRAY,
                    pad_width=[(0, 0), (0, 0), (0, cols-current_cols)],
                    mode='constant',
                    constant_values=0
                )
            elif current_cols > cols:
                # remove array cols
                CURRENT_ARRAY = CURRENT_ARRAY[:, :, :cols]

            if len(CURRENT_DF) > 0:
                # remove trains not on the grid anymore
                CURRENT_DF.drop(
                    index=CURRENT_DF[CURRENT_DF['start_pos'].apply(
                        lambda t: t[0] > rows-1 or t[1] > cols-1
                    )].index,
                    inplace=True
                )
                CURRENT_DF.reset_index(drop=True, inplace=True)

                # reset station not on the grid anymore
                for index, row in CURRENT_DF.iterrows():
                    if (row['end_pos'][0] > rows - 1 or
                            row['end_pos'][1] > cols - 1):
                        CURRENT_DF.at[index, 'end_pos'] = (-1, -1)

    CURRENT_BACKUP_ARRAY = CURRENT_ARRAY.copy()
    CURRENT_BACKUP_DF = CURRENT_DF.copy()

    build_track_builder_menu_frame()
    build_builder_grid_frame()

def builder_track_grid_to_para():
    global FRAMES

    if 'track_builder_menu_frame' in FRAMES:
        FRAMES['track_builder_menu_frame'].destroy_frame()
        del FRAMES['track_builder_menu_frame']
    if 'builder_grid_frame' in FRAMES:
        FRAMES['builder_grid_frame'].destroy_frame()
        del FRAMES['builder_grid_frame']

    build_builder_para_frame()

def build_builder_grid_frame():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT, \
        CURRENT_ARRAY, CURRENT_DF

    FRAMES['builder_grid_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    CANVASES['builder_grid_canvas'] = BuildCanvas(
        root=FRAMES['builder_grid_frame'].frame,
        width=FRAMES['builder_grid_frame'].width,
        height=FRAMES['builder_grid_frame'].height,
        x=FRAMES['builder_grid_frame'].width * 0,
        y=FRAMES['builder_grid_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        array=CURRENT_ARRAY,
        train_data=CURRENT_DF,
    )

    FRAMES['builder_grid_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['builder_grid_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['builder_grid_frame'].frame.grid_propagate(False)

def build_track_builder_menu_frame():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['track_builder_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['back_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command= builder_track_grid_to_para,
        text='<',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['horizontal_straight_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 1),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(1025),
        image='../data/png/Gleis_horizontal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['vertical_straight_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 2),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(32800),
        image='../data/png/Gleis_vertikal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_top_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 5),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(2064),
        image='../data/png/Gleis_kurve_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_top_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 6),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(72),
        image='../data/png/Gleis_kurve_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_bottom_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 7),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(16386),
        image='../data/png/Gleis_kurve_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_bottom_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 8),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(4608),
        image='../data/png/Gleis_kurve_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_top_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 1),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(3089),
        image='../data/png/Weiche_horizontal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_top_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 2),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(1097),
        image='../data/png/Weiche_horizontal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_bottom_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 3),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(17411),
        image='../data/png/Weiche_horizontal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_bottom_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 4),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(5633),
        image='../data/png/Weiche_horizontal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_top_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 5),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(34864),
        image='../data/png/Weiche_vertikal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_top_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 6),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(32872),
        image='../data/png/Weiche_vertikal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_bottom_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 7),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(49186),
        image='../data/png/Weiche_vertikal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_bottom_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(2, 8),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(37408),
        image='../data/png/Weiche_vertikal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['diamond_crossing_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(3, 1),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(33825),
        image='../data/png/Gleis_Diamond_Crossing.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['single_slip_top_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(3, 5),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(35889),
        image='../data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    BUTTONS['single_slip_top_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(3, 6),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(33897),
        image='../data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    BUTTONS['single_slip_bottom_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(3, 7),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(50211),
        image='../data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['single_slip_bottom_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(3, 8),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(38433),
        image='../data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['double_slip_top_left_bottom_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(4, 1),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(52275),
        image='../data/png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['double_slip_bottom_left_top_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(4, 2),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(38505),
        image='../data/png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['symmetrical_top_left_top_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(4, 5),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(2136),
        image='../data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    BUTTONS['symmetrical_top_right_bottom_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(4, 6),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(16458),
        image='../data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['symmetrical_bottom_left_bottom_right_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(4, 7),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(20994),
        image='../data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['symmetrical_top_left_bottom_left_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(4, 8),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(6672),
        image='../data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    BUTTONS['delete_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(5, 1),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(0),
        image='../data/png/eraser.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['reset_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 5),
        padding=(0, 0),
        columnspan=2,
        command=lambda: open_reset_frame(FRAMES['track_builder_menu_frame']),
        text='RESET',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['train_builder_button'] = Button(
        root=FRAMES['track_builder_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(6, 1),
        padding=(0, 0),
        columnspan=8,
        command=builder_track_to_train,
        text='Trains',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    FRAMES['track_builder_menu_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['track_builder_menu_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['track_builder_menu_frame'].frame.rowconfigure(
        tuple(range(1,7)), weight=2
    )
    FRAMES['track_builder_menu_frame'].frame.columnconfigure(
        tuple(range(1,9)), weight=2
    )
    FRAMES['track_builder_menu_frame'].frame.grid_propagate(False)

def builder_track_to_train():
    global FRAMES, CANVASES

    if 'track_builder_menu_frame' in FRAMES:
        FRAMES['track_builder_menu_frame'].destroy_frame()
        del FRAMES['track_builder_menu_frame']

    CANVASES['builder_grid_canvas'].current_selection = None

    build_train_builder_menu_frame()

def builder_train_to_track():
    global FRAMES, CANVASES

    if 'train_builder_menu_frame' in FRAMES:
        FRAMES['train_builder_menu_frame'].destroy_frame()
        del FRAMES['train_builder_menu_frame']

    CANVASES['builder_grid_canvas'].current_selection = None

    build_track_builder_menu_frame()

def build_train_builder_menu_frame():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT, CURRENT_DF

    FRAMES['train_builder_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['back_button'] = Button(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command= builder_train_to_track,
        text='<',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['train_north_button'] = Button(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 1),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(1),
        image='../data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['train_east_button'] = Button(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 2),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(2),
        image='../data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    BUTTONS['train_south_button'] = Button(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 3),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(3),
        image='../data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    BUTTONS['train_west_button'] = Button(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=int(FONT_SCALE * 80),
        height=int(FONT_SCALE * 80),
        grid_pos=(1, 4),
        padding=(0, 0),
        command=lambda: CANVASES['builder_grid_canvas'].select(4),
        image='../data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['reset_button'] = Button(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 6),
        padding=(0, 0),
        command=lambda: open_reset_frame(FRAMES['train_builder_menu_frame']),
        text='RESET',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    FRAMES['train_config_list_canvas_frame'] = Frame(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=FRAMES['train_builder_menu_frame'].width * 0.75,
        height=FRAMES['train_builder_menu_frame'].height * 0.6,
        grid_pos=(2, 1),
        padding=(0, 0),
        columnspan=6,
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['finish_building_button'] = Button(
        root=FRAMES['train_builder_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(3, 1),
        padding=(0, 0),
        columnspan=6,
        command=builder_train_grid_to_env,
        text='Finish Building',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    FRAMES['train_builder_menu_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['train_builder_menu_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['train_builder_menu_frame'].frame.rowconfigure(1, weight=2)
    FRAMES['train_builder_menu_frame'].frame.columnconfigure(
        tuple(range(1,7)), weight=2
    )
    FRAMES['train_builder_menu_frame'].frame.rowconfigure(2, weight=2)
    FRAMES['train_builder_menu_frame'].frame.rowconfigure(3, weight=2)
    FRAMES['train_builder_menu_frame'].frame.grid_propagate(False)

    CANVASES['train_config_list'] = TrainListCanvas(
        root=FRAMES['train_config_list_canvas_frame'].frame,
        width=FRAMES['train_config_list_canvas_frame'].width,
        height=FRAMES['train_config_list_canvas_frame'].height,
        x=FRAMES['train_config_list_canvas_frame'].width * 0,
        y=FRAMES['train_config_list_canvas_frame'].height * 0,
        background_color='#000000',
        border_width=0,
        grid=CANVASES['builder_grid_canvas'],
        train_data=CURRENT_DF,
        outer_frame=FRAMES['train_builder_menu_frame'].frame,
        base_font=BASE_FONT,
        font_scale=FONT_SCALE,
    )
    CANVASES['builder_grid_canvas'].train_list = CANVASES['train_config_list']

def builder_train_grid_to_env():
    global FRAMES, CANVASES, CURRENT_BACKUP_ARRAY, CURRENT_BACKUP_DF, \
        CURRENT_IMG

    # TODO: error if trains is empty in train builder
    # TODO: error if tracks is empty ???? in track builder

    tracks = CURRENT_ARRAY[0]
    x = [t[1] for t in CURRENT_DF['start_pos']]
    y = [t[0] for t in CURRENT_DF['start_pos']]
    x_end = [t[1] for t in CURRENT_DF['end_pos']]
    y_end = [t[0] for t in CURRENT_DF['end_pos']]

    trains = pd.DataFrame({
        'id': CURRENT_DF.index,
        'x': x,
        'y': y,
        'dir': CURRENT_DF['dir'],
        "x_end": x_end,
        "y_end": y_end,
        "e_dep": CURRENT_DF['e_dep'],
        "l_arr": CURRENT_DF['l_arr']
    })

    USER_PARAMS['agents'] = len(trains)

    env = create_custom_env(tracks, trains, USER_PARAMS)
    os.makedirs("../data", exist_ok=True)
    save_png(env, "../data/running_tmp.png")

    CURRENT_IMG = '../data/running_tmp.png'

    if 'train_builder_menu_frame' in FRAMES:
        FRAMES['train_builder_menu_frame'].destroy_frame()
        del FRAMES['train_builder_menu_frame']
    if 'builder_grid_frame' in FRAMES:
        FRAMES['builder_grid_frame'].destroy_frame()
        del FRAMES['builder_grid_frame']

    CURRENT_BACKUP_ARRAY = CURRENT_ARRAY.copy()
    CURRENT_BACKUP_DF = CURRENT_DF.copy()

    build_builder_env_viewer()
    build_builder_env_menu()

def build_builder_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT, CURRENT_IMG

    FRAMES['builder_env_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    CANVASES['builder_env_viewer_canvas'] = EnvCanvas(
        root=FRAMES['builder_env_viewer_frame'].frame,
        width=FRAMES['builder_env_viewer_frame'].width,
        height=FRAMES['builder_env_viewer_frame'].height,
        x=FRAMES['builder_env_viewer_frame'].width * 0,
        y=FRAMES['builder_env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image=CURRENT_IMG,
        rows=USER_PARAMS['rows'],
        cols=USER_PARAMS['cols'],
    )

    FRAMES['builder_env_viewer_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['builder_env_viewer_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['builder_env_viewer_frame'].frame.grid_propagate(False)

def build_builder_env_menu():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT, TEXTS, \
        CURRENT_DF

    FRAMES['builder_env_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['return_to_menu_button'] = Button(
        root=FRAMES['builder_env_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='n',
        command=switch_builder_to_main,
        text='Return To Main Menu',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    current_df_to_env_text()
    with open("../data/current_df.txt", "r") as file:
        displaytext = file.read()

    TEXTS['builder_env_trains'] = Text(
        root=FRAMES['builder_env_menu_frame'].frame,
        width=FRAMES['builder_env_menu_frame'].width,
        height=FRAMES['builder_env_menu_frame'].height * 0.75,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=displaytext,
        font=("Courier", int(FONT_SCALE * 15)),
        wrap='word',
        foreground_color='#FFFFFF',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    FRAMES['builder_env_menu_frame'].frame.rowconfigure(0, weight=15)
    FRAMES['builder_env_menu_frame'].frame.rowconfigure(1, weight=1)
    FRAMES['builder_env_menu_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['builder_env_menu_frame'].frame.grid_propagate(False)

def builder_toggle_advanced_para_options():
    LABELS['remove_label'].toggle_visibility()
    ENTRY_FIELDS['remove_entry'].toggle_visibility()
    LABELS['speed_label'].toggle_visibility()
    ENTRY_FIELDS['speed_entry'].toggle_visibility()
    LABELS['malfunction_label'].toggle_visibility()
    ENTRY_FIELDS['malfunction_entry'].toggle_visibility()
    LABELS['min_duration_label'].toggle_visibility()
    ENTRY_FIELDS['min_duration_entry'].toggle_visibility()
    LABELS['max_duration_label'].toggle_visibility()
    ENTRY_FIELDS['max_duration_entry'].toggle_visibility()
    return

def switch_builder_to_main():
    global BUILD_MODE
    BUILD_MODE = None

    if 'builder_env_viewer_frame' in FRAMES:
        FRAMES['builder_env_viewer_frame'].destroy_frame()
        del FRAMES['builder_env_viewer_frame']
    if 'builder_env_menu_frame' in FRAMES:
        FRAMES['builder_env_menu_frame'].destroy_frame()
        del FRAMES['builder_env_menu_frame']

    create_main_menu()

def save_builder_env_params():

    def str_to_bool(s):
        if isinstance(s, str):
            s = s.lower()
            if s == "true":
                return True
            elif s == "false":
                return False
        raise ValueError(f"Invalid boolean string: {s}")

    err_count = 0

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_PARAMS:
            continue
        if key in ['answer', 'clingo', 'lpFiles', 'agents', 'cities', 'seed',
                   'grid', 'intercity', 'incity']:
            continue

        data = ENTRY_FIELDS[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'grid' or key == 'remove':
                data = str_to_bool(data)
            elif key == 'speed':
                data = ast.literal_eval(data)
            elif key == 'malfunction':
                data = (int(data.split('/')[0]),int(data.split('/')[1]))
            else:
                data = int(data)

            LABELS[f'{key}_error_label'].hide_label()
        except Exception as e:
            err = type(e)
            LABELS[f'{key}_error_label'].label.config(text=ERR_DICT[key][err])
            LABELS[f'{key}_error_label'].place_label()
            if err not in ERR_DICT[key]:
                print(e)
                print(err)
                print(data)
            err_count += 1

        if type(data) is not str:
            USER_PARAMS[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_builder_env_params():
    global USER_PARAMS

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_PARAMS:
            continue
        elif key in ['answer', 'clingo', 'lpFiles', 'agents', 'cities', 'seed',
                     'grid', 'intercity', 'incity']:
            continue
        elif USER_PARAMS[key] is None:
            continue
        elif key == 'malfunction':
            ENTRY_FIELDS[field].insert_string(
                f'{USER_PARAMS["malfunction"][0]}/'
                f'{USER_PARAMS["malfunction"][1]}'
            )
        else:
            ENTRY_FIELDS[field].insert_string(str(USER_PARAMS[key]))

def open_reset_frame(parent_frame):
    global FRAMES, LABELS, BUTTONS

    FRAMES['reset_frame'] = Frame(
        root=parent_frame.root,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    LABELS['reset_label'] = Label(
        root=FRAMES['reset_frame'].frame,
        grid_pos=(0, 0),
        padding=(0, 0),
        columnspan=2,
        sticky='nesw',
        text='RESET GRID?',
        font=('Arial', int(FONT_SCALE * 30), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    BUTTONS['yes_reset_button'] = Button(
        root=FRAMES['reset_frame'].frame,
        width=4,
        height=1,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='n',
        command=reset_builder_grid,
        text='YES',
        font=('Arial', int(FONT_SCALE * BASE_FONT)),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['no_reset_button'] = Button(
        root=FRAMES['reset_frame'].frame,
        width=4,
        height=1,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='n',
        command=FRAMES['reset_frame'].destroy_frame,
        text='NO',
        font=('Arial', int(FONT_SCALE * BASE_FONT)),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    FRAMES['reset_frame'].frame.rowconfigure(0, weight=2)
    FRAMES['reset_frame'].frame.rowconfigure(1, weight=1)
    FRAMES['reset_frame'].frame.columnconfigure((0, 1), weight=1)
    FRAMES['reset_frame'].frame.grid_propagate(False)

def reset_builder_grid():
    global CURRENT_ARRAY, CURRENT_DF, CURRENT_BACKUP_ARRAY, CURRENT_BACKUP_DF

    CURRENT_ARRAY = CURRENT_BACKUP_ARRAY.copy()
    CURRENT_DF = CURRENT_BACKUP_DF.copy()

    if 'track_builder_menu_frame' in FRAMES:
        FRAMES['track_builder_menu_frame'].destroy_frame()
        del FRAMES['track_builder_menu_frame']
    if 'train_builder_menu_frame' in FRAMES:
        FRAMES['train_builder_menu_frame'].destroy_frame()
        del FRAMES['train_builder_menu_frame']
    if 'builder_grid_frame' in FRAMES:
        FRAMES['builder_grid_frame'].destroy_frame()
        del FRAMES['builder_grid_frame']

    if 'reset_frame' in FRAMES:
        FRAMES['reset_frame'].destroy_frame()
        del FRAMES['reset_frame']

    build_track_builder_menu_frame()
    build_builder_grid_frame()





# result menu

def create_result_menu():
    build_result_env_viewer()
    build_result_menu()

def build_result_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT, CURRENT_PATHS, \
        CURRENT_IMG

    FRAMES['result_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    CANVASES['result_viewer_canvas'] = ResultCanvas(
        root=FRAMES['result_viewer_frame'].frame,
        width=FRAMES['result_viewer_frame'].width,
        height=FRAMES['result_viewer_frame'].height,
        x=FRAMES['result_viewer_frame'].width * 0,
        y=FRAMES['result_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image=CURRENT_IMG,
        paths_df=CURRENT_PATHS,
        rows=USER_PARAMS['rows'],
        cols=USER_PARAMS['cols'],
    )
    FRAMES['result_viewer_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['result_viewer_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['result_viewer_frame'].frame.grid_propagate(False)

def build_result_menu():
    FRAMES['result_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['show_time_table_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(1, 0),
        padding=(0, 0),
        command=stub,
        text='Show Time Table',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['show_gif_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(2, 0),
        padding=(0, 0),
        command=stub,
        text='Show GIF',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    FRAMES['path_list_canvas_frame'] = Frame(
        FRAMES['result_menu_frame'].frame,
        width=FRAMES['result_menu_frame'].width * 0.5,
        height=FRAMES['result_menu_frame'].height * 0.25,
        grid_pos=(4,0),
        padding=(0,0),
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['return_to_menu_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(5, 0),
        padding=(0, 0),
        command=switch_result_to_main,
        text='Return To Main Menu',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    FRAMES['result_menu_frame'].frame.rowconfigure((0,1,2,3,4,5), weight=1)
    FRAMES['result_menu_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['result_menu_frame'].frame.grid_propagate(False)

    CANVASES['path_list_canvas'] = PathListCanvas(
        root=FRAMES['path_list_canvas_frame'].frame,
        width=FRAMES['path_list_canvas_frame'].width,
        height=FRAMES['path_list_canvas_frame'].height,
        x=FRAMES['path_list_canvas_frame'].width * 0,
        y=FRAMES['path_list_canvas_frame'].height * 0,
        background_color='#000000',
        border_width=0,
        train_data=CURRENT_DF,
        grid=CANVASES['result_viewer_canvas'],
        base_font=BASE_FONT,
        font_scale=FONT_SCALE,
    )

    BUTTONS['toggle_all_paths_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(3, 0),
        padding=(0, 0),
        command=CANVASES['path_list_canvas'].toggle_all_paths,
        text='Toggle All Paths',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

def switch_result_to_main():
    if 'result_viewer_frame' in FRAMES:
        FRAMES['result_viewer_frame'].destroy_frame()
        del FRAMES['result_viewer_frame']
    if 'result_menu_frame' in FRAMES:
        FRAMES['result_menu_frame'].destroy_frame()
        del FRAMES['result_menu_frame']

    create_main_menu()





# functions

def current_df_to_env_text():
    global CURRENT_DF

    def format_row(index, row):
        new_line = (f"| {index:>8} | {str(row['start_pos']):>14} "
                    f"| {row['dir']:^3} | {str(row['end_pos']):>14} "
                    f"| {row['e_dep']:>7} | {row['l_arr']:>7} |")
        return new_line

    header = ("| Train ID | Start Position | Dir |   "
              "End Position |   E Dep |   L Arr |")
    divider = ("|----------|----------------|-----|"
               "----------------|---------|---------|")

    new_rows = [format_row(index, row) for index, row in CURRENT_DF.iterrows()]

    with open('../data/current_df.txt', "w") as file:
        file.write(header + "\n")
        file.write(divider + "\n")
        file.writelines(new_row + "\n" for new_row in new_rows)

def save_user_data_to_file():
    global USER_PARAMS

    with open('../data/user_params.json', 'w') as file:
        json.dump(USER_PARAMS, file, indent=4)

def load_user_data_from_file():
    global USER_PARAMS, DEFAULT_PARAMS

    with open('../data/user_params.json', 'r') as file:
        data = json.load(file)

    if data['speed'] is not None:
        data['speed'] = {int(k): v for k, v in data['speed'].items()}
    if data['malfunction'] is not None:
        data['malfunction'] = (data['malfunction'][0], data['malfunction'][1])

    USER_PARAMS = data

    # use default if no user parameters given
    for key in USER_PARAMS:
        if USER_PARAMS[key] is None or USER_PARAMS[key] == []:
            USER_PARAMS[key] = DEFAULT_PARAMS[key]

def load_env_from_file():
    global CURRENT_ARRAY, CURRENT_DF, CURRENT_IMG, LAST_MENU, USER_PARAMS

    file = filedialog.askopenfilename(
        title="Select LP Environment File",
        initialdir='../environments',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    if not file:
        return

    tracks, trains = lp_to_env(file)

    if len(trains):
        start_pos = list(zip(trains['x'], trains['y']))
        end_pos = list(zip(trains['x_end'], trains['y_end']))

        CURRENT_DF = pd.DataFrame({
            'start_pos': start_pos,
            'dir': trains['dir'],
            'end_pos': end_pos,
            'e_dep': trains['e_dep'],
            'l_arr': trains['l_arr']
        })
    else:
        CURRENT_DF = pd.DataFrame(
            columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
        )

    direction = {
        'n': 1,
        'e': 2,
        's': 3,
        'w': 4,
    }

    tracks = np.array(tracks)
    CURRENT_ARRAY = np.zeros((3, *tracks.shape), dtype=int)
    CURRENT_ARRAY[0] = tracks

    for _, row in CURRENT_DF.iterrows():
        CURRENT_ARRAY[1][row['start_pos']] = direction[row['dir']]
        if row['end_pos'] != (-1, -1):
            CURRENT_ARRAY[2][row['end_pos']] = 5

    USER_PARAMS['rows'] = tracks.shape[0]
    USER_PARAMS['cols'] = tracks.shape[1]
    USER_PARAMS['agents'] = len(trains)

    temp = trains['x']
    trains['x'] = trains['y']
    trains['y'] = temp

    temp = trains['x_end']
    trains['x_end'] = trains['y_end']
    trains['y_end'] = temp

    env = create_custom_env(tracks, trains, USER_PARAMS)
    os.makedirs("../data", exist_ok=True)
    save_png(env, "../data/running_tmp.png")

    CURRENT_IMG = '../data/running_tmp.png'

    if LAST_MENU == 'start':
        switch_start_to_main()
    else:
        reload_main_env_viewer()

def save_env_to_file():
    global CURRENT_ARRAY, CURRENT_DF

    file = filedialog.asksaveasfilename(
        title="Select LP Environment File",
        initialdir='../environments',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    if not file:
        return

    tracks = CURRENT_ARRAY[0]
    x = [t[1] for t in CURRENT_DF['start_pos']]
    y = [t[0] for t in CURRENT_DF['start_pos']]
    x_end = [t[1] for t in CURRENT_DF['end_pos']]
    y_end = [t[0] for t in CURRENT_DF['end_pos']]

    trains = pd.DataFrame({
        'id': CURRENT_DF.index,
        'x': x,
        'y': y,
        'dir': CURRENT_DF['dir'],
        "x_end": x_end,
        "y_end": y_end,
        "e_dep": CURRENT_DF['e_dep'],
        "l_arr": CURRENT_DF['l_arr']
    })

    save_env(tracks, trains, name=file)

def run_simulation():
    global CURRENT_ARRAY, CURRENT_DF, USER_PARAMS, CURRENT_PATHS

    tracks = CURRENT_ARRAY[0]
    x = [t[1] for t in CURRENT_DF['start_pos']]
    y = [t[0] for t in CURRENT_DF['start_pos']]
    x_end = [t[1] for t in CURRENT_DF['end_pos']]
    y_end = [t[0] for t in CURRENT_DF['end_pos']]

    trains = pd.DataFrame({
        'id': CURRENT_DF.index,
        'x': x,
        'y': y,
        'dir': CURRENT_DF['dir'],
        "x_end": x_end,
        "y_end": y_end,
        "e_dep": CURRENT_DF['e_dep'],
        "l_arr": CURRENT_DF['l_arr']
    })

    save_env(tracks, trains)

    CURRENT_PATHS = position_df(
        tracks,
        trains,
        USER_PARAMS['clingo'],
        USER_PARAMS['lpFiles'] + ['../data/running_tmp.lp'],
        USER_PARAMS['answer']
    )

    delete_tmp_lp()

def exit_gui(event):
    global WINDOWS

    save_user_data_to_file()
    delete_tmp_png()

    WINDOWS['flatland_window'].close_window()


# stubs

def stub():
    return



# TODOS

# TODO: loading symbols with Labels using toggle_visibility
#  make loading labels  XXX_status_label next to the generate or build or run
#  simulation buttons
#  and use the status label to show errors like not being able to generate an
#  environment or not getting the paths from the run sim button

# TODO: show time table and gif functions in Results
# TODO: add help buttons in random gen, builder and result menus
