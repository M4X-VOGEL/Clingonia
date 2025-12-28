"""Provides several functions for the Clingonia graphical user interface.

Provides functions to open and transition between vies and menus in Clingonia,
as well as data management functions, such as file imports and environment
generation.

Example usage:
    import views

    views.build_flatland_window()
    views.create_start_menu()
    views.start_flatland()
"""

import os
import re
import ast
import json
import shutil
from tkinter import filedialog, font

import pandas as pd

from code.build_png import create_custom_env, save_png
from code.build_gif import render_gif
from code.custom_canvas import *
from code.files import save_env, delete_tmp_lp, delete_tmp_png, delete_tmp_gif, delete_tmp_frames
from code.gen_png import gen_env, render_time_prediction
from code.load_env import load_env
from code.positions import position_df



# Platform: 
sys_platform = platform.system()


# screen dimensions
screenwidth, screenheight = 1920, 1080


# font styling
base_font_size = 20
info_text_font_size = 18 if sys_platform == 'Darwin' else 14
frame_title_font_size = 50
font_base_mod = 1
font_path_mod = 0.5
font_err_mod = 0.75

# font layouts -- get set in update_fonts()
base_font_layout = None
canvas_font_layout = None
canvas_label_font_layout = None
save_font_layout = None
path_font_layout = None
err_font_layout = None
help_font_layout = None
info_font_layout = None
title_font_layout = None


# color scheme
dark_background_color = '#111214'
background_color = '#1E1F22'
canvas_color = '#313338'
button_color = '#2B2D31'
blue_button_color = '#5865F2'
red_button_color = '#9B0000'
label_color = '#FFFFFF'
entry_color = '#383A40'
input_color = '#F0F0F0'
example_color = '#AFB3BA'
selector_color = '#35373C'
good_status_color = '#209752'
bad_status_color = '#F23F43'
switch_on_color = '#2ECC71'
switch_off_color = '#E03A3E'
train_color = '#0FF000'
station_color = '#000FF0'
golden_color = '#F0B232'
grid_color = '#AFB3BA'


# Button Style Maps
base_button_style_map = {
    'foreground': [('active', '#F1F1F1')],
    'background': [('active', '#27292D')]
}
yellow_text_button_style_map = {
    'foreground': [('active', '#E2A323')],
    'background': [('active', '#27292D')]
}
blue_button_style_map = {
    'foreground': [('active', '#F1F1F1')],
    'background': [('active', '#4752C4')]
}
red_button_style_map = {
    'foreground': [('active', '#F1F1F1')],
    'background': [('active', '#690000')]
}
green_button_style_map = {
    'foreground': [('active', '#F1F1F1')],
    'background': [('active', '#206552')]
}
tool_button_style_map = {
    'foreground': [('active', '#000000')],
    'background': [('active', '#2B2D31')]
}
selector_button_style_map = {
    'foreground': [('active', '#000000')],
    'background': [('active', '#111214')]
}
reset_button_style_map = {
    'foreground': [('active', '#111214')],
    'background': [('active', '#E03A3E')]
}


# state trackers
first_mod_try = True
first_build_try = True
build_mode = None
last_menu = None
current_act_err_log = None
show_act_err_logs = False
last_gif_params = (None, None)
last_solve_params = (None, None, None, [])
env_counter = 0


# Widget handlers
windows, frames, buttons, labels = {}, {}, {}, {}
canvases, entry_fields, pictures, texts = {}, {}, {}, {}
scroll_bars = {}


# Parameter Dictionaries
default_params = {
    'rows': 40,
    'cols': 40,
    'agents': 4,
    'cities': 4,
    'seed': 1,
    'globalTimeLimit': 100,
    'grid': False,
    'intercity': 2,
    'incity': 2,
    'remove': True,
    'speedMap': {1.0 : 1.0},
    'malfunction': (0, 30),
    'min': 2,
    'max': 6,
    'lowQuality': False,
    'saveImage': False,
    'answer': 1,
    'clingo': 'clingo',
    'lpFiles': [],
    'lowQualityGIF': False,
    'frameRate': 2.0,
}
user_params = {
    'rows': None,
    'cols': None,
    'agents': None,
    'cities': None,
    'seed': None,
    'globalTimeLimit': None,
    'grid': None,
    'intercity': None,
    'incity': None,
    'remove': None,
    'speedMap': None,
    'malfunction': None,
    'min': None,
    'max': None,
    'lowQuality': False,
    'saveImage': False,
    'answer': None,
    'clingo': None,
    'lpFiles': [],
    'lowQualityGIF': False,
    'frameRate': None,
}
user_params_backup = user_params.copy()

# Parameter Dictionaries for Error handling
err_dict = {
    'rows': {
        ValueError: 'needs int > 0',
        'tooFewRows': 'needs at least 10 rows',
        'notEnoughRows': 'needs int > 0',
    },
    'cols': {
        ValueError: 'needs int > 0',
        'tooFewCols': 'needs at least 10 cols',
        'notEnoughCols': 'needs int > 0',
    },
    'agents': {
        ValueError: 'needs int > 0',
        'tooFewAgents': 'needs at least 1 agent'
    },
    'cities': {
        ValueError: 'needs int > 0',
        'tooFewCities': 'needs at least 2 cities'
    },
    'seed': {
        ValueError: 'needs int >= 0',
        'tooBigSeed': 'seed is too big',
        'negativeValue': 'needs Seed >= 0',
    },
    'globalTimeLimit': {
        ValueError: 'needs int > 0',
        'notEnoughTime': 'needs at least Time >= 1',
    },
    'grid': {ValueError: 'needs true or false'},
    'intercity': {
        ValueError: 'needs int > 0',
        'tooFewRails': 'needs at least 1 rail between cities'
    },
    'incity': {
        ValueError: 'needs int > 0',
        'tooFewRails': 'needs at least 1 rail pair in the cities'
    },
    'remove': {ValueError: 'needs true or false'},
    'speedMap': {
        ValueError: 'needs dictionary: float: float,... , 0 <= float <= 1',
        SyntaxError: 'needs dictionary: float: float,... , 0 <= float <= 1',
        'negativeValue': 'needs dictionary float: float,... , 0 <= float <= 1',
        'tooBigSpeed': 'needs dictionary float: float,... , 0 <= float <= 1',
        'notFloat': 'needs dictionary float: float,... , 0 <= float <= 1',
    },
    'malfunction': {
        ValueError: 'needs fraction: int / int, 0 <= fraction <= 1',
        IndexError: 'needs fraction: int / int, 0 <= fraction <= 1',
        'divByZero': 'divisor cannot be 0',
        'negativeValue': 'needs fraction: int / int, 0 <= fraction <= 1',
        'tooBigMalfunction': 'needs fraction: int / int, 0 <= fraction <= 1',
    },
    'min': {
        ValueError: 'needs int > 0',
        'negativeValue': 'needs int > 0',
    },
    'max': {
        ValueError: 'needs int > 0',
        'negativeValue': 'needs int > 0',
    },
    'answer': {
        ValueError: 'needs int >= 0',
        'negativeValue': 'needs int >= 0',
        'tooBigAnswer': 'answer is too big',
    },
    'clingo': {
        'noPathToClingo': 'The given path does not lead to clingo',
    },
    'lpFiles': {},
    'frameRate': {
        ValueError: 'needs 0 < num <= 60',
        'negativeFrameRate': 'needs 0 < num <= 60',
        'tooBigFrameRate': 'needs 0 < num <= 60',
    }
}
loading_err_dict = {
    -1: 'No environment .lp file found.',
    -2: 'A cell predicate is improperly specified.',
    -3: 'A train predicate is improperly specified.',
    -4: 'A start predicate is improperly specified.',
    -5: 'An end predicate is improperly specified.',
    -6: 'A start direction is invalid.',
    -7: 'A train has no start or end predicate.',
    -8: 'A train starts or ends on an invalid cell.',
    -9: 'A train\'s latest arr. is earlier than its earliest dep.',
    -10: 'Incomplete grid: Missing cell predicates.',
    -11: 'A train\'s ID is negative.',
    -12: 'Negative coordinates are invalid.',
    -13: 'An end predicate has an invalid latest arrival.',
    -14: 'No dead ends allowed in the environment.',
    -15: 'Invalid file type. Environment must be a .lp file',
    -16: 'A speed predicate is improperly specified.'
}
clingo_err_dict = {
    -1: 'No .lp files given.',
    -2: 'Clingo returned an error.',
    -3: 'Clingo returns UNSATISFIABLE.',
    -4: 'Clingo did not provide the requested answer: ',
    -5: 'Invalid actions. Ensure to use #show action/3.',
    -6: 'Invalid action format. Ensure action(train(ID), Action, Timestep).'
}


# Environment Arrays
current_array = np.zeros((3, 40, 40), dtype=int)
current_builder_backup_array = current_array.copy()
current_modify_backup_array = current_array.copy()

# Positions DataFrame
pos_df = pd.DataFrame(
    columns=["trainID", "x", "y", "dir", "timestep"]
)

# Trains Dataframe
current_df = pd.DataFrame(
    columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr', 'speed']
)
current_builder_backup_df = current_df.copy()
current_modify_backup_df = current_df.copy()

# Environment image and GIF
current_img = None
current_gif = None
current_timestep = None

# Train Paths Dataframe
current_paths = pd.DataFrame()




# start menu

def build_flatland_window():
    """Loads user data from file and opens the program window.

    Modifies:
        screenwidth (int):
            sets the global screenwidth of the screen where the
            program is opened on.
        screenheight (int):
            sets the global screenheight of the screen where the
            program is opened on.
        Adjusts all global font layouts to the current window size.
    """
    global screenwidth, screenheight

    load_user_data_from_file()

    windows['flatland_window'] = Window(
        width=None,
        height=None,
        fullscreen=True,
        background_color=background_color,
        title='Clingonia'
    )
    windows['flatland_window'].window.bind('<Escape>', open_exit_confirmation_frame)

    screenwidth = windows['flatland_window'].screenwidth
    screenheight = windows['flatland_window'].screenheight

    update_fonts()

    windows['flatland_window'].window.rowconfigure(0, weight=1)
    windows['flatland_window'].window.columnconfigure((0, 1), weight=1)

def update_fonts():
    """Updates all font layouts to the current window size

    Modifies:
        All global font_layouts and font_base_mod.
    """
    global font_base_mod, base_font_layout, canvas_font_layout, \
        canvas_label_font_layout, save_font_layout, path_font_layout,\
        err_font_layout, help_font_layout, \
        info_font_layout, title_font_layout

    font_base_mod = ((screenwidth / 1920) ** 0.6) * ((screenheight / 1080) ** 0.4)
    base_font_layout = font.Font(family='Arial', size=int(font_base_mod * base_font_size), weight='bold')
    canvas_font_layout = font.Font(family='Arial', size=int(font_base_mod * base_font_size))
    canvas_label_font_layout = font.Font(family='Arial', size=int(font_base_mod * base_font_size), weight='bold')
    save_font_layout = font.Font(family='Arial', size=int(font_base_mod * base_font_size), slant='italic')
    path_font_layout = font.Font(family='Arial', size=int(font_base_mod * base_font_size * font_path_mod), weight='bold')
    err_font_layout = font.Font(family='Arial', size=int(font_base_mod * font_err_mod * base_font_size), weight='bold')
    help_font_layout = font.Font(family='Courier', size=int(font_base_mod * base_font_size))
    info_font_layout = font.Font(family='Courier', size=int(font_base_mod * info_text_font_size))
    title_font_layout = font.Font(family='Arial', size=int(font_base_mod * frame_title_font_size), weight='bold')

def start_flatland():
    """Starts the main event loop of the program"""
    print('Info: Launch was successful.')
    windows['flatland_window'].run()

def create_start_menu():
    """Wrapper function to create the start menu.

    Modifies:
        last_menu(str):
            global tracker for the last opened menu.
    """
    global last_menu

    last_menu = 'start'

    build_title_frame()
    build_start_menu_frame()

def build_title_frame():
    """Builds the title frame."""
    frames['title_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsew',
        background_color=canvas_color,
        border_width=0,
        visibility=True
    )

    if sys_platform == 'Windows':
        title_frame_label('Lucida Handwriting', 80)
        title_frame_subtitle_label('Lucida Handwriting', 30)
    elif sys_platform == 'Darwin':  # macOS
        title_frame_label('Big Caslon', 100)
        title_frame_subtitle_label('Big Caslon', 40)
    else:  # Linux and other
        title_frame_label('Arial', 80)
        title_frame_subtitle_label('Arial', 30)

    pictures['title_gif'] = GIF(
        root=frames['title_frame'].frame,
        width=frames['title_frame'].width,
        height=frames['title_frame'].height * 0.35,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='n',
        gif='data/png/title_gif.gif',
        background_color=canvas_color,
        visibility=True,
    )

    frames['title_frame'].frame.rowconfigure((0, 1), weight=1)
    frames['title_frame'].frame.columnconfigure(0, weight=1)
    frames['title_frame'].frame.grid_propagate(False)

def title_frame_label(font, scale_fac):
    """Adds the Title to the title frame.

    Args:
        font (str):
            font family of the title label.
        scale_fac (int):
            scales the font size.
    """
    # Necessary for macOS
    labels['title_label'] = Label(
        root=frames['title_frame'].frame,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsew',
        text='CLINGONIA',
        font=(font, int(font_base_mod * scale_fac), 'bold'),
        foreground_color=label_color,
        background_color=canvas_color,
        visibility=True,
    )

def title_frame_subtitle_label(font, scale_fac):
    """Adds the subtitle to the title frame.

    Args:
        font (str):
            font family of the subtitle label.
        scale_fac (int):
            scales the font size.
    """
    # Necessary for macOS
    labels['sub_title_label'] = Label(
        root=frames['title_frame'].frame,
        grid_pos=(2, 0),
        padding=(0, (0,40)),
        sticky='sew',
        text='Powered by MadMotion',
        font=(font, int(font_base_mod * scale_fac), 'bold'),
        foreground_color=example_color,
        background_color=canvas_color,
        visibility=True,
    )

def build_start_menu_frame():
    """Builds the start menu."""
    frames['start_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['start_help_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='n',
        command=toggle_start_menu_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['start_toggle_fullscreen_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 1),
        padding=(5, 5),
        sticky='nw',
        command=windows['flatland_window'].toggle_fullscreen,
        image='data/png/fullscreen.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['exit_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=160,
        height=120,
        grid_pos=(0, 2),
        padding=(0, 0),
        sticky='ne',
        command=open_exit_confirmation_frame,
        image='data/png/quit.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['random_gen_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(1,1),
        padding=(0,0),
        sticky='new',
        command=switch_start_to_random_gen,
        text='Generate Random Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['build_env_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='new',
        command=switch_start_to_builder,
        text='Build New Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['load_env_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='new',
        command=load_env_from_file,
        text='Load Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    labels['start_load_status_label'] = Label(
        root=frames['start_menu_frame'].frame,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='n',
        text='',
        font=err_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    frames['start_menu_frame'].frame.rowconfigure(tuple(range(4)), weight=2)
    frames['start_menu_frame'].frame.rowconfigure(5, weight=1)
    frames['start_menu_frame'].frame.columnconfigure(tuple(range(3)), weight=1)
    frames['start_menu_frame'].frame.grid_propagate(False)

def build_start_menu_help_frame():
    """Builds the start menu help frame."""
    frames['start_menu_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/start_menu_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['start_menu_help_frame'] = Text(
        root=frames['start_menu_help_frame'].frame,
        width=frames['start_menu_help_frame'].width,
        height=frames['start_menu_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['start_menu_help_frame'].frame.rowconfigure(0, weight=1)
    frames['start_menu_help_frame'].frame.columnconfigure(0, weight=1)
    frames['start_menu_help_frame'].frame.grid_propagate(False)

def toggle_start_menu_help():
    """Opens or hides the start menu help frame."""
    if 'start_menu_help_frame' in frames:
        frames['start_menu_help_frame'].toggle_visibility()
        frames['start_menu_help_frame'].frame.rowconfigure(0, weight=1)
        frames['start_menu_help_frame'].frame.columnconfigure(0, weight=1)
        frames['start_menu_help_frame'].frame.grid_propagate(False)
    else:
        build_start_menu_help_frame()

def switch_start_to_random_gen():
    """Destroys all start menu frames and opens the random gen parameter view.

    Saves a backup of the current user parameters.

    Modifies:
        user_params_backup (dict):
            holds a backup of the user parameters.
    """
    global user_params_backup

    user_params_backup = user_params.copy()

    if 'title_frame' in frames:
        frames['title_frame'].destroy_frame()
        del frames['title_frame']
    if 'start_menu_frame' in frames:
        frames['start_menu_frame'].destroy_frame()
        del frames['start_menu_frame']
    if 'start_menu_help_frame' in frames:
        frames['start_menu_help_frame'].destroy_frame()
        del frames['start_menu_help_frame']
    if 'start_menu_env_viewer_frame' in frames:
        frames['start_menu_env_viewer_frame'].destroy_frame()
        del frames['start_menu_env_viewer_frame']

    build_random_gen_para_frame()

def switch_start_to_builder():
    """Destroys all start menu frames and opens the builder parameter view.

    Modifies:
        build_mode (str):
            global tracker of the current build menu state.
    """
    global build_mode

    build_mode = 'build'

    if 'title_frame' in frames:
        frames['title_frame'].destroy_frame()
        del frames['title_frame']
    if 'start_menu_frame' in frames:
        frames['start_menu_frame'].destroy_frame()
        del frames['start_menu_frame']
    if 'start_menu_help_frame' in frames:
        frames['start_menu_help_frame'].destroy_frame()
        del frames['start_menu_help_frame']
    if 'start_menu_env_viewer_frame' in frames:
        frames['start_menu_env_viewer_frame'].destroy_frame()
        del frames['start_menu_env_viewer_frame']

    build_builder_para_frame()

def switch_start_to_main():
    """Destroys all start menu frames and opens the main menu.

    Opens the main menu and the load info frame.
    """
    if 'title_frame' in frames:
        frames['title_frame'].destroy_frame()
        del frames['title_frame']
    if 'start_menu_frame' in frames:
        frames['start_menu_frame'].destroy_frame()
        del frames['start_menu_frame']
    if 'start_menu_help_frame' in frames:
        frames['start_menu_help_frame'].destroy_frame()
        del frames['start_menu_help_frame']
    if 'start_menu_env_viewer_frame' in frames:
        frames['start_menu_env_viewer_frame'].destroy_frame()
        del frames['start_menu_env_viewer_frame']

    create_main_menu()
    build_main_menu_load_info_frame()





# main menu

def create_main_menu():
    """Wrapper function to create the main menu.

    Modifies:
        last_menu(str):
            global tracker for the last opened menu.
    """
    global last_menu

    last_menu = 'main'

    build_main_menu()
    build_main_menu_env_viewer()

def build_main_menu():
    """Builds the main menu."""
    frames['main_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='nw',
        command=toggle_main_menu_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['main_toggle_fullscreen_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 1),
        padding=(5, 5),
        sticky='nw',
        command=windows['flatland_window'].toggle_fullscreen,
        image='data/png/fullscreen.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['exit_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=160,
        height=120,
        grid_pos=(0, 2),
        padding=(0, 0),
        sticky='ne',
        command=open_exit_confirmation_frame,
        image='data/png/quit.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['random_gen_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='new',
        command=switch_main_to_random_gen,
        text='Generate Random Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['build_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='new',
        command=switch_main_to_builder,
        text='Build New Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['modify_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='new',
        command=switch_main_to_modify,
        text='Modify Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['save_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='new',
        command=save_env_to_file,
        text='Save Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['save_button_frame'] = Frame(
        root=frames['main_menu_frame'].frame,
        width=10,
        height=10,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='ne',
        background_color=button_color,
        border_width=0,
        visibility=True
    )

    labels['saveImage_label'] = Label(
        root=frames['save_button_frame'].frame,
        grid_pos=(0, 0),
        padding=((0, 10), (5, 0)),
        sticky='n',
        text='Image',
        font=save_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        visibility=True,
    )
    buttons['saveImage_button'] = ToggleSwitch(
        root=frames['save_button_frame'].frame,
        width=frames['save_button_frame'].width * 5,
        height=frames['save_button_frame'].height * 2,
        on_color=switch_on_color,
        off_color=switch_off_color,
        handle_color=input_color,
        background_color=button_color,
        command=change_save_image_status,
    )
    buttons['saveImage_button'].grid(
        row=1, column=0, padx=(0, 10), pady=(5, 0), sticky="s"
    )
    buttons['saveImage_button'].set_state(user_params['saveImage'])

    buttons['load_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='new',
        command=load_env_from_file,
        text='Load Environment',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    labels['main_load_status_label'] = Label(
        root=frames['main_menu_frame'].frame,
        grid_pos=(6, 1),
        padding=(0, 0),
        sticky='n',
        text='',
        font=err_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['run_sim_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(8, 1),
        padding=(0, 0),
        sticky='new',
        command=switch_main_to_clingo_para,
        text='Next: Clingo Solver',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=blue_button_color,
        border_width=0,
        visibility=True,
        style_map=blue_button_style_map,
    )

    frames['main_menu_frame'].frame.rowconfigure(tuple(range(9)), weight=1)
    frames['main_menu_frame'].frame.columnconfigure(0, weight=5)
    frames['main_menu_frame'].frame.columnconfigure(1, weight=1)
    frames['main_menu_frame'].frame.columnconfigure(2, weight=5)
    frames['main_menu_frame'].frame.grid_propagate(False)

def build_main_menu_load_info_frame():
    """Builds the load info frame."""
    get_load_info()

    frames['main_menu_load_info_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    with open("data/info_text.txt", "r") as file:
        displaytext = file.read()

    texts['main_menu_load_info'] = Text(
        root=frames['main_menu_load_info_frame'].frame,
        width=frames['main_menu_load_info_frame'].width,
        height=frames['main_menu_load_info_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        columnspan=2,
        text=displaytext,
        font=info_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    buttons['ok_info_button'] = Button(
        root=frames['main_menu_load_info_frame'].frame,
        width=30,
        height=2,
        grid_pos=(1, 0),
        padding=(30, (0,50)),
        sticky='sw',
        command=close_load_info,
        text='Confirm',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=blue_button_color,
        border_width=0,
        visibility=True,
        style_map=blue_button_style_map,
    )

    frames['main_menu_load_info_frame'].frame.rowconfigure(0, weight=2)
    frames['main_menu_load_info_frame'].frame.rowconfigure(1, weight=1)
    frames['main_menu_load_info_frame'].frame.columnconfigure((0,1), weight=1)
    frames['main_menu_load_info_frame'].frame.grid_propagate(False)

def close_load_info():
    """Destroys the load info frame."""
    if 'main_menu_load_info_frame' in frames:
        frames['main_menu_load_info_frame'].destroy_frame()
        del frames['main_menu_load_info_frame']

def build_main_menu_help_frame():
    """Builds the main menu help frame."""
    frames['main_menu_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/main_menu_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['main_menu_help'] = Text(
        root=frames['main_menu_help_frame'].frame,
        width=frames['main_menu_help_frame'].width,
        height=frames['main_menu_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['main_menu_help_frame'].frame.rowconfigure(0, weight=1)
    frames['main_menu_help_frame'].frame.columnconfigure(0, weight=1)
    frames['main_menu_help_frame'].frame.grid_propagate(False)

def build_main_menu_env_viewer():
    """Builds the main menu environment viewer frame."""
    frames['main_menu_env_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    canvases['main_menu_env_viewer_canvas'] = EnvCanvas(
        root=frames['main_menu_env_viewer_frame'].frame,
        width=frames['main_menu_env_viewer_frame'].width,
        height=frames['main_menu_env_viewer_frame'].height,
        x=frames['main_menu_env_viewer_frame'].width * 0,
        y=frames['main_menu_env_viewer_frame'].height * 0,
        font=canvas_font_layout,
        background_color=canvas_color,
        grid_color=grid_color,
        border_width=0,
        image=current_img,
        rows=user_params['rows'],
        cols=user_params['cols'],
    )

def build_clingo_para_frame():
    """Builds the clingo parameter modification frame."""
    frames['clingo_para_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 4),
        padding=(5, 5),
        sticky='n',
        command=toggle_clingo_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['back_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=120,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='nw',
        command=switch_clingo_para_to_main,
        image='data/png/back.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    labels['clingo_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text='Clingo Path:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['clingo_entry'] = EntryField(
        root=frames['clingo_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["clingo"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['clingo_error_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        columnspan=2,
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['answer_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text='Answer to display:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['answer_entry'] = EntryField(
        root=frames['clingo_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["answer"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['answer_error_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        columnspan=2,
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    buttons['select_lp_files_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=30,
        height=1,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        columnspan=2,
        command=load_lp_files,
        text='Select Problem-Solving LP Files',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    labels['clingo_paths_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='w',
        columnspan=2,
        text='',
        font=path_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['run_sim_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=30,
        height=2,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='sw',
        columnspan=2,
        command=switch_clingo_para_to_result,
        text='Run Simulation',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=red_button_color,
        border_width=0,
        visibility=True,
        style_map=red_button_style_map,
    )

    labels['clingo_status_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(8, 2),
        padding=(0, 0),
        text='',
        font=err_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    frames['clingo_para_frame'].frame.rowconfigure(0, weight=1)
    frames['clingo_para_frame'].frame.columnconfigure(0, weight=1)
    frames['clingo_para_frame'].frame.columnconfigure(1, weight=1)
    frames['clingo_para_frame'].frame.rowconfigure(
        tuple(range(1,9)), weight=2
    )
    frames['clingo_para_frame'].frame.columnconfigure(
        tuple(range(2,4)), weight=2
    )
    frames['clingo_para_frame'].frame.grid_propagate(False)

    load_clingo_params()
    windows['flatland_window'].window.update_idletasks()

def build_clingo_help_frame():
    """Builds the clingo parameter help frame."""
    frames['clingo_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/clingo_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['clingo_help'] = Text(
        root=frames['clingo_help_frame'].frame,
        width=frames['clingo_help_frame'].width,
        height=frames['clingo_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['clingo_help_frame'].frame.rowconfigure(0, weight=1)
    frames['clingo_help_frame'].frame.columnconfigure(0, weight=1)
    frames['clingo_help_frame'].frame.grid_propagate(False)

def toggle_main_menu_help():
    """Opens or hides the main menu help frame."""
    if 'main_menu_help_frame' in frames:
        frames['main_menu_help_frame'].toggle_visibility()
        frames['main_menu_help_frame'].frame.rowconfigure(0, weight=1)
        frames['main_menu_help_frame'].frame.columnconfigure(0, weight=1)
        frames['main_menu_help_frame'].frame.grid_propagate(False)
    else:
        build_main_menu_help_frame()

def toggle_clingo_help():
    """Opens or hides the clingo parameter help frame."""
    if 'clingo_help_frame' in frames:
        frames['clingo_help_frame'].toggle_visibility()
        frames['clingo_help_frame'].frame.rowconfigure(0, weight=1)
        frames['clingo_help_frame'].frame.columnconfigure(0, weight=1)
        frames['clingo_help_frame'].frame.grid_propagate(False)
    else:
        build_clingo_help_frame()

def switch_main_to_random_gen():
    """Destroys all main menu frames and opens the random gen parameter view.

    Saves a backup of the current user parameters.

    Modifies:
        user_params_backup (dict):
            holds a backup of the user parameters.
    """
    global user_params_backup

    user_params_backup = user_params.copy()

    if 'main_menu_frame' in frames:
        frames['main_menu_frame'].destroy_frame()
        del frames['main_menu_frame']
    if 'main_menu_help_frame' in frames:
        frames['main_menu_help_frame'].destroy_frame()
        del frames['main_menu_help_frame']
    if 'main_menu_env_viewer_frame' in frames:
        frames['main_menu_env_viewer_frame'].destroy_frame()
        del frames['main_menu_env_viewer_frame']

    build_random_gen_para_frame()

def switch_main_to_builder():
    """Destroys all main menu frames and opens the builder parameter view.

    Saves a backup of the current user parameters and environment data.

    Modifies:
        user_params_backup (dict):
            holds a backup of the user parameters.
        current_builder_backup_array (np.array):
            holds a backup of the current environment map.
        current_builder_backup_df (pd.Dataframe):
            holds a backup of the current environment train list.
        build_mode (str):
            global tracker of the current build menu state.
    """
    global build_mode, user_params_backup, \
        current_modify_backup_array, current_modify_backup_df

    user_params_backup = user_params.copy()
    current_modify_backup_array = current_array.copy()
    current_modify_backup_df = current_df.copy()

    build_mode = 'build'

    if 'main_menu_frame' in frames:
        frames['main_menu_frame'].destroy_frame()
        del frames['main_menu_frame']
    if 'main_menu_help_frame' in frames:
        frames['main_menu_help_frame'].destroy_frame()
        del frames['main_menu_help_frame']
    if 'main_menu_env_viewer_frame' in frames:
        frames['main_menu_env_viewer_frame'].destroy_frame()
        del frames['main_menu_env_viewer_frame']

    build_builder_para_frame()

def switch_main_to_modify():
    """Destroys all main menu frames and opens the builder parameter view.

    Saves a backup of the current user parameters and environment data.

    Modifies:
        user_params_backup (dict):
            holds a backup of the user parameters.
        current_builder_backup_array (np.array):
            holds a backup of the current environment map.
        current_builder_backup_df (pd.Dataframe):
            holds a backup of the current environment train list.
        build_mode (str):
            global tracker of the current build menu state.
    """
    global build_mode, user_params_backup, \
        current_modify_backup_array, current_modify_backup_df

    user_params_backup = user_params.copy()
    current_modify_backup_array = current_array.copy()
    current_modify_backup_df = current_df.copy()

    build_mode = 'modify'

    if 'main_menu_frame' in frames:
        frames['main_menu_frame'].destroy_frame()
        del frames['main_menu_frame']
    if 'main_menu_help_frame' in frames:
        frames['main_menu_help_frame'].destroy_frame()
        del frames['main_menu_help_frame']
    if 'main_menu_env_viewer_frame' in frames:
        frames['main_menu_env_viewer_frame'].destroy_frame()
        del frames['main_menu_env_viewer_frame']
    if 'main_menu_load_info_frame' in frames:
        frames['main_menu_load_info_frame'].destroy_frame()
        del frames['main_menu_load_info_frame']

    build_builder_para_frame()

def switch_main_to_clingo_para():
    """Destroys all main menu frames and opens the clingo parameter frame."""

    if 'main_menu_frame' in frames:
        frames['main_menu_frame'].destroy_frame()
        del frames['main_menu_frame']
    if 'main_menu_help_frame' in frames:
        frames['main_menu_help_frame'].destroy_frame()
        del frames['main_menu_help_frame']

    build_clingo_para_frame()

def switch_clingo_para_to_main():
    """Destroys all clingo parameter frames and opens the main menu frame."""
    if save_clingo_params('main') == -1:
        return

    if 'clingo_para_frame' in frames:
        frames['clingo_para_frame'].destroy_frame()
        del frames['clingo_para_frame']
    if 'clingo_help_frame' in frames:
        frames['clingo_help_frame'].destroy_frame()
        del frames['clingo_help_frame']
    if 'main_menu_env_viewer_frame' in frames:
        frames['main_menu_env_viewer_frame'].destroy_frame()
        del frames['main_menu_env_viewer_frame']

    create_main_menu()

def switch_clingo_para_to_result():
    """Switch from clingo parameter frames to result view.

    Saves the clingo parameters.

    If there were changes made to the environment or the parameters changed
    since the last solve process the solver get called.

    Destroys all clingo parameter frames.
    Produces the timetable information from the solve results
    Opens the result view.

    Modifies:
        last_solve_params (dict):
            holds the last parameters used to solve an environment.
        show_act_err_logs (bool):
            holds a tracker for showing error logs in the result view.

    Returns:
        None (None):
            an error is shown on the clingo parameter view if the solver fails.
    """
    global last_solve_params, show_act_err_logs

    if save_clingo_params('result') == -1:
        return

    labels['clingo_status_label'].label.config(
        text='...Simulating...',
        fg=good_status_color,
    )
    frames['clingo_para_frame'].frame.update()

    if len(current_df) == 0:
        labels['clingo_status_label'].label.config(
            text='No trains on environment',
            fg=bad_status_color,
        )
        frames['clingo_para_frame'].frame.update()
        return

    current_solve_params = (
        env_counter, user_params['clingo'], user_params['answer'], user_params['lpFiles']
    )

    if last_solve_params != current_solve_params or isinstance(current_paths, int):
        if user_params['answer'] == 0:
            # Reset Simulation
            user_params['answer'] = 1
            current_solve_params = (
                env_counter, user_params['clingo'], user_params['answer'], user_params['lpFiles']
            )
            print(f'\n🌱 Simulation Reset successful: Going for Answer 1.')
        show_act_err_logs = False
        last_solve_params = current_solve_params
        sim_result = run_simulation()

        if sim_result:
            if sim_result == -4:
                answer_err = (clingo_err_dict[sim_result] +
                                               f'{user_params["answer"]}')
                labels['clingo_status_label'].label.config(
                    text=answer_err,
                    fg=bad_status_color,
                )
            else:
                labels['clingo_status_label'].label.config(
                    text=clingo_err_dict[sim_result],
                    fg=bad_status_color,
                )
            frames['clingo_para_frame'].frame.update()
            return
    else:
        print('\n🔄 Simulation skipped: No changes in parameters (answer, files, env).\n - If you changed the encoding in your selected files, choose Answer 0 to force a run.')

    if 'clingo_para_frame' in frames:
        frames['clingo_para_frame'].destroy_frame()
        del frames['clingo_para_frame']
    if 'clingo_help_frame' in frames:
        frames['clingo_help_frame'].destroy_frame()
        del frames['clingo_help_frame']
    if 'main_menu_env_viewer_frame' in frames:
        frames['main_menu_env_viewer_frame'].destroy_frame()
        del frames['main_menu_env_viewer_frame']

    df_to_timetable_text()
    create_result_menu()

def reload_main_env_viewer():
    """Destroys the old main menu builder and rebuilds it."""
    if 'main_menu_env_viewer_frame' in frames:
        frames['main_menu_env_viewer_frame'].destroy_frame()
        del frames['main_menu_env_viewer_frame']

    build_main_menu_env_viewer()

def load_lp_files():
    """Open a file dialog window and request a lp files to be selected.

    Displays selected file paths on the clingo parameter frame.
    """
    files = filedialog.askopenfilenames(
        title="Select LP Files",
        initialdir='asp',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    if not files:
        return

    user_params['lpFiles'] = list(files)
    displaytext = "\n".join(files)

    labels['clingo_paths_label'].label.config(
        text=displaytext, wraplength=500, justify='left',
    )
    if labels['clingo_status_label'].label.cget('text') == 'No .lp files given.':
        labels['clingo_status_label'].label.config(text='')

def save_clingo_params(next_menu) -> int:
    """Saves the clingo parameters from the clingo parameter view.

    Args:
        next_menu (str): The next menu to be opened.

    Returns:
        int: -1 if there was an error with any input 0 otherwise.
    """
    err_count = 0

    for field in entry_fields:
        # get the key from every entry field in the global list
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key not in ['answer', 'clingo']:
            continue

        # get the data from the entry field
        data = entry_fields[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = default_params[key]
            elif data == '':
                data = default_params[key]
            elif key == 'clingo':
                if data.endswith('clingo.exe'):
                    data = data[:-4]
                else:
                    data = data
            else:
                data = int(data)

            # hide label if there was no problem with the data conversion
            labels[f'{key}_error_label'].hide_label()
        except Exception as e:
            # register the error and display corresponding error message
            err_count += 1
            err = type(e)
            if err in err_dict[key]:
                labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
                labels[f'{key}_error_label'].place_label()
            else:
                print(e)
                print(err)
                print(data)
            continue

        # check for additional constrains and display error when violated
        if key == 'clingo' and not (data.endswith('clingo') or data.lower() == 'api'):
            err_count += 1
            err = 'noPathToClingo'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
            data = default_params[key]
        elif key == 'answer' and data < 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
            data = default_params[key]
        elif key == 'answer' and data >= 2**31:
            err_count += 1
            err = 'tooBigAnswer'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
            data = default_params[key]

        # only save non string values as parameters except for the clingo path
        if type(data) is not str or key == 'clingo':
            user_params[key] = data

    if err_count and next_menu == 'result':
        return -1
    else:
        return 0

def load_clingo_params():
    """Load the current user parameters onto the clingo para frame"""
    for field in entry_fields:
        # get the key from every entry field in the global list
        key = field.split('_')[0]

        if key not in default_params:
            continue
        elif key not in ['answer', 'clingo']:
            continue
        elif user_params[key] is None:
            continue
        else:
            entry_fields[field].insert_string(str(user_params[key]))

    if user_params['lpFiles'] is not None:
        displaytext = "\n".join(user_params["lpFiles"])
        labels['clingo_paths_label'].label.config(
            text=displaytext, wraplength=500, justify='left',
        )





# exit confirmation

def open_exit_confirmation_frame(event=None):
    """Build confirmation frame for exiting the program.

    Args:
        event (tk.Event):
            event generated by the window when escape is pressed.
    """
    if 'exit_confirmation_frame' in frames:
        return

    frames['exit_confirmation_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        columnspan=2,
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    labels['exit_label'] = Label(
        root=frames['exit_confirmation_frame'].frame,
        grid_pos=(0, 0),
        padding=(0, 80),
        columnspan=2,
        sticky='s',
        text='EXIT CLINGONIA?',
        font=title_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['yes_exit_button'] = Button(
        root=frames['exit_confirmation_frame'].frame,
        width=15,
        height=3,
        grid_pos=(1, 0),
        padding=(50, 0),
        sticky='ne',
        command=exit_gui,
        text='YES',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['no_exit_button'] = Button(
        root=frames['exit_confirmation_frame'].frame,
        width=15,
        height=3,
        grid_pos=(1, 1),
        padding=(50, 0),
        sticky='nw',
        command=close_exit_confirmation_frame,
        text='NO',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['exit_confirmation_frame'].frame.rowconfigure(0, weight=2)
    frames['exit_confirmation_frame'].frame.rowconfigure(1, weight=3)
    frames['exit_confirmation_frame'].frame.columnconfigure((0, 1), weight=1)
    frames['exit_confirmation_frame'].frame.grid_propagate(False)

def exit_gui():
    """Wrapper function to exit the program."""
    save_user_data_to_file()
    delete_tmp_lp()
    delete_tmp_png()
    delete_tmp_gif()
    delete_tmp_frames()

    windows['flatland_window'].close_window()

def close_exit_confirmation_frame():
    """Destroys the confirmation frame."""
    if 'exit_confirmation_frame' in frames:
        frames['exit_confirmation_frame'].destroy_frame()
        del frames['exit_confirmation_frame']





# random generation

def random_gen_change_to_start_or_main():
    """Wrapper function to change to start or main menu.

    Loads the backup user parameters into the user parameters.
    Resets first build try.

    Opens start or main menu depending on last_menu.

    Modifies:
        user_params (dict):
            holds the current user parameters.
        first_build_try (bool):
            global tracker for first environment generation and build try.
    """
    global user_params, first_build_try

    user_params = user_params_backup.copy()

    first_build_try = True

    if last_menu == 'start':
        random_gen_para_to_start()
    else:
        random_gen_para_to_main()

def random_gen_para_to_start():
    """Destroys random gen parameter frames and opens start menu."""
    if 'random_gen_para_frame' in frames:
        frames['random_gen_para_frame'].destroy_frame()
        del frames['random_gen_para_frame']
    if 'random_gen_para_help_frame' in frames:
        frames['random_gen_para_help_frame'].destroy_frame()
        del frames['random_gen_para_help_frame']

    create_start_menu()

def random_gen_para_to_main():
    """Destroys random gen parameter frames and opens main menu."""
    if 'random_gen_para_frame' in frames:
        frames['random_gen_para_frame'].destroy_frame()
        del frames['random_gen_para_frame']
    if 'random_gen_para_help_frame' in frames:
        frames['random_gen_para_help_frame'].destroy_frame()
        del frames['random_gen_para_help_frame']

    create_main_menu()

def build_random_gen_para_frame():
    """Builds random generation parameter frame."""
    frames['random_gen_para_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.7),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 3),
        padding=(5, 5),
        sticky='ne',
        command=toggle_random_gen_para_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['back_button'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=120,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='nw',
        command=random_gen_change_to_start_or_main,
        image='data/png/back.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    labels['spacing_err_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(0, 4),
        padding=(0, 0),
        sticky='nw',
        text='needs dictionary float: float,... , 0 <= float <= 1',
        font=base_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    labels['rows_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment rows:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['rows_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["rows"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['rows_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(1, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['cols_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment columns:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['cols_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(2, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["cols"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['cols_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(2, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['agents_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text='Number of agents:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['agents_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["agents"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['agents_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(3, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['cities_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of cities:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['cities_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(4, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["cities"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['cities_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(4, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['seed_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text='Seed:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['seed_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["seed"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['seed_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(5, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['globalTimeLimit_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text='Global Time Limit:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['globalTimeLimit_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(6, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["globalTimeLimit"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['globalTimeLimit_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(6, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['grid_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text='Use grid mode:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    buttons['grid_button'] = ToggleSwitch(
        root=frames['random_gen_para_frame'].frame,
        width=70, height=30,
        on_color=switch_on_color, off_color=switch_off_color,
        handle_color=input_color, background_color=background_color,
        command=change_grid_status,
    )
    buttons['grid_button'].set_state(user_params['grid'])

    labels['grid_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(7, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['intercity_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of rails between cities:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['intercity_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(8, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["intercity"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['intercity_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(8, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['incity_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(9, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of rail pairs in cities:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['incity_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(9, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["incity"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['incity_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(9, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['remove_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(10, 2),
        padding=(0, 0),
        sticky='nw',
        text='Remove agents on arrival:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    buttons['remove_button'] = ToggleSwitch(
        root=frames['random_gen_para_frame'].frame,
        width=70, height=30,
        on_color=switch_on_color, off_color=switch_off_color,
        handle_color=input_color, background_color=background_color,
        command=change_remove_status,
    )
    buttons['remove_button'].set_state(user_params['remove'])

    labels['remove_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(10, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['speedMap_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(11, 2),
        padding=(0, 0),
        sticky='nw',
        text='Speed ratio map for trains:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['speedMap_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(11, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {str(default_params["speedMap"]).strip("{}")}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['speedMap_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(11, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['malfunction_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(12, 2),
        padding=(0, 0),
        sticky='nw',
        text='Malfunction rate:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['malfunction_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(12, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["malfunction"][0]}/'
             f'{default_params["malfunction"][1]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['malfunction_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(12, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['min_duration_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(13, 2),
        padding=(0, 0),
        sticky='nw',
        text='Min. duration for malfunctions:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['min_duration_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(13, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["min"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['min_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(13, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['max_duration_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(14, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. duration for malfunctions:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['max_duration_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(14, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["max"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['max_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(14, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['lowQuality_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(15, 2),
        padding=(0, 0),
        sticky='nw',
        text='Low quality mode:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    buttons['lowQuality_button'] = ToggleSwitch(
        root=frames['random_gen_para_frame'].frame,
        width=70, height=30,
        on_color=switch_on_color, off_color=switch_off_color,
        handle_color=input_color, background_color=background_color,
        command=change_low_quality_status,
    )
    buttons['lowQuality_button'].set_state(user_params['lowQuality'])

    buttons['advanced_options'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(16, 2),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_toggle_advanced_para_options,
        text='Advanced Options',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['generate_button'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=9,
        height=1,
        grid_pos=(16, 3),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_para_to_env,
        text='Generate',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=red_button_color,
        border_width=0,
        visibility=True,
        style_map=red_button_style_map,
    )

    labels['random_gen_status_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(16, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    frames['random_gen_para_frame'].frame.rowconfigure(0, weight=1)
    frames['random_gen_para_frame'].frame.rowconfigure(
        tuple(range(1,17)), weight=2
    )
    frames['random_gen_para_frame'].frame.columnconfigure(0, weight=1)
    frames['random_gen_para_frame'].frame.columnconfigure(1, weight=1)
    frames['random_gen_para_frame'].frame.columnconfigure(2, weight=2)
    frames['random_gen_para_frame'].frame.columnconfigure(3, weight=0)
    frames['random_gen_para_frame'].frame.columnconfigure(4, weight=2)

    frames['random_gen_para_frame'].frame.grid_propagate(False)

    load_random_gen_env_params()
    windows['flatland_window'].window.update_idletasks()

def build_random_gen_para_help_frame():
    """Builds random generation parameter help frame."""
    frames['random_gen_para_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.3),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/random_gen_para_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['random_gen_para_help'] = Text(
        root=frames['random_gen_para_help_frame'].frame,
        width=frames['random_gen_para_help_frame'].width,
        height=frames['random_gen_para_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['random_gen_para_help_frame'].frame.rowconfigure(0, weight=1)
    frames['random_gen_para_help_frame'].frame.columnconfigure(0, weight=1)
    frames['random_gen_para_help_frame'].frame.grid_propagate(False)

def random_gen_para_to_env():
    """Generates random environment.

    Saves current user parameters entered in the random generation parameter
    frame.

    Generates a random environment with the current user parameters.
    Saves data of the environment in the corresponding data structures.
    Displays an error message on the random generation parameter frame if there
    was an error during generation.

    Modifies:
        first_build_try (bool):
            global tracker for first environment generation and build try.
        current_img (str):
            path to the image of the current environment.
        current_df (pd.DataFrame):
            holds a train list of the current environment.
        current_array (np.array):
            holds a layered map representation of the current environment.
        env_counter:
            tracks changes to the current environment.
        user_params_backup (dict):
            backup for the user parameters.
    """
    global first_build_try, current_img, current_df, current_array, env_counter, \
        user_params_backup

    if save_random_gen_env_params() == -1:
        return

    if first_build_try:
        first_build_try = False
        if user_params['rows'] * user_params['cols'] > 1000000:
            labels['random_gen_status_label'].label.config(
                text=f'Warning: Extremely high RAM usage\n'
                     f'for this environment size!\n\n'
                     f'⚠️Click again to proceed at your own risk⚠️',
                fg=golden_color,
            )
            labels['random_gen_status_label'].place_label()
            return
    else:
        first_build_try = True

    labels['random_gen_status_label'].label.config(
        text='...Generating...',
        fg=good_status_color,
    )
    frames['random_gen_para_frame'].frame.update()

    try:
        tracks, trains = gen_env(user_params)
        delete_tmp_frames()
        env_counter += 1
    except ValueError as e:
        labels['random_gen_status_label'].label.config(
            text='Cannot fit more than one city in this map.\n' + \
                 'Hint: min. dimensions are 18×10 or 10×18.\n' + \
                 'Tip: reduce Max. num. of rail pairs in cities.',
            fg=bad_status_color,
        )
        frames['random_gen_para_frame'].frame.update()
        print(f'❌ FLATLAND is unable to generate environment with current parameters.\n')
        return

    if tracks == -1:
        labels['random_gen_status_label'].label.config(
            text='No environment generated.\n'
                 'Please restart the program.',
            fg=bad_status_color,
            anchor="w",
            justify="left",
        )
        frames['random_gen_para_frame'].frame.update()
        return
    elif tracks == -2:
        labels['random_gen_status_label'].label.config(
            text='No environment generated.\n'
                 'Try different parameters;\n'
                 'Perhaps larger dimensions\n'
                 'or another seed.',
            fg=bad_status_color,
            anchor="w",
            justify="left",
        )
        frames['random_gen_para_frame'].frame.update()
        return

    # TODO: remove once gen_env outputs trains with speed.
    trains["speed"] = 1

    if len(trains):
        start_pos = list(zip(trains['x'], trains['y']))
        end_pos = list(zip(trains['x_end'], trains['y_end']))

        current_df = pd.DataFrame({
            'start_pos': start_pos,
            'dir': trains['dir'],
            'end_pos': end_pos,
            'e_dep': trains['e_dep'],
            'l_arr': trains['l_arr'],
            'speed': trains['speed'],
        })
    else:
        current_df = pd.DataFrame(
            columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr', 'speed']
        )

    direction = {
        'n': 1,
        'e': 2,
        's': 3,
        'w': 4,
    }

    tracks = np.array(tracks)
    current_array = np.zeros((3, *tracks.shape), dtype=int)
    current_array[0] = tracks

    for _, row in current_df.iterrows():
        current_array[1][row['start_pos']] = direction[row['dir']]
        if row['end_pos'] != (-1, -1):
            current_array[2][row['end_pos']] = 5

    current_img = 'data/running_tmp.png'

    if 'random_gen_para_frame' in frames:
        frames['random_gen_para_frame'].destroy_frame()
        del frames['random_gen_para_frame']
    if 'random_gen_para_help_frame' in frames:
        frames['random_gen_para_help_frame'].destroy_frame()
        del frames['random_gen_para_help_frame']

    user_params_backup = user_params.copy()
    build_random_gen_env_viewer()
    build_random_gen_env_menu()

def build_random_gen_env_viewer():
    """Builds random generation environment viewer frame."""
    frames['random_gen_env_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    canvases['gen_env_viewer_canvas'] = EnvCanvas(
        root=frames['random_gen_env_viewer_frame'].frame,
        width=frames['random_gen_env_viewer_frame'].width,
        height=frames['random_gen_env_viewer_frame'].height,
        x=frames['random_gen_env_viewer_frame'].width * 0,
        y=frames['random_gen_env_viewer_frame'].height * 0,
        font=canvas_font_layout,
        background_color=canvas_color,
        grid_color=grid_color,
        border_width=0,
        image=current_img,
        rows=user_params['rows'],
        cols=user_params['cols'],
    )

def build_random_gen_env_menu():
    """Builds Random generation environment menu frame."""
    frames['random_gen_env_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['return_to_menu_button'] = Button(
        root=frames['random_gen_env_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='n',
        command=switch_random_gen_to_main,
        text='Confirm',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=blue_button_color,
        border_width=0,
        visibility=True,
        style_map=blue_button_style_map,
    )

    current_df_to_env_text(mode='gen')
    with open("data/info_text.txt", "r") as file:
        displaytext = file.read()

    texts['random_gen_env_trains'] = Text(
        root=frames['random_gen_env_menu_frame'].frame,
        width=frames['random_gen_env_menu_frame'].width,
        height=frames['random_gen_env_menu_frame'].height * 0.75,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=displaytext,
        font=info_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['random_gen_env_menu_frame'].frame.rowconfigure(0, weight=15)
    frames['random_gen_env_menu_frame'].frame.rowconfigure(1, weight=1)
    frames['random_gen_env_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['random_gen_env_menu_frame'].frame.grid_propagate(False)

def random_gen_toggle_advanced_para_options():
    """Toggles the visibility of labels and entries in random gen para frame."""
    labels['grid_label'].toggle_visibility()
    if buttons['grid_button'].winfo_ismapped():
        buttons['grid_button'].grid_forget()
    else:
        buttons['grid_button'].grid(row=7, column=3, sticky='n')
    labels['intercity_label'].toggle_visibility()
    entry_fields['intercity_entry'].toggle_visibility()
    labels['incity_label'].toggle_visibility()
    entry_fields['incity_entry'].toggle_visibility()
    labels['remove_label'].toggle_visibility()
    if buttons['remove_button'].winfo_ismapped():
        buttons['remove_button'].grid_forget()
    else:
        buttons['remove_button'].grid(row=10, column=3, sticky='n')
    labels['speedMap_label'].toggle_visibility()
    entry_fields['speedMap_entry'].toggle_visibility()
    labels['malfunction_label'].toggle_visibility()
    entry_fields['malfunction_entry'].toggle_visibility()
    labels['min_duration_label'].toggle_visibility()
    entry_fields['min_duration_entry'].toggle_visibility()
    labels['max_duration_label'].toggle_visibility()
    entry_fields['max_duration_entry'].toggle_visibility()
    labels['lowQuality_label'].toggle_visibility()
    if buttons['lowQuality_button'].winfo_ismapped():
        buttons['lowQuality_button'].grid_forget()
    else:
        buttons['lowQuality_button'].grid(row=15, column=3, sticky='n')
    return

def toggle_random_gen_para_help():
    """Open or hides the random generation parameter frame."""
    if 'random_gen_para_help_frame' in frames:
        frames['random_gen_para_help_frame'].toggle_visibility()
        frames['random_gen_para_help_frame'].frame.rowconfigure(0, weight=1)
        frames['random_gen_para_help_frame'].frame.columnconfigure(0, weight=1)
        frames['random_gen_para_help_frame'].frame.grid_propagate(False)
    else:
        build_random_gen_para_help_frame()

def switch_random_gen_to_main():
    """Destroys all random gen viewer menu frames and opens the main menu."""
    if 'random_gen_env_viewer_frame' in frames:
        frames['random_gen_env_viewer_frame'].destroy_frame()
        del frames['random_gen_env_viewer_frame']
    if 'random_gen_env_menu_frame' in frames:
        frames['random_gen_env_menu_frame'].destroy_frame()
        del frames['random_gen_env_menu_frame']

    create_main_menu()

def save_random_gen_env_params():
    """Saves the parameters from the random generation parameter frame.

    Returns:
        int: -1 if there was an error with any input 0 otherwise.
    """
    err_count = 0

    for field in entry_fields:
        # get the key from every entry field in the global list
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key not in ['rows','cols','agents','cities','seed','globalTimeLimit',
                         'intercity','incity','speedMap','malfunction','min','max']:
            continue

        # get the data from the entry field
        data = entry_fields[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                raise ValueError
            elif data == '':
                raise ValueError
            elif key == 'speedMap':
                if ":" not in data:
                    raise ValueError
                data = '{' + data + '}'
                data = ast.literal_eval(data)
            elif key == 'malfunction':
                if data.count("/") > 1:
                    raise ValueError
                data = (int(data.split('/')[0]),int(data.split('/')[1]))
            else:
                data = int(data)

            # hide label if there was no problem with the data conversion
            labels[f'{key}_error_label'].hide_label()
        except Exception as e:
            # register the error and display corresponding error message
            err = type(e)
            err_count += 1
            if err in err_dict[key]:
                labels[f'{key}_error_label'].label.config(
                    text=err_dict[key][err])
                labels[f'{key}_error_label'].place_label()
            else:
                print(e)
                print(err)
                print(data)
            continue

        # check for additional constrains and display error when violated
        if key=='rows' and data < 10:
            err_count += 1
            err = 'tooFewRows'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='cols' and data < 10:
            err_count += 1
            err = 'tooFewCols'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='agents' and data < 1:
            err_count += 1
            err = 'tooFewAgents'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='cities' and data < 2:
            err_count += 1
            err = 'tooFewCities'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='seed' and data >= 2**32:
            err_count += 1
            err = 'tooBigSeed'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='seed' and data < 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key == 'globalTimeLimit' and data < 1:
            err_count += 1
            err = 'notEnoughTime'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='intercity' and data < 1:
            err_count += 1
            err = 'tooFewRails'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='incity' and data < 1:
            err_count += 1
            err = 'tooFewRails'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='malfunction' and data[1] == 0:
            err_count += 1
            err = 'divByZero'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='malfunction' and data[0]/data[1] < 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='malfunction' and data[0]/data[1] > 1:
            err_count += 1
            err = 'tooBigMalfunction'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='min' and data <= 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='max' and data <= 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()

        if key=='speedMap':
            for k, v in data.items():
                if not isinstance(k, float) or not isinstance(v, float):
                    err_count += 1
                    err = 'notFloat'
                    labels[f'{key}_error_label'].label.config(
                        text=err_dict[key][err])
                    labels[f'{key}_error_label'].place_label()
                if k < 0 or v < 0:
                    err_count += 1
                    err = 'negativeValue'
                    labels[f'{key}_error_label'].label.config(
                        text=err_dict[key][err])
                    labels[f'{key}_error_label'].place_label()
                if k > 1 or v > 1:
                    err_count += 1
                    err = 'tooBigSpeed'
                    labels[f'{key}_error_label'].label.config(
                        text=err_dict[key][err])
                    labels[f'{key}_error_label'].place_label()

        # only save non string values as parameters except for the clingo path
        if type(data) is not str:
            user_params[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_random_gen_env_params():
    """Load the current user parameters onto the random gen para frame"""
    for field in entry_fields:
        # get the key from every entry field in the global list
        key = field.split('_')[0]

        if key not in default_params:
            continue
        elif key not in ['rows','cols','agents','cities','seed','globalTimeLimit',
                         'intercity','incity','speedMap','malfunction','min','max']:
            continue
        elif user_params[key] is None:
            continue
        elif key == 'speedMap':
            string = ''
            for k, v in user_params['speedMap'].items():
                string = string + f'{k}: {v}, '
            entry_fields[field].insert_string(string[:-2])
        elif key == 'malfunction':
            entry_fields[field].insert_string(
                f'{user_params["malfunction"][0]}/'
                f'{user_params["malfunction"][1]}'
            )
        else:
            entry_fields[field].insert_string(str(user_params[key]))





# builder

def builder_change_to_start_or_main():
    """Wrapper function to change to start or main menu.

    Loads the backup user parameters into the user parameters.
    Also loads the backup current array and df into the current_array and
    current_df.
    Resets first build try and first mod try.
    Resets the build_mode variable.

    Opens start or main menu depending on last_menu.

    Modifies:
        user_params (dict):
            hold the current user parameters.
        first_build_try (bool):
            global tracker for first environment generation and build try.
        first_mod_try (bool):
            global tracker for first modification try.
        build_mode (str):
            global tracker for the current mode in the builder view.
        current_array (np.array):
            holds a map representation of the current environment.
        current_df (pd.DataFrame):
            holds a train list of the current environment.
    """
    global first_mod_try, first_build_try, build_mode, user_params, \
        current_array, current_df

    user_params = user_params_backup.copy()

    if build_mode == 'change_params':
        build_mode = 'build'

    first_mod_try = True
    first_build_try = True

    # only overwrite if exiting para from modify - to not overwrite with default empty array when coming from build
    #if build_mode == 'modify':
    current_array = current_modify_backup_array.copy()
    current_df = current_modify_backup_df.copy()

    if last_menu == 'start':
        builder_para_to_start()
    else:
        builder_para_to_main()

def open_builder_discard_changes_frame():
    """Builds discard build mode changes frame."""
    frames['builder_discard_changes_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        columnspan=2,
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    labels['discard_changes_label'] = Label(
        root=frames['builder_discard_changes_frame'].frame,
        grid_pos=(0, 0),
        padding=(0, 80),
        columnspan=2,
        sticky='s',
        text='DISCARD CHANGES?',
        font=title_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['yes_discard_changes_button'] = Button(
        root=frames['builder_discard_changes_frame'].frame,
        width=15,
        height=3,
        grid_pos=(1, 0),
        padding=(50, 0),
        sticky='ne',
        command=builder_change_to_start_or_main,
        text='YES',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['no_discard_changes_button'] = Button(
        root=frames['builder_discard_changes_frame'].frame,
        width=15,
        height=3,
        grid_pos=(1, 1),
        padding=(50, 0),
        sticky='nw',
        command=frames['builder_discard_changes_frame'].destroy_frame,
        text='NO',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['builder_discard_changes_frame'].frame.rowconfigure(0, weight=2)
    frames['builder_discard_changes_frame'].frame.rowconfigure(1, weight=3)
    frames['builder_discard_changes_frame'].frame.columnconfigure((0, 1), weight=1)
    frames['builder_discard_changes_frame'].frame.grid_propagate(False)

def builder_para_to_start():
    """Destroys builder parameter frames and opens start menu.

    Modifies:
        build_mode (bool):
            global tracker for the current mode in the builder view.
    """
    global build_mode

    build_mode = None

    if 'builder_para_frame' in frames:
        frames['builder_para_frame'].destroy_frame()
        del frames['builder_para_frame']
    if 'builder_para_help_frame' in frames:
        frames['builder_para_help_frame'].destroy_frame()
        del frames['builder_para_help_frame']
    if 'builder_discard_changes_frame' in frames:
        frames['builder_discard_changes_frame'].destroy_frame()
        del frames['builder_discard_changes_frame']

    create_start_menu()

def builder_para_to_main():
    """Destroys builder parameter frames and opens main menu.

        Modifies:
            build_mode (bool):
                global tracker for the current mode in the builder view.
        """
    global build_mode

    build_mode = None

    if 'builder_para_frame' in frames:
        frames['builder_para_frame'].destroy_frame()
        del frames['builder_para_frame']
    if 'builder_para_help_frame' in frames:
        frames['builder_para_help_frame'].destroy_frame()
        del frames['builder_para_help_frame']
    if 'builder_discard_changes_frame' in frames:
        frames['builder_discard_changes_frame'].destroy_frame()
        del frames['builder_discard_changes_frame']

    create_main_menu()

def build_builder_para_frame():
    """Builds builder parameter frame."""
    frames['builder_para_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.7),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['builder_para_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 3),
        padding=(5, 5),
        sticky='ne',
        command=toggle_builder_para_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['back_button'] = Button(
        root=frames['builder_para_frame'].frame,
        width=120,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='nw',
        command=open_builder_discard_changes_frame,
        image='data/png/back.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    labels['spacing_err_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(0, 4),
        padding=(0, 0),
        sticky='nw',
        text='needs dictionary float: float,... , 0 <= float <= 1',
        font=base_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    labels['rows_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment rows:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['rows_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["rows"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['rows_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(1, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['cols_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment columns:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['cols_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(2, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["cols"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['cols_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(2, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )


    labels['globalTimeLimit_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text='Global Time Limit:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['globalTimeLimit_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["globalTimeLimit"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['globalTimeLimit_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(3, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['remove_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        text='Remove agents on arrival:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    buttons['remove_button'] = ToggleSwitch(
        root=frames['builder_para_frame'].frame,
        width=70, height=30,
        on_color=switch_on_color, off_color=switch_off_color,
        handle_color=input_color, background_color=background_color,
        command=change_remove_status,
    )
    buttons['remove_button'].set_state(user_params['remove'])

    labels['remove_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(4, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['malfunction_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text='Malfunction rate:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['malfunction_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["malfunction"][0]}/'
             f'{default_params["malfunction"][1]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['malfunction_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(5, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['min_duration_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text='Min. duration for malfunctions:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['min_duration_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(6, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["min"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['min_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(6, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['max_duration_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. duration for malfunctions:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    entry_fields['max_duration_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(7, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["max"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=False,
    )

    labels['max_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(7, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['lowQuality_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        text='Low quality mode:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=False,
    )

    buttons['lowQuality_button'] = ToggleSwitch(
        root=frames['builder_para_frame'].frame,
        width=70, height=30,
        on_color=switch_on_color, off_color=switch_off_color,
        handle_color=input_color, background_color=background_color,
        command=change_low_quality_status,
    )
    buttons['lowQuality_button'].set_state(user_params['lowQuality'])

    buttons['advanced_options'] = Button(
        root=frames['builder_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(9, 2),
        padding=(0, 0),
        sticky='nw',
        command=builder_toggle_advanced_para_options,
        text='Advanced Options',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['build_button'] = Button(
        root=frames['builder_para_frame'].frame,
        width=9,
        height=1,
        grid_pos=(9, 3),
        padding=(0, 0),
        sticky='nw',
        command=builder_para_to_track_grid,
        text='Build' if build_mode == 'build' else 'Modify',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=blue_button_color,
        border_width=0,
        visibility=True,
        style_map=blue_button_style_map,
    )

    labels['build_para_status_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(9, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    frames['builder_para_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_para_frame'].frame.rowconfigure(
        tuple(range(1,10)), weight=2
    )
    frames['builder_para_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_para_frame'].frame.columnconfigure(1, weight=1)
    frames['builder_para_frame'].frame.columnconfigure(2, weight=2)
    frames['builder_para_frame'].frame.columnconfigure(3, weight=2)
    frames['builder_para_frame'].frame.columnconfigure(4, weight=2)
    frames['builder_para_frame'].frame.grid_propagate(False)

    load_builder_env_params()

    windows['flatland_window'].window.update_idletasks()

def build_builder_para_help_frame():
    """Builds builder parameter help frame."""
    frames['builder_para_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.3),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/builder_para_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['builder_para_help_text'] = Text(
        root=frames['builder_para_help_frame'].frame,
        width=frames['builder_para_help_frame'].width,
        height=frames['builder_para_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_para_help_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_para_help_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_para_help_frame'].frame.grid_propagate(False)

def toggle_builder_para_help():
    """Opens or hides the builder parameter help frame."""
    if 'builder_para_help_frame' in frames:
        frames['builder_para_help_frame'].toggle_visibility()
        frames['builder_para_help_frame'].frame.rowconfigure(0, weight=1)
        frames['builder_para_help_frame'].frame.columnconfigure(0, weight=1)
        frames['builder_para_help_frame'].frame.grid_propagate(False)
    else:
        build_builder_para_help_frame()

def builder_para_to_track_grid():
    """Switches from builder parameter frame to the track builder view.

    If the mode is 'modify' this will check if the current environment has to
    many tiles in the array and will issue a warning.
    Also checks if the new array created in the build mode is very large.

    Saves teh current user params from the builder parameter frame.

    Destroys the builder parameter frame.
    Creates or, in modify mode, resizes the current environment to the new
    parameter rows and columns.
    Creates a backup of the current_array and current_df.
    Opens the track builder menu view.

    Modifies:
        first_build_try (bool):
            global tracker for first environment generation and build try.
        first_mod_try (bool):
            global tracker for first modification try.
        build_mode (str):
            global tracker for the current mode in the builder view.
        current_img (str):
            path to the image of the current environment.
        current_df (pd.DataFrame):
            holds a train list of the current environment.
        current_array (np.array):
            holds a layered map representation of the current environment.
        current_builder_backup_df (pd.DataFrame):
            holds a backup train list of the current environment for the build
            mode.
        current_modify_backup_df (pd.DataFrame):
            holds a backup train list of the current environment for the modify
            mode.
        current_builder_backup_array (np.array):
            holds a backup layered map representation of the current environment
            for the build mode.
        current_modify_backup_array (np.array):
            holds a backup layered map representation of the current environment
            for the modify mode.
        env_counter:
            tracks changes to the current environment.
        user_params_backup (dict):
            backup for the user parameters.
    """
    global first_mod_try, first_build_try, build_mode, current_array, current_df, \
        current_builder_backup_array, current_builder_backup_df, \
        current_modify_backup_array, current_modify_backup_df

    if build_mode == 'modify' and sys_platform == 'Windows':

        # get the count of objects in the current environment
        # counts tracks, trains and stations.
        # trains and station on the same cell only get counted once
        pic_count = np.count_nonzero(current_array)

        if pic_count > 4800:
            # return with an error to the parameter view
            labels['build_para_status_label'].label.config(
                text=f'Windows cannot render\n'
                     f'this many elements ({pic_count})\n '
                     f'on the canvas.\n',
                fg=bad_status_color,
            )
            labels['build_para_status_label'].place_label()
            return
        elif pic_count > 4500:
            if first_mod_try:
                # on the first try return with a warning to the parameter view
                first_mod_try = False
                labels['build_para_status_label'].label.config(
                    text=f'Warning: High element count ({pic_count})\n'
                         f'Memory issues may disrupt execution\n\n'
                         f'⚠️Click again to proceed at your own risk⚠️',
                    fg=golden_color,
                )
                labels['build_para_status_label'].place_label()
                return
            else:
                # reset the first try on the second try and continue
                first_mod_try = True

    if save_builder_env_params() == -1:
        return

    if first_build_try:
        # on the first try return with a warning to the parameter view
        first_build_try = False
        if user_params['rows'] * user_params['cols'] > 1000000:
            labels['build_para_status_label'].label.config(
                text=f'Warning: Extremely high RAM usage\n'
                     f'for this environment size!\n\n'
                     f'⚠️Click again to proceed at your own risk⚠️',
                fg=golden_color,
            )
            labels['build_para_status_label'].place_label()
            return
    else:
        # reset the first try on the second try and continue
        first_build_try = True


    if 'builder_para_frame' in frames:
        frames['builder_para_frame'].destroy_frame()
        del frames['builder_para_frame']
    if 'builder_para_help_frame' in frames:
        frames['builder_para_help_frame'].destroy_frame()
        del frames['builder_para_help_frame']

    if user_params['rows'] is not None:
        rows = user_params['rows']
    else:
        rows = default_params['rows']

    if user_params['cols'] is not None:
        cols = user_params['cols']
    else:
        cols = default_params['cols']

    if build_mode == 'build':
        # create a new empty environment and train list
        current_array = np.zeros((3, rows, cols), dtype=int)
        current_df = pd.DataFrame(
            columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr', 'speed']
        )
    else:
        # get the shape of the current array
        current_rows, current_cols = current_array.shape[1:3]

        current_df.reset_index(drop=True, inplace=True)

        if (rows,cols) != (current_rows,current_cols):
            # if the desired size is different from the current one: resize
            if current_rows < rows:
                # add array rows
                current_array = np.pad(
                    current_array,
                    pad_width=[(0, 0), (0, rows-current_rows), (0, 0)],
                    mode='constant',
                    constant_values=0
                )
            elif current_rows > rows:
                # remove array rows
                current_array = current_array[:, :rows, :]

            if current_cols < cols:
                # add array cols
                current_array = np.pad(
                    current_array,
                    pad_width=[(0, 0), (0, 0), (0, cols-current_cols)],
                    mode='constant',
                    constant_values=0
                )
            elif current_cols > cols:
                # remove array cols
                current_array = current_array[:, :, :cols]

            if len(current_df) > 0:
                # remove trains not on the grid anymore
                current_df.drop(
                    index=current_df[current_df['start_pos'].apply(
                        lambda t: t[0] > rows-1 or t[1] > cols-1
                    )].index,
                    inplace=True
                )
                current_df.reset_index(drop=True, inplace=True)

                # reset station not on the grid anymore
                for index, row in current_df.iterrows():
                    if (row['end_pos'][0] > rows - 1 or
                            row['end_pos'][1] > cols - 1):
                        current_df.at[index, 'end_pos'] = (-1, -1)

    if build_mode == 'build':
        current_builder_backup_array = current_array.copy()
        current_builder_backup_df = current_df.copy()

    if build_mode == 'change_params':
        build_mode = 'build'

    build_track_builder_menu_frame()
    build_builder_grid_frame()

def builder_track_grid_to_para():
    """Destroy the builder track view and open the parameter view.

    If going back from the build menu in build mode open the parameter view in
    modify mode to allow for retrospective modifications.

    Modifies:
        build_mode (str):
            global tracker for the current mode in the builder view.
    """
    global build_mode

    if 'track_builder_menu_frame' in frames:
        frames['track_builder_menu_frame'].destroy_frame()
        del frames['track_builder_menu_frame']
    if 'builder_grid_frame' in frames:
        frames['builder_grid_frame'].destroy_frame()
        del frames['builder_grid_frame']
    if 'builder_track_help_frame' in frames:
        frames['builder_track_help_frame'].destroy_frame()
        del frames['builder_track_help_frame']

    if build_mode == 'build':
        build_mode = 'change_params'

    build_builder_para_frame()

def build_builder_grid_frame():
    """Build the builder grid canvas frame."""
    frames['builder_grid_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    canvases['builder_grid_canvas'] = BuildCanvas(
        root=frames['builder_grid_frame'].frame,
        width=frames['builder_grid_frame'].width,
        height=frames['builder_grid_frame'].height,
        x=frames['builder_grid_frame'].width * 0,
        y=frames['builder_grid_frame'].height * 0,
        font=canvas_font_layout,
        id_label_font=canvas_label_font_layout,
        background_color=dark_background_color,
        grid_color=grid_color,
        train_color=train_color,
        station_color=station_color,
        border_width=0,
        array=current_array,
        train_data=current_df,
    )

    frames['builder_grid_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_grid_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_grid_frame'].frame.grid_propagate(False)

def build_track_builder_menu_frame():
    """Build the track builder menu frame."""
    frames['track_builder_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 2),
        padding=(5, 5),
        sticky='n',
        command=toggle_builder_track_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['back_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=120,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='nw',
        command= builder_track_grid_to_para,
        image='data/png/back.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['horizontal_straight_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 1),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(1025),
        image='data/png/Gleis_horizontal.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['vertical_straight_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(32800),
        image='data/png/Gleis_vertikal.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['corner_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(3, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(2064),
        image='data/png/Gleis_kurve_oben_links.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['corner_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(3, 1),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(72),
        image='data/png/Gleis_kurve_oben_rechts.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['corner_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(2, 1),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(16386),
        image='data/png/Gleis_kurve_unten_rechts.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['corner_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(2, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(4608),
        image='data/png/Gleis_kurve_unten_links.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_hor_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(3, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(3089),
        image='data/png/Weiche_horizontal_oben_links.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_hor_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(3, 4),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(1097),
        image='data/png/Weiche_horizontal_oben_rechts.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_hor_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(2, 4),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(17411),
        image='data/png/Weiche_horizontal_unten_rechts.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_hor_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(2, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(5633),
        image='data/png/Weiche_horizontal_unten_links.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_ver_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(3, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(34864),
        image='data/png/Weiche_vertikal_oben_links.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_ver_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(3, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(32872),
        image='data/png/Weiche_vertikal_oben_rechts.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_ver_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(2, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(49186),
        image='data/png/Weiche_vertikal_unten_rechts.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['switch_ver_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(2, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(37408),
        image='data/png/Weiche_vertikal_unten_links.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['diamond_crossing_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(4, 1),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(33825),
        image='data/png/Gleis_Diamond_Crossing.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['single_slip_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(4, 6),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(35889),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=270,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['single_slip_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(4, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(33897),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=180,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['single_slip_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(4, 3),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(50211),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=90,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['single_slip_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(4, 4),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(38433),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['double_slip_top_left_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(4, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(52275),
        image='data/png/Weiche_Double_Slip.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=90,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['double_slip_bottom_left_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(4, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(38505),
        image='data/png/Weiche_Double_Slip.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['symmetrical_top_left_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(2136),
        image='data/png/Weiche_Symetrical.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=180,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['symmetrical_top_right_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(16458),
        image='data/png/Weiche_Symetrical.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=90,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['symmetrical_bottom_left_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 4),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(20994),
        image='data/png/Weiche_Symetrical.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['symmetrical_top_left_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(6672),
        image='data/png/Weiche_Symetrical.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=270,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['delete_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(5, 1),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(0),
        image='data/png/eraser.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['reset_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 7),
        padding=(0, 0),
        columnspan=2,
        command=lambda: open_reset_frame(frames['track_builder_menu_frame']),
        text='RESET',
        font=base_font_layout,
        foreground_color=switch_off_color,
        background_color=dark_background_color,
        border_width=0,
        visibility=True,
        style_map=reset_button_style_map,
    )

    buttons['train_builder_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(6, 6),
        padding=(0, 0),
        columnspan=4,
        sticky='w',
        command=builder_track_to_train,
        text='Next: Trains',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=blue_button_color,
        border_width=0,
        visibility=True,
        style_map=blue_button_style_map,
    )

    frames['track_builder_menu_frame'].frame.rowconfigure(0, weight=1)
    frames['track_builder_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['track_builder_menu_frame'].frame.columnconfigure(1, weight=1)
    frames['track_builder_menu_frame'].frame.rowconfigure(
        tuple(range(1,7)), weight=2
    )
    frames['track_builder_menu_frame'].frame.columnconfigure(
        tuple(range(2,9)), weight=2
    )
    frames['track_builder_menu_frame'].frame.grid_propagate(False)

def build_builder_track_help_frame():
    """Builds the track builder menu help frame."""
    frames['builder_track_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/builder_track_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['builder_track_help_text'] = Text(
        root=frames['builder_track_help_frame'].frame,
        width=frames['builder_track_help_frame'].width,
        height=frames['builder_track_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_track_help_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_track_help_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_track_help_frame'].frame.grid_propagate(False)

def toggle_builder_track_help():
    """Opens or hide the track builder menu help frame."""
    if 'builder_track_help_frame' in frames:
        frames['builder_track_help_frame'].toggle_visibility()
        frames['builder_track_help_frame'].frame.rowconfigure(0, weight=1)
        frames['builder_track_help_frame'].frame.columnconfigure(0, weight=1)
        frames['builder_track_help_frame'].frame.grid_propagate(False)
    else:
        build_builder_track_help_frame()

def builder_track_to_train():
    """Destroys the track builder menu frame and open the train builder view

    Resets the current selection for the builder grid.
    """
    if 'track_builder_menu_frame' in frames:
        frames['track_builder_menu_frame'].destroy_frame()
        del frames['track_builder_menu_frame']
    if 'builder_track_help_frame' in frames:
        frames['builder_track_help_frame'].destroy_frame()
        del frames['builder_track_help_frame']

    canvases['builder_grid_canvas'].current_selection = None

    build_train_builder_menu_frame()

def builder_train_to_track():
    """Destroys the train builder menu frame and open the track builder view

    Resets the current selection for the builder grid.
    """
    if 'train_builder_menu_frame' in frames:
        frames['train_builder_menu_frame'].destroy_frame()
        del frames['train_builder_menu_frame']
    if 'builder_train_help_frame' in frames:
        frames['builder_train_help_frame'].destroy_frame()
        del frames['builder_train_help_frame']

    canvases['builder_grid_canvas'].current_selection = None

    build_track_builder_menu_frame()

def build_train_builder_menu_frame():
    """Builds the train builder menu frame."""
    frames['train_builder_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 2),
        padding=(5, 5),
        sticky='n',
        command=toggle_builder_train_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['back_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=120,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='nw' ,
        command= builder_train_to_track,
        image='data/png/back.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['train_north_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(1),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=0,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['train_east_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 3),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(2),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=270,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['train_south_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 4),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(3),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=180,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['train_west_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_base_mod * 80),
        height=int(font_base_mod * 80),
        grid_pos=(1, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(4),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color=selector_color,
        background_color=background_color,
        border_width=0,
        rotation=90,
        visibility=True,
        style_map=selector_button_style_map,
    )

    buttons['reset_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 7),
        padding=(0, 0),
        command=lambda: open_reset_frame(frames['train_builder_menu_frame']),
        text='RESET',
        font=base_font_layout,
        foreground_color=switch_off_color,
        background_color=dark_background_color,
        border_width=0,
        visibility=True,
        style_map=reset_button_style_map,
    )

    frames['train_config_list_canvas_frame'] = Frame(
        root=frames['train_builder_menu_frame'].frame,
        width=frames['train_builder_menu_frame'].width * 0.95,
        height=frames['train_builder_menu_frame'].height * 0.52,
        grid_pos=(2, 0),
        padding=(0, 0),
        columnspan=8,
        background_color=background_color,
        border_width=0,
        visibility=True,
    )

    buttons['configAll_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(3, 2),
        padding=(0, 0),
        columnspan=3,
        command=open_train_all_config_frame,
        text='Config All Trains',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    labels['configAll_status_label'] = Label(
        root=frames['train_builder_menu_frame'].frame,
        grid_pos=(3, 6),
        padding=(0, 0),
        sticky='w',
        columnspan=4,
        text='',
        font=err_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['finish_building_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(4, 2),
        padding=(0, 0),
        columnspan=3,
        command=builder_train_grid_to_env,
        text='Finish Build' if build_mode == 'build' else 'Finish Modifying',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=red_button_color,
        border_width=0,
        visibility=True,
        style_map=red_button_style_map,
    )

    labels['builder_status_label'] = Label(
        root=frames['train_builder_menu_frame'].frame,
        grid_pos=(4, 6),
        padding=(0, 0),
        sticky='w',
        columnspan=4,
        text='',
        font=err_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    frames['train_builder_menu_frame'].frame.rowconfigure(0, weight=1)
    frames['train_builder_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['train_builder_menu_frame'].frame.columnconfigure(1, weight=1)
    frames['train_builder_menu_frame'].frame.rowconfigure(1, weight=2)
    frames['train_builder_menu_frame'].frame.columnconfigure(
        tuple(range(2,8)), weight=2
    )
    frames['train_builder_menu_frame'].frame.rowconfigure((2, 3, 4), weight=2)
    frames['train_builder_menu_frame'].frame.grid_propagate(False)

    canvases['train_config_list'] = TrainListCanvas(
        root=frames['train_config_list_canvas_frame'].frame,
        width=frames['train_config_list_canvas_frame'].width,
        height=frames['train_config_list_canvas_frame'].height,
        x=frames['train_config_list_canvas_frame'].width * 0,
        y=frames['train_config_list_canvas_frame'].height * 0,
        base_font_layout=base_font_layout,
        err_font_layout=err_font_layout,
        title_font_layout=title_font_layout,
        background_color=background_color,
        label_color=label_color,
        button_color=button_color,
        entry_color=entry_color,
        input_color=input_color,
        example_color=example_color,
        bad_status_color=bad_status_color,
        base_button_style_map=base_button_style_map,
        selector_button_style_map=selector_button_style_map,
        remove_button_style_map=reset_button_style_map,
        border_width=0,
        grid=canvases['builder_grid_canvas'],
        train_data=current_df,
        frames=frames,
        windows=windows,
    )
    canvases['builder_grid_canvas'].train_list = canvases['train_config_list']

def open_train_all_config_frame():
    """Builds the all train config menu frame.

    Resets the current selection for the builder grid.

    Returns:
        a warning if no trains are in the environment.
    """
    if len(current_df):
        labels['configAll_status_label'].hide_label()
        canvases['builder_grid_canvas'].current_selection = None
    else:
        # if no trains are in the environment
        labels['configAll_status_label'].label.config(
            text='No Trains Placed',
            fg=bad_status_color,
        )
        labels['configAll_status_label'].place_label()
        return

    frames['train_all_config_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['go_back_button'] = Button(
        root=frames['train_all_config_frame'].frame,
        width=120,
        height=60,
        grid_pos=(0, 0),
        padding=(5, 5),
        sticky='nw' ,
        command=lambda: save_train_all_config(False),
        image='data/png/back.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    labels['all_config_label'] = Label(
        root=frames['train_all_config_frame'].frame,
        grid_pos=(1,0),
        padding=(100,(200,100)),
        columnspan=2,
        sticky='s',
        text=f'Configure All Trains',
        font=title_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    labels['eDep_label'] = Label(
        root=frames['train_all_config_frame'].frame,
        grid_pos=(2,0),
        padding=(100,0),
        sticky='sw',
        text=f'Earliest Departure All Trains:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['eDep_entry'] = EntryField(
        root=frames['train_all_config_frame'].frame,
        width=10,
        height=1,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='s',
        text=f'e.g. 1',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['eDep_error_label'] = Label(
        root=frames['train_all_config_frame'].frame,
        grid_pos=(2,2),
        padding=((0,50),0),
        sticky='s',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=True,
    )

    labels['lArr_label'] = Label(
        root=frames['train_all_config_frame'].frame,
        grid_pos=(3,0),
        padding=(100,20),
        sticky='sw',
        text=f'Latest Arrival All Trains:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['lArr_entry'] = EntryField(
        root=frames['train_all_config_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 1),
        padding=(0, 20),
        sticky='s',
        text=f'e.g. 200',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['lArr_error_label'] = Label(
        root=frames['train_all_config_frame'].frame,
        grid_pos=(3,2),
        padding=((0,50),20),
        sticky='s',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=True,
    )

    labels['speed_label'] = Label(
        root=frames['train_all_config_frame'].frame,
        grid_pos=(4,0),
        padding=(100,(0,20)),
        sticky='sw',
        text=f'Speed All Trains:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['speed_entry'] = EntryField(
        root=frames['train_all_config_frame'].frame,
        width=10,
        height=1,
        grid_pos=(4, 1),
        padding=(0, (0,20)),
        sticky='s',
        text=f'e.g. 1',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )

    labels['speed_error_label'] = Label(
        root=frames['train_all_config_frame'].frame,
        grid_pos=(4,2),
        padding=((0,50),(0,20)),
        sticky='s',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['save_all_config_button'] = Button(
        root=frames['train_all_config_frame'].frame,
        width=20,
        height=1,
        grid_pos=(5, 0),
        padding=(100, 40),
        sticky='sw',
        columnspan=2,
        command=lambda: save_train_all_config(True),
        text='Save',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['train_builder_menu_frame'].frame.rowconfigure((0,1,2,3,4,5), weight=1)
    frames['train_builder_menu_frame'].frame.columnconfigure((0,1,2), weight=1)
    frames['train_builder_menu_frame'].frame.grid_propagate(False)

    windows['flatland_window'].window.update_idletasks()

def save_train_all_config(save):
    """Saves the modified train parameters.

    Checks if the entered parameters are valid.
    If parameters are entered and valid it replaces the e_dep and l_arr
    attributes of all trains in current_df.

    Destroys the all config frame.

    Modifies:
        current_df (pd.DataFrame):
            holds a train list of the current environment.

    Returns:
        int: -1 if an error was registered, otherwise 0.
    """
    global current_df

    if not save:
        # if returning via the back button of the frame
        # just destroy the frame
        if 'eDep_entry' in entry_fields:
            del entry_fields['eDep_entry']
        if 'lArr_entry' in entry_fields:
            del entry_fields['lArr_entry']
        if 'speed_entry' in entry_fields:
            del entry_fields['speed_entry']
        if 'train_all_config_frame' in frames:
            frames['train_all_config_frame'].destroy_frame()
            del frames['train_all_config_frame']
        return 0

    # get the entered parameters
    ed = entry_fields['eDep_entry'].entry_field.get()
    la = entry_fields['lArr_entry'].entry_field.get()
    speed = entry_fields['speed_entry'].entry_field.get()

    err_count = 0

    try:
        if ed.startswith('e.g.') or ed == '' or ed is None:
            ed = None
        else:
            ed = int(ed)
            labels['eDep_error_label'].hide_label()
    except ValueError:
        # register the error and print an error message
        labels['eDep_error_label'].label.config(
            text='needs int > 0',
            fg=bad_status_color,
        )
        labels[f'eDep_error_label'].place_label()
        err_count += 1

    try:
        if la.startswith('e.g.') or la == '' or la is None:
            la = None
        else:
            la = int(la)
            labels['lArr_error_label'].hide_label()
    except ValueError:
        # register the error and print an error message
        labels['lArr_error_label'].label.config(
            text='needs int > 0',
            fg=bad_status_color,
        )
        labels[f'lArr_error_label'].place_label()
        err_count += 1

    try:
        if speed.startswith('e.g.') or speed == '' or speed is None:
            speed = None
        else:
            speed = int(speed)
            labels['speed_error_label'].hide_label()
    except ValueError:
        # register the error and print an error message
        labels['speed_error_label'].label.config(
            text='needs int > 0',
            fg=bad_status_color,
        )
        labels[f'speed_error_label'].place_label()
        err_count += 1

    if err_count:
        return -1

    # check for valid parameter values
    if ed is not None:
        if ed < 1:
            labels['eDep_error_label'].label.config(
                text='needs int > 0',
                fg=bad_status_color,
            )
            labels['eDep_error_label'].place_label()
            err_count += 1
        else:
            current_df['e_dep'] = [ed] * len(current_df['e_dep'])

    if la is not None:
        if la < 1:
            labels['lArr_error_label'].label.config(
                text='needs int > 0',
                fg=bad_status_color,
            )
            labels['lArr_error_label'].place_label()
            err_count += 1
        else:
            current_df['l_arr'] = [la] * len(current_df['l_arr'])

    if speed is not None:
        if speed < 1:
            labels['speed_error_label'].label.config(
                text='needs int > 0',
                fg=bad_status_color,
            )
            labels['speed_error_label'].place_label()
            err_count += 1
        else:
            current_df['speed'] = [speed] * len(current_df['speed'])

    if err_count:
        return -1

    if 'eDep_entry' in entry_fields:
        del entry_fields['eDep_entry']
    if 'lArr_entry' in entry_fields:
        del entry_fields['lArr_entry']
    if 'speed_entry' in entry_fields:
        del entry_fields['speed_entry']
    if 'train_all_config_frame' in frames:
        frames['train_all_config_frame'].destroy_frame()
        del frames['train_all_config_frame']

def build_builder_train_help_frame():
    """Builds the train builder menu help frame."""
    frames['builder_train_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/builder_train_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['builder_train_help_text'] = Text(
        root=frames['builder_train_help_frame'].frame,
        width=frames['builder_train_help_frame'].width,
        height=frames['builder_train_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_train_help_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_train_help_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_train_help_frame'].frame.grid_propagate(False)

def toggle_builder_train_help():
    """Opens or hides the train builder menu help frame."""
    if 'builder_train_help_frame' in frames:
        frames['builder_train_help_frame'].toggle_visibility()
        frames['builder_train_help_frame'].frame.rowconfigure(0, weight=1)
        frames['builder_train_help_frame'].frame.columnconfigure(0, weight=1)
        frames['builder_train_help_frame'].frame.grid_propagate(False)
    else:
        build_builder_train_help_frame()

def builder_train_grid_to_env():
    """Switches from builder train menu frame to the builder environment viewer.

    Checks if all trains have valid entries and returns with a warning
    otherwise.

    Generates an image of the created or modified environment.

    Creates a backup of the current_array and current_df.
    Opens the builder environment viewer.

    Modifies:
        current_img (str):
            path to the image of the current environment.
        current_df (pd.DataFrame):
            holds a train list of the current environment.
        current_builder_backup_df (pd.DataFrame):
            holds a backup train list of the current environment for the build
            mode.
        current_modify_backup_df (pd.DataFrame):
            holds a backup train list of the current environment for the modify
            mode.
        current_builder_backup_array (np.array):
            holds a backup layered map representation of the current environment
            for the build mode.
        current_modify_backup_array (np.array):
            holds a backup layered map representation of the current environment
            for the modify mode.
        env_counter:
            tracks changes to the current environment.
    """
    global current_img, current_builder_backup_array, current_builder_backup_df, \
        current_modify_backup_array, current_modify_backup_df, env_counter, \
        current_df
    print("\nBuilding environment...")

    # check if there are trains in the environment
    if len(current_df) == 0:
        labels['builder_status_label'].label.config(
            text='No Trains Placed',
            fg=bad_status_color,
        )
        frames['train_builder_menu_frame'].frame.update()
        print(f"❌ Environment needs at least one train.")
        return
    else:
        labels['builder_status_label'].label.config(
            text='...Building...',
            fg=good_status_color,
        )
        frames['train_builder_menu_frame'].frame.update()

    tracks = current_array[0]
    trains = get_trains()

    prev_agent_count = user_params['agents']
    user_params['agents'] = len(trains)

    # try to generate an image of the environment
    env, trains, invalid_train, invalid_station = create_custom_env(tracks, trains, user_params)

    # handle possible errors from the image creation
    if invalid_train is not None:
        user_params['agents'] = prev_agent_count
        labels['builder_status_label'].label.config(
            text=f'Train {invalid_train} not on track',
            fg=bad_status_color,
        )
        frames['train_builder_menu_frame'].frame.update()
        return
    if invalid_station is not None:
        if invalid_station >= 0:
            user_params['agents'] = prev_agent_count
            labels['builder_status_label'].label.config(
                text=f'Station of Train {invalid_station} not on track',
                fg=bad_status_color,
            )
            frames['train_builder_menu_frame'].frame.update()
            return
        else:
            user_params['agents'] = prev_agent_count
            labels['builder_status_label'].label.config(
                text=f'Missing Station of Train {-(invalid_station+1)}',
                fg=bad_status_color,
            )
            frames['train_builder_menu_frame'].frame.update()
            return

    # check if trains have necessary parameters
    if current_df['e_dep'].isin([-1]).any():
        user_params['agents'] = prev_agent_count
        labels['builder_status_label'].label.config(
            text='A train has no earliest departure',
            fg=bad_status_color,
        )
        frames['train_builder_menu_frame'].frame.update()
        print(f"❌ All trains must be fully configured.")
        return
    elif current_df['l_arr'].isin([-1]).any():
        user_params['agents'] = prev_agent_count
        labels['builder_status_label'].label.config(
            text='A train has no latest arrival',
            fg=bad_status_color,
        )
        frames['train_builder_menu_frame'].frame.update()
        return
    elif current_df['speed'].isin([-1]).any():
        user_params['agents'] = prev_agent_count
        labels['builder_status_label'].label.config(
            text='A train has no speed',
            fg=bad_status_color,
        )
        frames['train_builder_menu_frame'].frame.update()
        return

    start_pos = list(zip(trains['y'], trains['x']))
    end_pos = list(zip(trains['y_end'], trains['x_end']))

    current_df = pd.DataFrame({
        'start_pos': start_pos,
        'dir': trains['dir'],
        'end_pos': end_pos,
        'e_dep': trains['e_dep'],
        'l_arr': trains['l_arr'],
        'speed': trains['speed'],
    })

    # save the generated image for the runtime of the program
    delete_tmp_frames()
    env_counter += 1
    os.makedirs("data", exist_ok=True)
    if save_png(env, "data/running_tmp.png", user_params["lowQuality"]) == -1:
        labels['builder_status_label'].label.config(
            text='Flatland failed to create image.\n'
                 'Please restart the program.',
            fg=bad_status_color,
        )
        frames['train_builder_menu_frame'].frame.update()
        return

    current_img = 'data/running_tmp.png'

    if 'train_builder_menu_frame' in frames:
        frames['train_builder_menu_frame'].destroy_frame()
        del frames['train_builder_menu_frame']
    if 'builder_grid_frame' in frames:
        frames['builder_grid_frame'].destroy_frame()
        del frames['builder_grid_frame']
    if 'builder_train_help_frame' in frames:
        frames['builder_train_help_frame'].destroy_frame()
        del frames['builder_train_help_frame']

    current_builder_backup_array = current_array.copy()
    current_builder_backup_df = current_df.copy()
    current_modify_backup_array = current_array.copy()
    current_modify_backup_df = current_df.copy()

    build_builder_env_viewer()
    build_builder_env_menu()

def build_builder_env_viewer():
    """Builds the builder environment viewer."""
    frames['builder_env_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    canvases['builder_env_viewer_canvas'] = EnvCanvas(
        root=frames['builder_env_viewer_frame'].frame,
        width=frames['builder_env_viewer_frame'].width,
        height=frames['builder_env_viewer_frame'].height,
        x=frames['builder_env_viewer_frame'].width * 0,
        y=frames['builder_env_viewer_frame'].height * 0,
        font=canvas_font_layout,
        background_color=canvas_color,
        grid_color=grid_color,
        border_width=0,
        image=current_img,
        rows=user_params['rows'],
        cols=user_params['cols'],
    )

    frames['builder_env_viewer_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_env_viewer_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_env_viewer_frame'].frame.grid_propagate(False)

def build_builder_env_menu():
    """Builds the environment viewer menu."""
    frames['builder_env_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['return_to_menu_button'] = Button(
        root=frames['builder_env_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='n',
        command=switch_builder_to_main,
        text='Confirm',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=blue_button_color,
        border_width=0,
        visibility=True,
        style_map=blue_button_style_map,
    )

    current_df_to_env_text(mode='build')
    with open("data/info_text.txt", "r") as file:
        displaytext = file.read()

    texts['builder_env_trains'] = Text(
        root=frames['builder_env_menu_frame'].frame,
        width=frames['builder_env_menu_frame'].width,
        height=frames['builder_env_menu_frame'].height * 0.75,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=displaytext,
        font=info_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_env_menu_frame'].frame.rowconfigure(0, weight=15)
    frames['builder_env_menu_frame'].frame.rowconfigure(1, weight=1)
    frames['builder_env_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_env_menu_frame'].frame.grid_propagate(False)

def builder_toggle_advanced_para_options():
    """Toggles the visibility of labels and entries in builder para frame."""
    labels['remove_label'].toggle_visibility()
    if buttons['remove_button'].winfo_ismapped():
        buttons['remove_button'].grid_forget()
    else:
        buttons['remove_button'].grid(row=4, column=3, sticky='n')
    labels['malfunction_label'].toggle_visibility()
    entry_fields['malfunction_entry'].toggle_visibility()
    labels['min_duration_label'].toggle_visibility()
    entry_fields['min_duration_entry'].toggle_visibility()
    labels['max_duration_label'].toggle_visibility()
    entry_fields['max_duration_entry'].toggle_visibility()
    labels['lowQuality_label'].toggle_visibility()
    if buttons['lowQuality_button'].winfo_ismapped():
        buttons['lowQuality_button'].grid_forget()
    else:
        buttons['lowQuality_button'].grid(row=8, column=3, sticky='n')
    return

def switch_builder_to_main():
    """Destroys all builder env viewer menu frames and opens the main menu.

    Modifies:
        build_mode (str):
            global tracker for the current mode in the builder view.
    """
    global build_mode

    build_mode = None

    if 'builder_env_viewer_frame' in frames:
        frames['builder_env_viewer_frame'].destroy_frame()
        del frames['builder_env_viewer_frame']
    if 'builder_env_menu_frame' in frames:
        frames['builder_env_menu_frame'].destroy_frame()
        del frames['builder_env_menu_frame']

    create_main_menu()

def save_builder_env_params():
    """Saves the parameters from the builder parameter frame.

    Returns:
        int: -1 if there was an error registered with any input 0 otherwise.
    """
    err_count = 0

    for field in entry_fields:
        # get the key from every entry field in the global list
        key = field.split('_')[0]
        if key not in default_params:
            continue
        if key not in ['rows','cols','globalTimeLimit','malfunction','min','max']:
            continue

        # get the data from the entry field
        data = entry_fields[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                raise ValueError
            elif data == '':
                raise ValueError
            elif key == 'malfunction':
                if data.count("/") > 1:
                    raise ValueError
                data = (int(data.split('/')[0]),int(data.split('/')[1]))
            else:
                data = int(data)

            # hide label if there was no problem with the data conversion
            labels[f'{key}_error_label'].hide_label()
        except Exception as e:
            # register the error and display corresponding error message
            err = type(e)
            err_count += 1
            if err in err_dict[key]:
                labels[f'{key}_error_label'].label.config(
                    text=err_dict[key][err])
                labels[f'{key}_error_label'].place_label()
            else:
                print(e)
                print(err)
                print(data)
            continue

        # check for additional constrains and display error when violated
        if key == 'rows' and data < 1:
            err_count += 1
            err = 'notEnoughRows'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key == 'cols' and data < 1:
            err_count += 1
            err = 'notEnoughCols'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key == 'globalTimeLimit' and data < 1:
            err_count += 1
            err = 'notEnoughTime'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='malfunction' and data[1] == 0:
            err_count += 1
            err = 'divByZero'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='malfunction' and data[0]/data[1] < 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='malfunction' and data[0]/data[1] > 1:
            err_count += 1
            err = 'tooBigMalfunction'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='min' and data <= 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='max' and data <= 0:
            err_count += 1
            err = 'negativeValue'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()

        # only save non string values as parameters except for the clingo path
        if type(data) is not str:
            user_params[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_builder_env_params():
    """Load the current user parameters onto the random gen para frame"""
    for field in entry_fields:
        # get the key from every entry field in the global list
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key not in ['rows','cols','globalTimeLimit','malfunction','min','max']:
            continue
        elif user_params[key] is None:
            continue
        elif key == 'malfunction':
            entry_fields[field].insert_string(
                f'{user_params["malfunction"][0]}/'
                f'{user_params["malfunction"][1]}'
            )
        else:
            entry_fields[field].insert_string(str(user_params[key]))

def open_reset_frame(parent_frame):
    """Builds builder reset frame."""
    frames['reset_frame'] = Frame(
        root=parent_frame.root,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    labels['reset_label'] = Label(
        root=frames['reset_frame'].frame,
        grid_pos=(0, 0),
        padding=(0, 60),
        columnspan=2,
        sticky='s',
        text='RESET GRID?',
        font=title_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['yes_reset_button'] = Button(
        root=frames['reset_frame'].frame,
        width=12,
        height=2,
        grid_pos=(1, 0),
        padding=(40, 0),
        sticky='ne',
        command=reset_builder_grid,
        text='YES',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['no_reset_button'] = Button(
        root=frames['reset_frame'].frame,
        width=12,
        height=2,
        grid_pos=(1, 1),
        padding=(40, 0),
        sticky='nw',
        command=frames['reset_frame'].destroy_frame,
        text='NO',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['reset_frame'].frame.rowconfigure(0, weight=2)
    frames['reset_frame'].frame.rowconfigure(1, weight=3)
    frames['reset_frame'].frame.columnconfigure((0, 1), weight=1)
    frames['reset_frame'].frame.grid_propagate(False)

def reset_builder_grid():
    """Reset current environment and return to track builder view.

    Reset current environment to the backups made upon entering the build or
    modify menu.

    Destroys reset frame and current build menu view and builds the track
    builder menu frame.

    Modifies:
        current_array (np.array):
            holds a map representation of the current environment.
        current_df (pd.DataFrame):
            holds a train list of the current environment.
    """
    global current_array, current_df

    if build_mode == 'build':
        current_array = current_builder_backup_array.copy()
        current_df = current_builder_backup_df.copy()
    else:
        current_array = current_modify_backup_array.copy()
        current_df = current_modify_backup_df.copy()

    if 'track_builder_menu_frame' in frames:
        frames['track_builder_menu_frame'].destroy_frame()
        del frames['track_builder_menu_frame']
    if 'train_builder_menu_frame' in frames:
        frames['train_builder_menu_frame'].destroy_frame()
        del frames['train_builder_menu_frame']
    if 'builder_grid_frame' in frames:
        frames['builder_grid_frame'].destroy_frame()
        del frames['builder_grid_frame']

    if 'reset_frame' in frames:
        frames['reset_frame'].destroy_frame()
        del frames['reset_frame']

    build_track_builder_menu_frame()
    build_builder_grid_frame()





# result menu

def create_result_menu():
    """Wrapper function to build the result view."""
    build_result_env_viewer()
    build_result_menu()

def build_result_env_viewer():
    """Builds the result environment viewer frame."""
    frames['result_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    canvases['result_viewer_canvas'] = ResultCanvas(
        root=frames['result_viewer_frame'].frame,
        width=frames['result_viewer_frame'].width,
        height=frames['result_viewer_frame'].height,
        x=frames['result_viewer_frame'].width * 0,
        y=frames['result_viewer_frame'].height * 0,
        font=canvas_font_layout,
        path_label_font=canvas_label_font_layout,
        background_color=canvas_color,
        grid_color=grid_color,
        border_width=0,
        image=current_img,
        paths_df=current_paths,
        rows=user_params['rows'],
        cols=user_params['cols'],
    )
    frames['result_viewer_frame'].frame.rowconfigure(0, weight=1)
    frames['result_viewer_frame'].frame.columnconfigure(0, weight=1)
    frames['result_viewer_frame'].frame.grid_propagate(False)

def build_result_menu():
    """Builds the result menu frame."""
    frames['result_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=60,
        height=60,
        grid_pos=(0, 1),
        padding=(5, 5),
        sticky='nw',
        command=toggle_result_help,
        image='data/png/info.png',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        visibility=True,
        style_map=tool_button_style_map,
    )

    buttons['show_error_logs_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=12,
        height=1,
        grid_pos=(0, 1),
        padding=(0, 10),
        sticky='n',
        command=show_error_logs,
        text='ActErr Log',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=blue_button_color,
        border_width=0,
        visibility=show_act_err_logs,
        style_map=blue_button_style_map,
    )

    labels['spacing_err_label'] = Label(
        root=frames['result_menu_frame'].frame,
        grid_pos=(0, 2),
        padding=(0, 0),
        sticky='nw',
        text='needs 0 < num <= 60',
        font=base_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['show_time_table_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=25,
        height=1,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='nwe',
        command=toggle_result_timetable,
        text='Time Table',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    min_t = int(pos_df['timestep'].min())
    max_t = int(pos_df['timestep'].max())
    timesteps = max_t - min_t + 1
    cells = user_params['rows'] * user_params['cols']
    render_time = render_time_prediction(timesteps, cells)

    buttons['show_gif_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=25,
        height=1,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='nwe',
        command=toggle_result_gif,
        text=f'Render Animation (~{render_time})',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=red_button_color,
        border_width=0,
        visibility=True,
        style_map=red_button_style_map,
    )

    labels['gif_status_label'] = Label(
        root=frames['result_menu_frame'].frame,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=base_font_layout,
        foreground_color=background_color,
        background_color=background_color,
        visibility=True,
    )

    labels['frameRate_label'] = Label(
        root=frames['result_menu_frame'].frame,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='nw',
        text='GIF Timesteps/sec:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    entry_fields['frameRate_entry'] = EntryField(
        root=frames['result_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 1),
        padding=((0, 0), 0),
        sticky='ne',
        text=f'e.g. {default_params["frameRate"]}',
        font=base_font_layout,
        foreground_color=input_color,
        background_color=entry_color,
        example_color=example_color,
        border_width=0,
        visibility=True,
    )
    if user_params['frameRate'] % 1:
        entry_fields['frameRate_entry'].insert_string(
            str(user_params['frameRate'])
        )
    else:
        entry_fields['frameRate_entry'].insert_string(
            str(int(user_params['frameRate']))
        )


    labels['frameRate_error_label'] = Label(
        root=frames['result_menu_frame'].frame,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=err_font_layout,
        foreground_color=bad_status_color,
        background_color=background_color,
        visibility=False,
    )

    labels['lowQuality_label'] = Label(
        root=frames['result_menu_frame'].frame,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='nw',
        text='GIF Low quality mode:',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['lowQuality_button'] = ToggleSwitch(
        root=frames['result_menu_frame'].frame,
        width=70, height=30,
        on_color=switch_on_color, off_color=switch_off_color,
        handle_color=input_color, background_color=background_color,
        command=change_low_quality_gif_status,
    )
    buttons['lowQuality_button'].grid(row=4, column=1, sticky='ne')
    buttons['lowQuality_button'].set_state(user_params['lowQualityGIF'])

    buttons['toggle_all_paths_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=25,
        height=1,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='we',
        command=toggle_all_paths,
        text='Toggle All Paths',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['path_list_canvas_frame'] = Frame(
        frames['result_menu_frame'].frame,
        width=frames['result_menu_frame'].width * 0.5,
        height=frames['result_menu_frame'].height * 0.25,
        grid_pos=(6,1),
        padding=(0,0),
        sticky='nwe',
        background_color=background_color,
        border_width=0,
        visibility=True,
    )

    buttons['return_to_menu_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=25,
        height=1,
        grid_pos=(7, 1),
        padding=(0, 0),
        sticky='nwe',
        command=switch_result_to_main,
        text='Return To Main Menu',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['result_menu_frame'].frame.rowconfigure(0, weight=1)
    frames['result_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['result_menu_frame'].frame.rowconfigure((1, 5, 6, 7), weight=2)
    frames['result_menu_frame'].frame.rowconfigure((2, 3, 4),weight=1)
    frames['result_menu_frame'].frame.columnconfigure(1, weight=2)
    frames['result_menu_frame'].frame.columnconfigure(2, weight=5)
    frames['result_menu_frame'].frame.grid_propagate(False)

    canvases['path_list_canvas'] = PathListCanvas(
        root=frames['path_list_canvas_frame'].frame,
        width=frames['path_list_canvas_frame'].width,
        height=frames['path_list_canvas_frame'].height,
        x=frames['path_list_canvas_frame'].width * 0,
        y=frames['path_list_canvas_frame'].height * 0,
        font=canvas_font_layout,
        background_color=background_color,
        on_color=switch_on_color,
        off_color=switch_off_color,
        handle_color=label_color,
        label_color=label_color,
        border_width=0,
        train_data=current_df,
        grid=canvases['result_viewer_canvas'],
    )

    windows['flatland_window'].window.update_idletasks()

def build_result_help_frame():
    """Builds the result menu help frame."""
    frames['result_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=dark_background_color,
        border_width=0,
        visibility=True
    )

    with open("data/help_texts/result_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['result_help_text'] = Text(
        root=frames['result_help_frame'].frame,
        width=frames['result_help_frame'].width,
        height=frames['result_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['result_help_frame'].frame.rowconfigure(0, weight=1)
    frames['result_help_frame'].frame.columnconfigure(0, weight=1)
    frames['result_help_frame'].frame.grid_propagate(False)

def build_result_timetable_frame():
    """Builds the result timetable frame."""
    frames['result_timetable_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    with open("data/info_text.txt", "r") as file:
        displaytext = file.read()

    texts['result_timetable_text'] = Text(
        root=frames['result_timetable_frame'].frame,
        width=frames['result_timetable_frame'].width,
        height=frames['result_timetable_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['result_timetable_frame'].frame.rowconfigure(0, weight=1)
    frames['result_timetable_frame'].frame.columnconfigure(0, weight=1)
    frames['result_timetable_frame'].frame.grid_propagate(False)

def build_result_gif_frame():
    """Builds the result GIF viewer frame."""
    frames['result_gif_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    frames['result_gif_container_frame'] = Frame(
        root=frames['result_gif_frame'].frame,
        width=frames['result_gif_frame'].width,
        height=frames['result_gif_frame'].height * 0.9,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        columnspan=2,
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    pictures['result_gif'] = ZoomableGIF(
        root=frames['result_gif_container_frame'].frame,
        width=frames['result_gif_container_frame'].width ,
        height=frames['result_gif_container_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        columnspan=2,
        gif=current_gif,
        rows=user_params['rows'],
        cols=user_params['cols'],
        background_color=canvas_color,
        visibility=True,
    )

    buttons['save_gif_button'] = Button(
        root=frames['result_gif_frame'].frame,
        width=15,
        height=1,
        grid_pos=(1, 0),
        padding=(5, 5),
        command=save_gif,
        text='Save GIF',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=good_status_color,
        border_width=0,
        visibility=True,
        style_map=green_button_style_map,
    )

    buttons['toggle_timestep_view_button'] = Button(
        root=frames['result_gif_frame'].frame,
        width=20,
        height=1,
        grid_pos=(1, 1),
        padding=(5, 5),
        command=toggle_timestep_viewer,
        text='Toggle View',
        font=base_font_layout,
        foreground_color=golden_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=yellow_text_button_style_map,
    )

    frames['result_gif_frame'].frame.rowconfigure((0,1), weight=1)
    frames['result_gif_frame'].frame.columnconfigure((0, 1), weight=1)
    frames['result_gif_frame'].frame.grid_propagate(False)

def build_timestep_viewer_frame():
    """Builds the result timestep viewer frame."""
    min_timestep = int(pos_df['timestep'].min())
    timestep_file_format = str(min_timestep).zfill(4)

    frames['timestep_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=frames['result_gif_frame'].width ,
        height=frames['result_gif_frame'].height * 0.9,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='new',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    frames['timestep_pic_container_frame'] = Frame(
        root=frames['timestep_viewer_frame'].frame,
        width=frames['timestep_viewer_frame'].width,
        height=frames['timestep_viewer_frame'].height * 0.95,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        columnspan=3,
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    canvases['timestep_pic'] = EnvCanvas(
        root=frames['timestep_pic_container_frame'].frame,
        width=frames['timestep_pic_container_frame'].width ,
        height=frames['timestep_pic_container_frame'].height,
        x=frames['timestep_pic_container_frame'].width * 0,
        y=frames['timestep_pic_container_frame'].height * 0,
        font=canvas_font_layout,
        background_color=canvas_color,
        grid_color=grid_color,
        border_width=0,
        image=f'data/tmp_frames/frame_{timestep_file_format}.png',
        rows=user_params['rows'],
        cols=user_params['cols'],
    )

    buttons['previous_button'] = Button(
        root=frames['timestep_viewer_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 0),
        padding=(5, 5),
        sticky='e',
        command=show_previous_timestep,
        text='<',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    labels['current_timestep_label'] = Label(
        root=frames['timestep_viewer_frame'].frame,
        grid_pos=(1, 1),
        padding=(5, 5),
        text=str(min_timestep),
        font=base_font_layout,
        foreground_color=label_color,
        background_color=background_color,
        visibility=True,
    )

    buttons['next_button'] = Button(
        root=frames['timestep_viewer_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 2),
        padding=(5, 5),
        sticky='w',
        command=show_next_timestep,
        text='>',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    frames['timestep_viewer_frame'].frame.rowconfigure((0,1), weight=1)
    frames['timestep_viewer_frame'].frame.columnconfigure((0, 2), weight=5)
    frames['timestep_viewer_frame'].frame.columnconfigure(1, weight=1)
    frames['timestep_viewer_frame'].frame.grid_propagate(False)

def toggle_all_paths():
    """Hides other frames if open and toggles all paths.

    Calls the toggle all paths function of the result viewer canvas.
    Will turn on or off paths of all trains in the environment.
    """
    if ('result_timetable_frame' in frames and
            frames['result_timetable_frame'].visibility):
        frames['result_timetable_frame'].toggle_visibility()
        
    if ('result_gif_frame' in frames and
            frames['result_gif_frame'].visibility):
        frames['result_gif_frame'].toggle_visibility()

    if ('timestep_viewer_frame' in frames and
            frames['timestep_viewer_frame'].visibility):
        frames['timestep_viewer_frame'].toggle_visibility()

    if ('result_help_frame' in frames and
            frames['result_help_frame'].visibility):
        frames['result_help_frame'].toggle_visibility()
        
    canvases['path_list_canvas'].toggle_all_paths()

def toggle_result_help():
    """Hides all other frames and opens or closes the result help frame."""
    if ('result_timetable_frame' in frames and 
            frames['result_timetable_frame'].visibility):
        frames['result_timetable_frame'].toggle_visibility()

    if ('result_gif_frame' in frames and 
            frames['result_gif_frame'].visibility):
        frames['result_gif_frame'].toggle_visibility()

    if ('timestep_viewer_frame' in frames and
            frames['timestep_viewer_frame'].visibility):
        frames['timestep_viewer_frame'].toggle_visibility()
        
    if 'result_help_frame' in frames:
        frames['result_help_frame'].toggle_visibility()
        frames['result_help_frame'].frame.rowconfigure(0, weight=1)
        frames['result_help_frame'].frame.columnconfigure(0, weight=1)
        frames['result_help_frame'].frame.grid_propagate(False)
    else:
        build_result_help_frame()

def toggle_result_timetable():
    """Hides all other frames and opens or closes the result timetable frame."""
    if ('result_gif_frame' in frames and 
            frames['result_gif_frame'].visibility):
        frames['result_gif_frame'].toggle_visibility()

    if ('timestep_viewer_frame' in frames and 
            frames['timestep_viewer_frame'].visibility):
        frames['timestep_viewer_frame'].toggle_visibility()
        
    if ('result_help_frame' in frames and 
            frames['result_help_frame'].visibility):
        frames['result_help_frame'].toggle_visibility()
        
    if 'result_timetable_frame' in frames:
        frames['result_timetable_frame'].toggle_visibility()
        frames['result_timetable_frame'].frame.rowconfigure(0, weight=1)
        frames['result_timetable_frame'].frame.columnconfigure(0, weight=1)
        frames['result_timetable_frame'].frame.grid_propagate(False)
    else:
        build_result_timetable_frame()

def toggle_result_gif():
    """Hides all other frames and opens or closes the result GIF frame.

    Checks if entered frame rate parameter is valid.
    If any of the parameters changed since the last GIF generation or if this
    is the first generation generate the GIF.

    Modifies:
        first_build_try (bool):
            global tracker for first environment generation and build try.

    Returns:
        int: -1 if there was an error registered with any input 0 otherwise.
    """
    global first_build_try, current_timestep

    err_count = 0

    for field in entry_fields:
        # get the key from every entry field in the global list
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key != 'frameRate':
            continue

        # get the data from the entry field
        data = entry_fields[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = default_params[key]
            elif data == '':
                data = default_params[key]
            else:
                data = float(data)

            # hide label if there was no problem with the data conversion
            labels[f'{key}_error_label'].hide_label()
        except Exception as e:
            # register the error and display corresponding error message
            err = type(e)
            err_count += 1
            if err in err_dict[key]:
                labels[f'{key}_error_label'].label.config(
                    text=err_dict[key][err])
                labels[f'{key}_error_label'].place_label()
            else:
                print(e)
                print(err)
                print(data)
            continue

        # check for additional constrains and display error when violated
        if key=='frameRate' and data <= 0:
            err_count += 1
            err = 'negativeFrameRate'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
        elif key=='frameRate' and data > 60:
            err_count += 1
            err = 'tooBigFrameRate'
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()

        # only save non string values as parameters except for the clingo path
        if type(data) is not str:
            user_params[key] = data

    if err_count:
        return -1
    else:
        # hide label if there was no problem with the parameter checking
        labels['frameRate_error_label'].hide_label()
        frames['result_menu_frame'].frame.update()

    if ('result_timetable_frame' in frames and 
            frames['result_timetable_frame'].visibility):
        frames['result_timetable_frame'].toggle_visibility()
        
    if ('result_help_frame' in frames and 
            frames['result_help_frame'].visibility):
        frames['result_help_frame'].toggle_visibility()

    current_gif_params = (user_params['frameRate'], user_params['lowQualityGIF'])

    if ('timestep_viewer_frame' in frames and 
            frames['timestep_viewer_frame'].visibility):
        frames['timestep_viewer_frame'].toggle_visibility()
        frames['timestep_viewer_frame'].frame.rowconfigure(0, weight=2)
        frames['timestep_viewer_frame'].frame.rowconfigure(1, weight=1)
        frames['timestep_viewer_frame'].frame.columnconfigure((0, 2), weight=2)
        frames['timestep_viewer_frame'].frame.columnconfigure(1, weight=1)
        frames['timestep_viewer_frame'].frame.grid_propagate(False)

    # check if the parameters changed since the last generation
    # or if this is the first generation with this environment
    if 'result_gif_frame' in frames and last_gif_params == current_gif_params:
        frames['result_gif_frame'].toggle_visibility()
        frames['result_gif_frame'].frame.rowconfigure(0, weight=1)
        frames['result_gif_frame'].frame.columnconfigure(0, weight=1)
        frames['result_gif_frame'].frame.grid_propagate(False)
    elif 'result_gif_frame' in frames and last_gif_params != current_gif_params:
        if first_build_try:
            # on the first try return with a warning to the result menu
            first_build_try = False
            if user_params['rows'] * user_params['cols'] > 1000000:
                labels['gif_status_label'].label.config(
                    text=f'Warning: Large GIF size.\n'
                         f'Memory issues may disrupt execution.\n\n'
                         f'⚠️Click again to proceed at your own risk⚠️',
                    fg=golden_color,
                    font=err_font_layout,
                )
                labels['gif_status_label'].place_label()
                return
        else:
            # reset the first try on the second try and continue
            first_build_try = True

        frames['result_gif_frame'].destroy_frame()
        del frames['result_gif_frame']

        if 'timestep_viewer_frame' in frames:
            frames['timestep_viewer_frame'].destroy_frame()
            del frames['timestep_viewer_frame']

        labels['gif_status_label'].label.config(
            text='...Rendering GIF...',
            fg=good_status_color,
        )
        frames['result_menu_frame'].frame.update()
        create_gif()
        current_timestep = int(pos_df['timestep'].min())
        build_result_gif_frame()
    else:
        if first_build_try:
            # on the first try return with a warning to the result menu
            first_build_try = False
            if user_params['rows'] * user_params['cols'] > 1000000:
                labels['gif_status_label'].label.config(
                    text=f'Warning: Large GIF size.\n'
                         f'Memory issues may disrupt execution.\n\n'
                         f'⚠️Click again to proceed at your own risk⚠️',
                    fg=golden_color,
                    font=err_font_layout,
                )
                labels['gif_status_label'].place_label()
                return
        else:
            # reset the first try on the second try and continue
            first_build_try = True

        labels['gif_status_label'].label.config(
            text='...Rendering GIF...',
            fg=good_status_color,
        )
        frames['result_menu_frame'].frame.update()
        create_gif()
        current_timestep = int(pos_df['timestep'].min())
        build_result_gif_frame()

    labels['gif_status_label'].label.config(
        text='',
        fg=good_status_color,
    )
    frames['result_menu_frame'].frame.update()

def toggle_timestep_viewer():
    """Opens or hides the result help frame."""
    if 'timestep_viewer_frame' in frames :
        frames['timestep_viewer_frame'].toggle_visibility()
        frames['timestep_viewer_frame'].frame.rowconfigure(0, weight=2)
        frames['timestep_viewer_frame'].frame.rowconfigure(1, weight=1)
        frames['timestep_viewer_frame'].frame.columnconfigure((0, 2), weight=2)
        frames['timestep_viewer_frame'].frame.columnconfigure(1, weight=1)
        frames['timestep_viewer_frame'].frame.grid_propagate(False)
    else:
        build_timestep_viewer_frame()

def show_previous_timestep():
    """Switch the image in timestep viewer to image of the previous timestep.

    Modifies:
        current_timestep (int):
            global tracker of the current timestep in the result timestep view.
    """
    global current_timestep

    frame_list = []

    for file in os.listdir('data/tmp_frames'):
        frame_list.append(file)

    # sort the list by the frame numbers
    frame_list = sorted(
        frame_list,
        key=lambda x: int(re.search(r'\d{4}', x).group())
    )

    min_t = int(pos_df['timestep'].min())
    max_t = int(pos_df['timestep'].max())
    if current_timestep is None:
        current_timestep = min_t
    
    if current_timestep == min_t:
        current_timestep = max_t
    else:
        current_timestep -= 1

    # show the new timestep image and update the displayed timestep on the frame
    pic = f'data/tmp_frames/{frame_list[current_timestep-min_t]}'
    canvases['timestep_pic'].image = canvases['timestep_pic'].get_image(pic)
    canvases['timestep_pic'].draw_image()
    labels['current_timestep_label'].label.config(text=str(current_timestep))
    frames['timestep_pic_container_frame'].frame.update()
    return

def show_next_timestep():
    """Switch the image in timestep viewer to image of the next timestep.

    Modifies:
        current_timestep (int):
            global tracker of the current timestep in the result timestep view.
    """
    global current_timestep

    frame_list = []

    for file in os.listdir('data/tmp_frames'):
        frame_list.append(file)

    # sort the list by the frame numbers
    frame_list = sorted(
        frame_list,
        key=lambda x: int(re.search(r'\d{4}', x).group())
    )

    min_t = int(pos_df['timestep'].min())
    if current_timestep is None:
        current_timestep = min_t
    
    if current_timestep-min_t < len(frame_list)-1:
        current_timestep += 1
    else:
        current_timestep = min_t

    # show the new timestep image and update the displayed timestep on the frame
    pic = f'data/tmp_frames/{frame_list[current_timestep-min_t]}'
    canvases['timestep_pic'].image = canvases['timestep_pic'].get_image(pic)
    canvases['timestep_pic'].draw_image()
    labels['current_timestep_label'].label.config(text=str(current_timestep))
    frames['timestep_pic_container_frame'].frame.update()
    return

def show_error_logs():
    """Builds the result error log viewer.

    Loads the full and minimized error log from data/act_err.txt or
    data/act_err_min.txt

    Modifies:
        current_act_err_log (str):
            global tracker to keep track of displayed error log type.
    """
    global current_act_err_log

    frames['result_error_log_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=int(screenwidth * 0.5),
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color=background_color,
        border_width=0,
        visibility=True
    )

    buttons['hide_error_logs_button'] = Button(
        root=frames['result_error_log_frame'].frame,
        width=15,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        command=hide_error_logs,
        text='Hide Log',
        font=base_font_layout,
        foreground_color=label_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=base_button_style_map,
    )

    buttons['switch_error_logs_button'] = Button(
        root=frames['result_error_log_frame'].frame,
        width=15,
        height=1,
        grid_pos=(0, 1),
        padding=(0, 0),
        command=switch_error_logs,
        text='Toggle Details',
        font=base_font_layout,
        foreground_color=golden_color,
        background_color=button_color,
        border_width=0,
        visibility=True,
        style_map=yellow_text_button_style_map,
    )

    with open("data/act_err_min.txt", "r") as file:
        min_displaytext = file.read()
    current_act_err_log = 'min'

    texts['result_min_error_log_text'] = Text(
        root=frames['result_error_log_frame'].frame,
        width=frames['result_error_log_frame'].width,
        height=frames['result_error_log_frame'].height,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='nesw',
        columnspan=2,
        text=min_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=True,
    )

    scroll_bars['min_err_log'] = tk.Scrollbar(
        frames['result_error_log_frame'].frame,
        command=texts['result_min_error_log_text'].text.yview
    )
    texts['result_min_error_log_text'].text.config(
        yscrollcommand=scroll_bars['min_err_log'].set
    )
    scroll_bars['min_err_log'].grid(
        row=1, column=0, sticky='nes', columnspan=2
    )

    with open("data/act_err.txt", "r") as file:
        full_displaytext = file.read()

    texts['result_full_error_log_text'] = Text(
        root=frames['result_error_log_frame'].frame,
        width=frames['result_error_log_frame'].width,
        height=frames['result_error_log_frame'].height,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='nesw',
        columnspan=2,
        text=full_displaytext,
        font=help_font_layout,
        wrap='word',
        foreground_color=label_color,
        background_color=dark_background_color,
        border_width=0,
        state='disabled',
        visibility=False,
    )

    scroll_bars['full_err_log'] = tk.Scrollbar(
        frames['result_error_log_frame'].frame,
        command=texts['result_full_error_log_text'].text.yview
    )
    texts['result_full_error_log_text'].text.config(
        yscrollcommand=scroll_bars['full_err_log'].set
    )

    frames['result_error_log_frame'].frame.rowconfigure(0, weight=1)
    frames['result_error_log_frame'].frame.rowconfigure(1, weight=5)
    frames['result_error_log_frame'].frame.columnconfigure((0,1), weight=1)
    frames['result_error_log_frame'].frame.grid_propagate(False)

def switch_error_logs():
    """Hide one type of error log and show the other one.

    Modifies:
        current_act_err_log (str):
            global tracker to keep track of displayed error log type.
    """
    global current_act_err_log

    if current_act_err_log == 'min':
        texts['result_full_error_log_text'].place_text()
        scroll_bars['full_err_log'].grid(
            row=1, column=0, sticky='nes', columnspan=2
        )
        texts['result_min_error_log_text'].hide_text()
        scroll_bars['min_err_log'].grid_forget()
        current_act_err_log = 'full'
    else:
        texts['result_min_error_log_text'].place_text()
        scroll_bars['min_err_log'].grid(
            row=1, column=0, sticky='nes', columnspan=2
        )
        texts['result_full_error_log_text'].hide_text()
        scroll_bars['full_err_log'].grid_forget()
        current_act_err_log = 'min'

def hide_error_logs():
    """Opens or hides the result error log frame."""
    if 'result_error_log_frame' in frames:
        frames['result_error_log_frame'].toggle_visibility()
        frames['result_error_log_frame'].frame.rowconfigure(0, weight=1)
        frames['result_error_log_frame'].frame.rowconfigure(1, weight=5)
        frames['result_error_log_frame'].frame.columnconfigure((0, 1), weight=1)
        frames['result_error_log_frame'].frame.grid_propagate(False)
    else:
        show_error_logs()

def switch_result_to_main():
    """Destroy the result menu frames and build the main menu.

    Resets the first_build_try tracker.

    Modifies:
        first_build_try (bool):
            global tracker for first environment generation and build try.
    """
    global first_build_try

    first_build_try = True

    if 'result_viewer_frame' in frames:
        frames['result_viewer_frame'].destroy_frame()
        del frames['result_viewer_frame']
    if 'result_menu_frame' in frames:
        frames['result_menu_frame'].destroy_frame()
        del frames['result_menu_frame']
    if 'result_help_frame' in frames:
        frames['result_help_frame'].destroy_frame()
        del frames['result_help_frame']
    if 'result_timetable_frame' in frames:
        frames['result_timetable_frame'].destroy_frame()
        del frames['result_timetable_frame']
    if 'result_gif_frame' in frames:
        frames['result_gif_frame'].destroy_frame()
        del frames['result_gif_frame']
    if 'timestep_viewer_frame' in frames:
        frames['timestep_viewer_frame'].destroy_frame()
        del frames['timestep_viewer_frame']
    if 'result_error_log_frame' in frames:
        frames['result_error_log_frame'].destroy_frame()
        del frames['result_error_log_frame']

    create_main_menu()





# functions

def change_grid_status():
    """Changes the grid parameter to the opposite"""
    user_params['grid'] = not user_params['grid']

def change_remove_status():
     """Changes the remove parameter to the opposite"""
     user_params['remove'] = not user_params['remove']

def change_low_quality_status():
    """Changes the lowQuality parameter to the opposite"""
    user_params['lowQuality'] = not user_params['lowQuality']

def change_low_quality_gif_status():
    """Changes the lowQualityGIF parameter to the opposite"""
    user_params['lowQualityGIF'] = not user_params['lowQualityGIF']

def change_save_image_status():
    """Changes the saveImage parameter to the opposite"""
    user_params['saveImage'] = not user_params['saveImage']

def create_gif():
    """Calls a GIF render from the current environment.

    Modifies:
        current_gif (str):
            holds teh path to the current GIF.
        last_gif_params (tuple(float, bool)):
            parameters at the time of the last GIF rendering.
    """
    global current_gif, last_gif_params

    tracks = current_array[0]
    trains = get_trains()
    current_gif = 'data/running_tmp.gif'
    fps = user_params['frameRate']
    low_q = user_params['lowQualityGIF']
    last_gif_params = (fps, low_q)
    render_gif(tracks, trains, current_paths, user_params, env_counter, current_gif, fps, low_q)

def save_gif():
    """Opens file dialog and saves GIF in selected location."""
    file = filedialog.asksaveasfilename(
        title="Select GIF save file",
        initialdir='env',
        defaultextension=".gif",
        filetypes=[("GIFs", "*.gif"), ("All Files", "*.*")],
    )

    if not file:
        return

    shutil.copy2('data/running_tmp.gif', file)

def df_to_timetable_text():
    """Creates a timetable from the current environment.

    Saves timetable in data/info_text.txt.

    Modifies:
        current_act_err_log (str):
            global tracker to keep track of displayed error log type.
    """
    global show_act_err_logs

    def format_row(idx, line) -> str:
        """Helper function to format a timetable row."""
        new_line = (f"| {idx:>8} | {line['e_dep']:>8} | {line['a_dep']:>6} | "
                    f"{line['l_arr']:>6} | {line['a_arr']:>6} |")
        return new_line

    a_dep = (
        current_paths.groupby("trainID")["timestep"]
        .apply(lambda x: x.iloc[0] if len(x) == 1 else x.nsmallest(2).iloc[-1])
        .tolist()
    )
    a_arr = current_paths.groupby("trainID")["timestep"].max().tolist()

    for index, (_, row) in enumerate(current_df.iterrows()):
        if row['start_pos'] == row['end_pos']:
            a_dep[index] = '--'
            a_arr[index] = '--'
        if (row['start_pos'] != row['end_pos'] and
                a_dep[index] == a_arr[index]  and a_arr[index] == 0):
            a_dep[index] = 'ActErr'
            a_arr[index] = 'ActErr'
            show_act_err_logs = True

    df = pd.DataFrame({
        'e_dep': current_df['e_dep'],
        'a_dep': a_dep,
        'l_arr': current_df['l_arr'],
        'a_arr': a_arr,
    })

    header = ("|          |      Departure    |     Arrival     |\n"
              "| Train ID | Earliest | Actual | Latest | Actual |")
    divider = "|----------|----------|--------|--------|--------|"

    new_rows = [format_row(index, row) for index, row in df.iterrows()]

    with open('data/info_text.txt', "w") as file:
        file.write(header + "\n")
        file.write(divider + "\n")
        file.writelines(new_row + "\n" for new_row in new_rows)

def get_load_info():
    """Prepares the info of the loaded environment.

    Saves the prepared info of the loaded environment in the data/info_text.txt
    """
    def format_row(index, row):
        """Formats a text line from the passed row and index."""
        new_line = (f"| {index:>8} | {str(row['start_pos']):>14} "
                    f"| {row['dir']:^3} | {str(row['end_pos']):>14} "
                    f"| {row['e_dep']:>5} | {row['l_arr']:>5} | {row['speed']:>5} |")
        return new_line

    param_header = '| Parameters |'
    param_divider = '|------------|'

    load_param_text = [
        f'|-Global Time Limit: {user_params["globalTimeLimit"]}',
    ]

    spacing = '|\n|'

    table_header = ("| Train ID | Start Position | Dir |   "
                    "End Position | E Dep | L Arr | Speed |")
    table_divider = ("|----------|----------------|-----|"
                     "----------------|-------|-------|-------|")

    new_rows = [format_row(index, row) for index, row in current_df.iterrows()]

    with open('data/info_text.txt', "w") as file:
        file.write(param_divider + '\n')
        file.write(param_header + '\n')
        file.write(param_divider + '\n')
        for row in load_param_text:
            file.write(row + '\n')
        file.write(spacing + '\n')
        file.write(table_divider + '\n')
        file.write(table_header + '\n')
        file.write(table_divider + '\n')
        file.writelines(row + '\n' for row in new_rows)
        file.write(table_divider + '\n')

def current_df_to_env_text(mode):
    """Create a train list from the current_df.

    Saves the train list in data/info_text.txt.
    """
    def format_row(index, row) -> str:
        """Helper function to format a dataframe row"""
        new_line = (f"| {index:>8} | {str(row['start_pos']):>14} "
                    f"| {row['dir']:^3} | {str(row['end_pos']):>14} "
                    f"| {row['e_dep']:>5} | {row['l_arr']:>5} | {row['speed']:>5} |")
        return new_line

    param_header = '| Parameters |'
    param_divider = '|------------|'

    gen_param_text = [
        f'|-Environment Seed: {user_params["seed"]}',
        f'|-Global Time Limit: {user_params["globalTimeLimit"]}',
        f'|-Grid Mode: {user_params["grid"]}',
        f'|-Remove agents on arrival: {user_params["remove"]}',
        f'|-Speeds of Trains: {user_params["speedMap"]}',
        f'|-Malfunction rate: '
        f'{user_params["malfunction"][0]}/{user_params["malfunction"][1]}',
        f'|-Minimum Duration of Malfunctions: {user_params["min"]}',
        f'|-Maximum Duration of Malfunctions: {user_params["max"]}',
    ]
    build_param_text = [
        f'|-Global Time Limit: {user_params["globalTimeLimit"]}',
        f'|-Remove agents on arrival: {user_params["remove"]}',
        f'|-Environment Time Limit: {user_params["globalTimeLimit"]}',
        f'|-Malfunction rate: '
        f'{user_params["malfunction"][0]}/{user_params["malfunction"][1]}',
        f'|-Minimum Duration of Malfunctions: {user_params["min"]}',
        f'|-Maximum Duration of Malfunctions: {user_params["max"]}',
    ]

    spacing = '|\n|'

    table_header = ("| Train ID | Start Position | Dir |   "
                    "End Position | E Dep | L Arr | Speed |")
    table_divider = ("|----------|----------------|-----|"
                     "----------------|-------|-------|-------|")

    new_rows = [format_row(index, row) for index, (_, row) in enumerate(current_df.iterrows())]

    with open('data/info_text.txt', "w") as file:
        file.write(param_divider + '\n')
        file.write(param_header + '\n')
        file.write(param_divider + '\n')
        for row in gen_param_text if mode == 'gen' else build_param_text:
            file.write(row + '\n')
        file.write(spacing + '\n')
        file.write(table_divider + '\n')
        file.write(table_header + '\n')
        file.write(table_divider + '\n')
        file.writelines(row + '\n' for row in new_rows)
        file.write(table_divider + '\n')

def save_user_data_to_file():
    """Save teh user parameters in data/user_params.json."""
    with open('data/user_params.json', 'w') as file:
        json.dump(user_params, file, indent=4)

def load_user_data_from_file():
    """Load the user parameters from data/user_params.json.

    Use default parameters if no user data is ave fora parameter.

    Modifies:
        user_params (dict):
            holds the current user parameters.
        user_params_backup (dict):
            holds a backup of the current user parameters.
    """
    global user_params, user_params_backup

    with open('data/user_params.json', 'r') as file:
        data = json.load(file)

    if data['speedMap'] is not None:
        data['speedMap'] = {float(k): float(v) for k, v in data['speedMap'].items()}
    if data['malfunction'] is not None:
        data['malfunction'] = (data['malfunction'][0], data['malfunction'][1])

    user_params = data
    user_params_backup = data

    # use default if no user parameters given
    for key in user_params:
        if user_params[key] is None or user_params[key] == []:
            user_params[key] = default_params[key]

def load_env_from_file():
    """Load an environment from a .lp file.

    Switches to main menu or reloads main menu environment viewer frame.
    Opens main menu load info frame.

    Display a status or error label in the start or main menu, determined by
    the global last_menu value.

    Modifies:
        current_img (str):
            path to the image of the current environment.
        env_counter:
            tracks changes to the current environment.
        current_df (pd.DataFrame):
            holds a train list of the current environment.
        current_array (np.array):
            holds a layered map representation of the current environment.
        current_builder_backup_df (pd.DataFrame):
            holds a backup train list of the current environment for the build
            mode.
        current_modify_backup_df (pd.DataFrame):
            holds a backup train list of the current environment for the modify
            mode.
        current_builder_backup_array (np.array):
            holds a backup layered map representation of the current environment
            for the build mode.
        current_modify_backup_array (np.array):
            holds a backup layered map representation of the current environment
            for the modify mode.

    """
    global current_array, current_df, current_img, env_counter, \
        current_builder_backup_array, current_builder_backup_df, \
        current_modify_backup_array, current_modify_backup_df

    file = filedialog.askopenfilename(
        title="Select LP Environment File",
        initialdir='env',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    if not file:
        return

    if last_menu == 'start':
        labels['start_load_status_label'].label.config(
            text='...Loading...',
            fg=good_status_color,
        )
        frames['start_menu_frame'].frame.update()
    else:
        labels['main_load_status_label'].label.config(
            text='...Loading...',
            fg=good_status_color,
        )
        frames['main_menu_frame'].frame.update()

    tracks, trains, user_params['globalTimeLimit'] = load_env(file)

    # check for possible error values
    if isinstance(tracks, int):
        if last_menu == 'start':
            labels['start_load_status_label'].label.config(
                text=loading_err_dict[tracks],
                fg=bad_status_color,
            )
            frames['start_menu_frame'].frame.update()
        else:
            labels['main_load_status_label'].label.config(
                text=loading_err_dict[tracks],
                fg=bad_status_color,
            )
            frames['main_menu_frame'].frame.update()
        return

    start_pos = list(zip(trains['y'], trains['x']))
    end_pos = list(zip(trains['y_end'], trains['x_end']))

    current_df = pd.DataFrame({
        '': trains['id'],
        'start_pos': start_pos,
        'dir': trains['dir'],
        'end_pos': end_pos,
        'e_dep': trains['e_dep'],
        'l_arr': trains['l_arr'],
        'speed': trains['speed'],
    }).set_index('')

    direction = {
        'n': 1,
        'e': 2,
        's': 3,
        'w': 4,
    }

    tracks = np.array(tracks)
    current_array = np.zeros((3, *tracks.shape), dtype=int)
    current_array[0] = tracks

    for _, row in current_df.iterrows():
        # add all trains and stations to the current_array
        current_array[1][row['start_pos']] = direction[row['dir']]
        if row['end_pos'] != (-1, -1):
            current_array[2][row['end_pos']] = 5

    user_params['rows'] = tracks.shape[0]
    user_params['cols'] = tracks.shape[1]
    user_params['agents'] = len(trains)

    print("\nBuilding environment...")
    env,_,_,_ = create_custom_env(tracks, trains, user_params)

    # save the png for the runtime of the program
    delete_tmp_frames()
    env_counter += 1
    os.makedirs("data", exist_ok=True)
    if save_png(env, "data/running_tmp.png") == -1:
        if last_menu == 'start':
            labels['start_load_status_label'].label.config(
                text='Flatland failed to create image.\n'
                     'Please restart the program.',
                fg=bad_status_color,
            )
            frames['start_menu_frame'].frame.update()
        else:
            labels['main_load_status_label'].label.config(
                text='Flatland failed to create image.\n'
                     'Please restart the program.',
                fg=bad_status_color,
            )
            frames['main_menu_frame'].frame.update()
        return

    current_img = 'data/running_tmp.png'

    # also copy to the backup data
    current_builder_backup_array = current_array.copy()
    current_builder_backup_df = current_df.copy()
    current_modify_backup_array = current_array.copy()
    current_modify_backup_df = current_df.copy()

    if last_menu == 'start':
        switch_start_to_main()
    else:
        labels['main_load_status_label'].label.config(
            text='',
            fg=background_color,
        )
        frames['main_menu_frame'].frame.update()
        reload_main_env_viewer()
        build_main_menu_load_info_frame()

def save_env_to_file():
    """Save an environment into a .lp file.

    Also saves a png if the saveImage user parameter is True.
    """
    file = filedialog.asksaveasfilename(
        title="Select LP Environment File",
        initialdir='env',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    if not file:
        return

    tracks = current_array[0]
    trains = get_trains()

    save_env(tracks, trains, user_params, name=file)
    if user_params['saveImage']:
        if file.endswith('.lp'):
            image_file = file[:-2] + 'png'
        else:
            image_file = file + '.png'
        shutil.copy2(current_img, image_file)

def run_simulation() -> int:
    """Call the clingo solver.

    Modifies:
        current_paths:
            holds the paths displayed in the result viewer frame.

    Returns:
        int: 0 if no error occurred, otherwise a negative integer as error code.
    """
    global current_paths

    tracks = current_array[0]
    trains = get_trains()

    save_env(tracks, trains, user_params)

    current_paths = calc_paths(tracks, trains)
    try:
        current_paths['timestep'] = current_paths['timestep'].astype(int)
    except TypeError:
        pass

    if isinstance(current_paths, int):
        return current_paths

    delete_tmp_lp()
    return 0

def calc_paths(tracks, trains) -> pd.DataFrame:
    """Call the clingo solver.

    Args:
        tracks (np.array):
            a map of the tracks in the environment.
        trains (pd.DataFrame):
            a list of trains in the environment.

    Modifies:
        pos_df:
            holds the paths calculated by clingo.

    Returns:
        pos_df (pd.DataFrame):
            if no error occurred, otherwise a negative integer as error code.
    """
    global pos_df
    pos_df = position_df(
        tracks,
        trains,
        user_params['clingo'],
        user_params['lpFiles'] + ['data/running_tmp.lp'],
        user_params['answer']
    )
    return pos_df

def get_trains() -> pd.DataFrame :
    """Transform current_df into a different format for other functions.

    Returns:
        trains (pd.DataFrame):
            a list of trains in the environment.
    """
    x = [t[1] for t in current_df['start_pos']]
    y = [t[0] for t in current_df['start_pos']]
    x_end = [t[1] for t in current_df['end_pos']]
    y_end = [t[0] for t in current_df['end_pos']]

    trains = pd.DataFrame({
        'id': current_df.index,
        'x': x,
        'y': y,
        'dir': current_df['dir'],
        "x_end": x_end,
        "y_end": y_end,
        "e_dep": current_df['e_dep'],
        "l_arr": current_df['l_arr'],
        "speed": current_df['speed'],
    }).reset_index(drop=True)
    return trains
