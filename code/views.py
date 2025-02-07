import os
import ast
import json
from tkinter import filedialog

from code.build_png import create_custom_env, initial_render_test, save_png
from code.custom_canvas import *
from code.env import save_env, delete_tmp_lp, delete_tmp_png
from code.gen_png import gen_env
from code.lp_to_env import lp_to_env
from code.positions import position_df


# Base style parameters
screenwidth, screenheight = 1920, 1080
base_font = 20
error_scale = 0.75
font_scale = 1

# state trackers
build_mode = None
last_menu = None


# Widget handlers
windows, frames, buttons, labels = {}, {}, {}, {}
canvases, entry_fields, pictures, texts = {}, {}, {}, {}


# Parameter Dictionaries
default_params = {
    'rows': 40,
    'cols': 40,
    'agents': 4,
    'cities': 4,
    'seed': 1,
    'grid': True,
    'intercity': 2,
    'incity': 2,
    'remove': True,
    'speed': {1.0 : 1.0},
    'malfunction': (0, 30),
    'min': 2,
    'max': 6,
    'answer': 1,
    'clingo': 'clingo',
    'lpFiles': []
}
user_params = {
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
user_params_backup = user_params.copy()

# Parameter Dictionaries for Error handling
err_dict = {
    'rows': {
        ValueError: 'needs int > 0',
        'tooFewRows': 'needs at least 10 rows'
    },
    'cols': {
        ValueError: 'needs int > 0',
        'tooFewCols': 'needs at least 10 cols'
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
    'speed': {
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
    'answer': {ValueError: 'needs int > 0'},
    'clingo': {},
    'lpFiles': {},
}
loading_err_dict = {
    -1: 'No environment .lp file found',
    -2: 'A cell predicate is faulty',
    -3: 'A train predicate is faulty',
    -4: 'A start predicate is faulty',
    -5: 'A end predicate is faulty',
}
clingo_err_dict = {
    -1: 'No .lp files given',
    -2: 'Invalid clingo path',
    -3: 'Clingo returned an error',
    -4: 'Clingo returns UNSATISFIABLE',
    -5: f'Clingo did not provide the requested Answer: {user_params["answer"]}',
}


# Environment Arrays
current_array = np.zeros((3, 40, 40), dtype=int)
current_builder_backup_array = current_array.copy()
current_modify_backup_array = current_array.copy()

# Trains Dataframe
current_df = pd.DataFrame(
    columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
)
current_builder_backup_df = current_df.copy()
current_modify_backup_df = current_df.copy()

# Environment image and gif
current_img = None
current_gif = None

# Train Paths Dataframe
current_paths = pd.DataFrame()




# start menu

def build_flatland_window():
    global screenwidth, screenheight, font_scale

    load_user_data_from_file()

    windows['flatland_window'] = Window(
        width=None,
        height=None,
        fullscreen=True,
        background_color='#000000',
        title='Clingonia'
    )
    windows['flatland_window'].window.bind('<Escape>', open_exit_confirmation_frame)

    screenwidth = windows['flatland_window'].window.winfo_screenwidth()
    screenheight = windows['flatland_window'].window.winfo_screenheight()
    font_scale = ((screenwidth / 1920) ** 0.6) * ((screenheight / 1080) ** 0.4)

    windows['flatland_window'].window.rowconfigure(0, weight=1)
    windows['flatland_window'].window.columnconfigure((0, 1), weight=1)

def start_flatland():
    windows['flatland_window'].run()

def create_start_menu():
    global last_menu

    last_menu = 'start'

    build_title_frame()
    build_start_menu_frame()
    # Test rendering
    initial_test_res = initial_render_test()
    if initial_test_res == 0:
        print("Info: Launch was successful.")
    else:
        print("❌ Warning: Launch abnormal. Restart program.")
        exit()

def build_title_frame():
    frames['title_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsew',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    labels['title_label'] = Label(
        root=frames['title_frame'].frame,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsew',
        text='CLINGONIA',
        font=('Lucida Handwriting', int(font_scale * 80), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    pictures['title_gif'] = GIF(
        root=frames['title_frame'].frame,
        width=frames['title_frame'].width * 0.8,
        height=frames['title_frame'].height * 0.3,
        grid_pos=(1, 0),
        padding=(0, 0),
        sticky='n',
        gif='data/png/title_gif.gif',
        background_color='#000000',
        visibility=True,
    )

    frames['title_frame'].frame.rowconfigure((0, 1), weight=1)
    frames['title_frame'].frame.columnconfigure(0, weight=1)
    frames['title_frame'].frame.grid_propagate(False)

def build_start_menu_frame():
    frames['start_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['start_help_button'] = Button(
        root=frames['start_menu_frame'].frame,
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

    buttons['exit_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 2),
        padding=(0, 0),
        sticky='ne',
        command=open_exit_confirmation_frame,
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['random_gen_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(1,1),
        padding=(0,0),
        sticky='n',
        command=switch_start_to_random_gen,
        text='Generate Random Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['build_env_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_start_to_builder,
        text='Build New Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['load_env_button'] = Button(
        root=frames['start_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='n',
        command=load_env_from_file,
        text='Load Custom Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['start_load_status_label'] = Label(
        root=frames['start_menu_frame'].frame,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='n',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#000000',
        background_color='#000000',
        visibility=True,
    )

    frames['start_menu_frame'].frame.rowconfigure(tuple(range(4)), weight=2)
    frames['start_menu_frame'].frame.rowconfigure(5, weight=1)
    frames['start_menu_frame'].frame.columnconfigure(tuple(range(3)), weight=1)
    frames['start_menu_frame'].frame.grid_propagate(False)

def build_start_menu_help_frame():
    frames['start_menu_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#00FF00',
        border_width=0,
        visibility=True
    )

    with open("help_texts/start_menu_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['start_menu_help_frame'] = Text(
        root=frames['start_menu_help_frame'].frame,
        width=frames['start_menu_help_frame'].width,
        height=frames['start_menu_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['start_menu_help_frame'].frame.rowconfigure(0, weight=1)
    frames['start_menu_help_frame'].frame.columnconfigure(0, weight=1)
    frames['start_menu_help_frame'].frame.grid_propagate(False)

def toggle_start_menu_help():
    if 'start_menu_help_frame' in frames:
        frames['start_menu_help_frame'].toggle_visibility()
    else:
        build_start_menu_help_frame()

def switch_start_to_random_gen():
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





# main menu

def create_main_menu():
    global last_menu

    last_menu = 'main'

    build_main_menu()
    build_main_menu_env_viewer()

def build_main_menu():
    frames['main_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['main_menu_frame'].frame,
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

    buttons['exit_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 2),
        padding=(0, 0),
        sticky='ne',
        command=open_exit_confirmation_frame,
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['random_gen_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(1, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_random_gen,
        text='Generate Random Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['build_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(2, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_builder,
        text='Build New Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['modify_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(3, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_modify,
        text='Modify Existing Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['save_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(4, 1),
        padding=(0, 0),
        sticky='n',
        command=save_env_to_file,
        text='Save Custom Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['load_env_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='n',
        command=load_env_from_file,
        text='Load Custom Environment',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['main_load_status_label'] = Label(
        root=frames['main_menu_frame'].frame,
        grid_pos=(6, 1),
        padding=(0, 0),
        sticky='n',
        text='',
        font=('Arial', int(font_scale * base_font  * error_scale), 'bold'),
        foreground_color='#000000',
        background_color='#000000',
        visibility=True,
    )

    buttons['run_sim_button'] = Button(
        root=frames['main_menu_frame'].frame,
        width=30,
        height=2,
        grid_pos=(7, 1),
        padding=(0, 0),
        sticky='n',
        command=switch_main_to_clingo_para,
        text='Next: Clingo Solver',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    frames['main_menu_frame'].frame.rowconfigure(tuple(range(8)), weight=1)
    frames['main_menu_frame'].frame.columnconfigure(tuple(range(3)), weight=1)
    frames['main_menu_frame'].frame.grid_propagate(False)

def build_main_menu_help_frame():
    frames['main_menu_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("help_texts/main_menu_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['main_menu_help'] = Text(
        root=frames['main_menu_help_frame'].frame,
        width=frames['main_menu_help_frame'].width,
        height=frames['main_menu_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['main_menu_help_frame'].frame.rowconfigure(0, weight=1)
    frames['main_menu_help_frame'].frame.columnconfigure(0, weight=1)
    frames['main_menu_help_frame'].frame.grid_propagate(False)

def build_main_menu_env_viewer():
    frames['main_menu_env_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    canvases['main_menu_env_viewer_canvas'] = EnvCanvas(
        root=frames['main_menu_env_viewer_frame'].frame,
        width=frames['main_menu_env_viewer_frame'].width,
        height=frames['main_menu_env_viewer_frame'].height,
        x=frames['main_menu_env_viewer_frame'].width * 0,
        y=frames['main_menu_env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image=current_img,
        rows=user_params['rows'],
        cols=user_params['cols'],
    )

def build_clingo_para_frame():
    frames['clingo_para_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_clingo_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['back_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 1),
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

    labels['clingo_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text='Clingo Path:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
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
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['answer_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text='Answer to display:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
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
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    buttons['select_lp_files_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='n',
        columnspan=2,
        command=load_lp_files,
        text='Select LP Files',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['clingo_paths_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='n',
        columnspan=2,
        text='',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    buttons['run_sim_button'] = Button(
        root=frames['clingo_para_frame'].frame,
        width=30,
        height=2,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='n',
        columnspan=2,
        command=switch_clingo_para_to_result,
        text='Run Simulation',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    labels['clingo_status_label'] = Label(
        root=frames['clingo_para_frame'].frame,
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='n',
        columnspan=4,
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#000000',
        background_color='#000000',
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

def build_clingo_help_frame():
    frames['clingo_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("help_texts/clingo_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['clingo_help'] = Text(
        root=frames['clingo_help_frame'].frame,
        width=frames['clingo_help_frame'].width,
        height=frames['clingo_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['clingo_help_frame'].frame.rowconfigure(0, weight=1)
    frames['clingo_help_frame'].frame.columnconfigure(0, weight=1)
    frames['clingo_help_frame'].frame.grid_propagate(False)

def toggle_main_menu_help():
    if 'main_menu_help_frame' in frames:
        frames['main_menu_help_frame'].toggle_visibility()
    else:
        build_main_menu_help_frame()

def toggle_clingo_help():
    if 'clingo_help_frame' in frames:
        frames['clingo_help_frame'].toggle_visibility()
        frames['clingo_help_frame'].frame.rowconfigure(0, weight=1)
        frames['clingo_help_frame'].frame.columnconfigure(0, weight=1)
        frames['clingo_help_frame'].frame.grid_propagate(False)
    else:
        build_clingo_help_frame()

def switch_main_to_random_gen():
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
    global build_mode, user_params_backup, \
        current_builder_backup_array, current_builder_backup_df

    user_params_backup = user_params.copy()
    current_builder_backup_array = current_array.copy()
    current_builder_backup_df = current_df.copy()

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

    build_builder_para_frame()

def switch_main_to_clingo_para():
    if 'main_menu_frame' in frames:
        frames['main_menu_frame'].destroy_frame()
        del frames['main_menu_frame']
    if 'main_menu_help_frame' in frames:
        frames['main_menu_help_frame'].destroy_frame()
        del frames['main_menu_help_frame']

    build_clingo_para_frame()

def switch_clingo_para_to_main():
    if save_clingo_params() == -1:
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
    if save_clingo_params() == -1:
        return

    labels['clingo_status_label'].label.config(
        text='...Simulating...',
        fg='#00FF00',
    )
    frames['clingo_para_frame'].frame.update()

    if len(current_df) == 0:
        labels['clingo_status_label'].label.config(
            text='No trains on environment',
            fg='#FF0000',
        )
        frames['clingo_para_frame'].frame.update()
        return

    sim_result = run_simulation()

    if sim_result:
        labels['clingo_status_label'].label.config(
            text=clingo_err_dict[sim_result],
            fg='#FF0000',
        )
        frames['clingo_para_frame'].frame.update()
        return
    else:
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
        create_gif()
        create_result_menu()

def reload_main_env_viewer():
    if 'main_menu_env_viewer_frame' in frames:
        frames['main_menu_env_viewer_frame'].destroy_frame()
        del frames['main_menu_env_viewer_frame']

    build_main_menu_env_viewer()

def load_lp_files():
    files = filedialog.askopenfilenames(
        title="Select LP Files",
        initialdir='asp',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    user_params['lpFiles'] = list(files)
    displaytext = "\n".join(files)

    labels['clingo_paths_label'].label.config(text=displaytext)

def save_clingo_params():
    err_count = 0

    for field in entry_fields:
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key not in ['answer', 'clingo']:
            continue

        data = entry_fields[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'clingo':
                data = data
            else:
                data = int(data)

            labels[f'{key}_error_label'].hide_label()
        except Exception as e:
            err = type(e)
            labels[f'{key}_error_label'].label.config(text=err_dict[key][err])
            labels[f'{key}_error_label'].place_label()
            if err not in err_dict[key]:
                print(e)
                print(err)
                print(data)
            err_count += 1

        if type(data) is not str or key == 'clingo':
            user_params[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_clingo_params():
    for field in entry_fields:
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
        labels['clingo_paths_label'].label.config(text=displaytext)





# exit confirmation

def open_exit_confirmation_frame(event=None):
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
        background_color='#000000',
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
        font=('Arial', int(font_scale * 50), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    frames['exit_confirmation_frame'].frame.rowconfigure(0, weight=2)
    frames['exit_confirmation_frame'].frame.rowconfigure(1, weight=3)
    frames['exit_confirmation_frame'].frame.columnconfigure((0, 1), weight=1)
    frames['exit_confirmation_frame'].frame.grid_propagate(False)

def exit_gui():
    save_user_data_to_file()
    delete_tmp_lp()
    delete_tmp_png()

    windows['flatland_window'].close_window()

def close_exit_confirmation_frame():
    if 'exit_confirmation_frame' in frames:
        frames['exit_confirmation_frame'].destroy_frame()
        del frames['exit_confirmation_frame']





# random generation

def random_gen_change_to_start_or_main():
    if last_menu == 'start':
        random_gen_para_to_start()
    else:
        random_gen_para_to_main()

def random_gen_para_to_start():
    if 'random_gen_para_frame' in frames:
        frames['random_gen_para_frame'].destroy_frame()
        del frames['random_gen_para_frame']

    create_start_menu()

def random_gen_para_to_main():
    if 'random_gen_para_frame' in frames:
        frames['random_gen_para_frame'].destroy_frame()
        del frames['random_gen_para_frame']
    if 'random_gen_para_help_frame' in frames:
        frames['random_gen_para_help_frame'].destroy_frame()
        del frames['random_gen_para_help_frame']

    create_main_menu()

def build_random_gen_para_frame():
    frames['random_gen_para_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.7,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_random_gen_para_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['back_button'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 1),
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

    labels['spacing_err_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(0, 4),
        padding=(0, 0),
        sticky='nw',
        text='needs dictionary float: float,... , 0 <= float <= 1',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#000000',
        visibility=True,
    )

    labels['rows_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment rows:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['rows_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(1, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['cols_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment columns:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['cols_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(2, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['agents_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text='Number of agents:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['agents_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(3, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['cities_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of cities:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['cities_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(4, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['seed_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text='Seed:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['seed_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(5, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['grid_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text='Use grid mode:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['grid_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(6, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["grid"]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['grid_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(6, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['intercity_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of rails between cities:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['intercity_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(7, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["intercity"]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['intercity_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(7, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['incity_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. number of rail pairs in cities:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['incity_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(8, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["incity"]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['incity_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(8, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['remove_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(9, 2),
        padding=(0, 0),
        sticky='nw',
        text='Remove agents on arrival:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['remove_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(9, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["remove"]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['remove_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(9, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['speed_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(10, 2),
        padding=(0, 0),
        sticky='nw',
        text='Speed ratio map for trains:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['speed_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(10, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {str(default_params["speed"]).strip("{}")}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['speed_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(10, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['malfunction_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(11, 2),
        padding=(0, 0),
        sticky='nw',
        text='Malfunction rate:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['malfunction_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(11, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["malfunction"][0]}/'
             f'{default_params["malfunction"][1]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['malfunction_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(11, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['min_duration_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(12, 2),
        padding=(0, 0),
        sticky='nw',
        text='Min. duration for malfunctions:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['min_duration_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(12, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["min"]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['min_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(12, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['max_duration_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(13, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. duration for malfunctions:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['max_duration_entry'] = EntryField(
        root=frames['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(13, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["max"]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['max_error_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(13, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    buttons['advanced_options'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(14, 2),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_toggle_advanced_para_options,
        text='Advanced Options',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['generate_button'] = Button(
        root=frames['random_gen_para_frame'].frame,
        width=9,
        height=1,
        grid_pos=(14, 3),
        padding=(0, 0),
        sticky='nw',
        command=random_gen_para_to_env,
        text='Generate',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    labels['random_gen_status_label'] = Label(
        root=frames['random_gen_para_frame'].frame,
        grid_pos=(14, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#000000',
        background_color='#000000',
        visibility=True,
    )

    frames['random_gen_para_frame'].frame.rowconfigure(0, weight=1)
    frames['random_gen_para_frame'].frame.rowconfigure(
        tuple(range(1,15)), weight=2
    )
    frames['random_gen_para_frame'].frame.columnconfigure(0, weight=1)
    frames['random_gen_para_frame'].frame.columnconfigure(1, weight=1)
    frames['random_gen_para_frame'].frame.columnconfigure(2, weight=2)
    frames['random_gen_para_frame'].frame.columnconfigure(3, weight=2)
    frames['random_gen_para_frame'].frame.columnconfigure(4, weight=2)

    frames['random_gen_para_frame'].frame.grid_propagate(False)

    load_random_gen_env_params()

def build_random_gen_para_help_frame():
    frames['random_gen_para_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.3,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("help_texts/random_gen_para_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['random_gen_para_help'] = Text(
        root=frames['random_gen_para_help_frame'].frame,
        width=frames['random_gen_para_help_frame'].width,
        height=frames['random_gen_para_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['random_gen_para_help_frame'].frame.rowconfigure(0, weight=1)
    frames['random_gen_para_help_frame'].frame.columnconfigure(0, weight=1)
    frames['random_gen_para_help_frame'].frame.grid_propagate(False)

def random_gen_para_to_env():
    global current_img, current_df, current_array

    if save_random_gen_env_params() == -1:
        return

    labels['random_gen_status_label'].label.config(
        text='...Generating...',
        fg='#00FF00',
    )
    frames['random_gen_para_frame'].frame.update()

    try:
        tracks, trains = gen_env(user_params)
    except ValueError as e:
        labels['random_gen_status_label'].label.config(
            text='Cannot fit more than one city in this map',
            fg='#FF0000',
        )
        frames['random_gen_para_frame'].frame.update()
        print(f'gen_env in random_gen_para_to_env returned a ValueError: {e}')
        return

    if tracks == -1:
        labels['random_gen_status_label'].label.config(
            text='No environment generated.\n'
                 'Please restart the program.',
            fg='#FF0000',
            anchor="w",
            justify="left",
        )
        frames['random_gen_para_frame'].frame.update()
        return

    if len(trains):
        start_pos = list(zip(trains['x'], trains['y']))
        end_pos = list(zip(trains['x_end'], trains['y_end']))

        current_df = pd.DataFrame({
            'start_pos': start_pos,
            'dir': trains['dir'],
            'end_pos': end_pos,
            'e_dep': trains['e_dep'],
            'l_arr': trains['l_arr']
        })
    else:
        current_df = pd.DataFrame(
            columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
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

    build_random_gen_env_viewer()
    build_random_gen_env_menu()

def build_random_gen_env_viewer():
    frames['random_gen_env_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    canvases['gen_env_viewer_canvas'] = EnvCanvas(
        root=frames['random_gen_env_viewer_frame'].frame,
        width=frames['random_gen_env_viewer_frame'].width,
        height=frames['random_gen_env_viewer_frame'].height,
        x=frames['random_gen_env_viewer_frame'].width * 0,
        y=frames['random_gen_env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image=current_img,
        rows=user_params['rows'],
        cols=user_params['cols'],
    )

def build_random_gen_env_menu():
    frames['random_gen_env_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
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
        text='Return To Main Menu',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    current_df_to_env_text()
    with open("data/current_df.txt", "r") as file:
        displaytext = file.read()

    texts['random_gen_env_trains'] = Text(
        root=frames['random_gen_env_menu_frame'].frame,
        width=frames['random_gen_env_menu_frame'].width,
        height=frames['random_gen_env_menu_frame'].height * 0.75,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=displaytext,
        font=("Courier", int(font_scale * 15)),
        wrap='word',
        foreground_color='#FFFFFF',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['random_gen_env_menu_frame'].frame.rowconfigure(0, weight=15)
    frames['random_gen_env_menu_frame'].frame.rowconfigure(1, weight=1)
    frames['random_gen_env_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['random_gen_env_menu_frame'].frame.grid_propagate(False)

def random_gen_toggle_advanced_para_options():
    labels['grid_label'].toggle_visibility()
    entry_fields['grid_entry'].toggle_visibility()
    labels['intercity_label'].toggle_visibility()
    entry_fields['intercity_entry'].toggle_visibility()
    labels['incity_label'].toggle_visibility()
    entry_fields['incity_entry'].toggle_visibility()
    labels['remove_label'].toggle_visibility()
    entry_fields['remove_entry'].toggle_visibility()
    labels['speed_label'].toggle_visibility()
    entry_fields['speed_entry'].toggle_visibility()
    labels['malfunction_label'].toggle_visibility()
    entry_fields['malfunction_entry'].toggle_visibility()
    labels['min_duration_label'].toggle_visibility()
    entry_fields['min_duration_entry'].toggle_visibility()
    labels['max_duration_label'].toggle_visibility()
    entry_fields['max_duration_entry'].toggle_visibility()
    return

def toggle_random_gen_para_help():
    if 'random_gen_para_help_frame' in frames:
        frames['random_gen_para_help_frame'].toggle_visibility()
        frames['random_gen_para_help_frame'].frame.rowconfigure(0, weight=1)
        frames['random_gen_para_help_frame'].frame.columnconfigure(0, weight=1)
        frames['random_gen_para_help_frame'].frame.grid_propagate(False)
    else:
        build_random_gen_para_help_frame()

def switch_random_gen_to_main():
    if 'random_gen_env_viewer_frame' in frames:
        frames['random_gen_env_viewer_frame'].destroy_frame()
        del frames['random_gen_env_viewer_frame']
    if 'random_gen_env_menu_frame' in frames:
        frames['random_gen_env_menu_frame'].destroy_frame()
        del frames['random_gen_env_menu_frame']

    create_main_menu()

def save_random_gen_env_params():
    def str_to_bool(s):
        if isinstance(s, str):
            s = s.lower()
            if s == "true" or s == 'tru' or s == 'yes' or s == 'y':
                return True
            elif s == "false" or s == 'no' or s == 'n':
                return False
        raise ValueError(f"Invalid boolean string: {s}")

    err_count = 0

    for field in entry_fields:
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key in ['answer', 'clingo', 'lpFiles']:
            continue

        data = entry_fields[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'grid' or key == 'remove':
                data = str_to_bool(data)
            elif key == 'speed':
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

            labels[f'{key}_error_label'].hide_label()
        except Exception as e:
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

        # input constraints
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


        if key=='speed':
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

        if type(data) is not str:
            user_params[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_random_gen_env_params():
    for field in entry_fields:
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key in ['answer', 'clingo', 'lpFiles']:
            continue
        elif user_params[key] is None:
            continue
        elif key == 'speed':
            string = ''
            for k, v in user_params['speed'].items():
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
    global user_params, current_array, current_df

    user_params = user_params_backup.copy()

    # if build_mode == 'build':
    #     current_array = current_builder_backup_array.copy()
    #     current_df = current_builder_backup_df.copy()
    # else:
    current_array = current_modify_backup_array.copy()
    current_df = current_modify_backup_df.copy()

    if last_menu == 'start':
        builder_para_to_start()
    else:
        builder_para_to_main()

def open_builder_discard_changes_frame():
    frames['builder_discard_changes_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        columnspan=2,
        sticky='nesw',
        background_color='#000000',
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
        font=('Arial', int(font_scale * 50), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    frames['builder_discard_changes_frame'].frame.rowconfigure(0, weight=2)
    frames['builder_discard_changes_frame'].frame.rowconfigure(1, weight=3)
    frames['builder_discard_changes_frame'].frame.columnconfigure((0, 1), weight=1)
    frames['builder_discard_changes_frame'].frame.grid_propagate(False)

def builder_para_to_start():
    global build_mode

    build_mode = None

    if 'builder_para_frame' in frames:
        frames['builder_para_frame'].destroy_frame()
        del frames['builder_para_frame']

    create_start_menu()

def builder_para_to_main():
    global build_mode

    build_mode = None

    if 'builder_para_frame' in frames:
        frames['builder_para_frame'].destroy_frame()
        del frames['builder_para_frame']
    if 'builder_para_help_frame' in frames:
        frames['builder_para_help_frame'].destroy_frame()
        del frames['builder_para_help_frame']

    create_main_menu()

def build_builder_para_frame():
    frames['builder_para_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.7,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['builder_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_builder_para_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['back_button'] = Button(
        root=frames['builder_para_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nw',
        command=open_builder_discard_changes_frame,
        text='<',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    labels['spacing_err_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(0, 4),
        padding=(0, 0),
        sticky='nw',
        text='needs dictionary float: float,... , 0 <= float <= 1',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#000000',
        visibility=True,
    )

    labels['rows_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(1, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment rows:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['rows_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(1, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['cols_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(2, 2),
        padding=(0, 0),
        sticky='nw',
        text='Environment columns:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    labels['cols_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(2, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['remove_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text='Remove agents on arrival:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['remove_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {default_params["remove"]}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['remove_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(3, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['speed_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        text='Speed ratio map for trains:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    entry_fields['speed_entry'] = EntryField(
        root=frames['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(4, 3),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {str(default_params["speed"]).strip("{}")}',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['speed_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(4, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['malfunction_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text='Malfunction rate:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['malfunction_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(5, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['min_duration_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text='Min. duration for malfunctions:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['min_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(6, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    labels['max_duration_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text='Max. duration for malfunctions:',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    labels['max_error_label'] = Label(
        root=frames['builder_para_frame'].frame,
        grid_pos=(7, 4),
        padding=(0, 0),
        sticky='nw',
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        visibility=False,
    )

    buttons['advanced_options'] = Button(
        root=frames['builder_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        command=builder_toggle_advanced_para_options,
        text='Advanced Options',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['build_button'] = Button(
        root=frames['builder_para_frame'].frame,
        width=9,
        height=1,
        grid_pos=(8, 3),
        padding=(0, 0),
        sticky='nw',
        command=builder_para_to_track_grid,
        text='Build' if build_mode == 'build' else 'Modify',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    frames['builder_para_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_para_frame'].frame.rowconfigure(
        tuple(range(1,9)), weight=2
    )
    frames['builder_para_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_para_frame'].frame.columnconfigure(1, weight=1)
    frames['builder_para_frame'].frame.columnconfigure(2, weight=2)
    frames['builder_para_frame'].frame.columnconfigure(3, weight=2)
    frames['builder_para_frame'].frame.columnconfigure(4, weight=2)
    frames['builder_para_frame'].frame.grid_propagate(False)

    load_builder_env_params()

def build_builder_para_help_frame():
    frames['builder_para_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.3,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("help_texts/builder_para_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['builder_para_help_text'] = Text(
        root=frames['builder_para_help_frame'].frame,
        width=frames['builder_para_help_frame'].width,
        height=frames['builder_para_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_para_help_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_para_help_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_para_help_frame'].frame.grid_propagate(False)

def toggle_builder_para_help():
    if 'builder_para_help_frame' in frames:
        frames['builder_para_help_frame'].toggle_visibility()
        frames['builder_para_help_frame'].frame.rowconfigure(0, weight=1)
        frames['builder_para_help_frame'].frame.columnconfigure(0, weight=1)
        frames['builder_para_help_frame'].frame.grid_propagate(False)
    else:
        build_builder_para_help_frame()

def builder_para_to_track_grid():
    global current_array, current_df, \
        current_builder_backup_array, current_builder_backup_df, \
        current_modify_backup_array, current_modify_backup_df

    if save_builder_env_params() == -1:
        return

    if build_mode == 'modify':
        current_modify_backup_array = current_array.copy()
        current_modify_backup_df = current_df.copy()

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
        current_array = np.zeros((3, rows, cols), dtype=int)
        current_df = pd.DataFrame(
            columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
        )
    else:
        current_rows, current_cols = current_array.shape[1:3]

        if (rows,cols) != (current_rows,current_cols):
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

    build_track_builder_menu_frame()
    build_builder_grid_frame()

def builder_track_grid_to_para():
    if 'track_builder_menu_frame' in frames:
        frames['track_builder_menu_frame'].destroy_frame()
        del frames['track_builder_menu_frame']
    if 'builder_grid_frame' in frames:
        frames['builder_grid_frame'].destroy_frame()
        del frames['builder_grid_frame']
    if 'builder_track_help_frame' in frames:
        frames['builder_track_help_frame'].destroy_frame()
        del frames['builder_track_help_frame']

    build_builder_para_frame()

def build_builder_grid_frame():
    frames['builder_grid_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nsw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    canvases['builder_grid_canvas'] = BuildCanvas(
        root=frames['builder_grid_frame'].frame,
        width=frames['builder_grid_frame'].width,
        height=frames['builder_grid_frame'].height,
        x=frames['builder_grid_frame'].width * 0,
        y=frames['builder_grid_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        array=current_array,
        train_data=current_df,
    )

    frames['builder_grid_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_grid_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_grid_frame'].frame.grid_propagate(False)

def build_track_builder_menu_frame():
    frames['track_builder_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_builder_track_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['back_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 1),
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

    buttons['horizontal_straight_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(1025),
        image='data/png/Gleis_horizontal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['vertical_straight_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 3),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(32800),
        image='data/png/Gleis_vertikal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['corner_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 6),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(2064),
        image='data/png/Gleis_kurve_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['corner_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(72),
        image='data/png/Gleis_kurve_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['corner_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(16386),
        image='data/png/Gleis_kurve_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['corner_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 9),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(4608),
        image='data/png/Gleis_kurve_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_hor_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(3089),
        image='data/png/Weiche_horizontal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_hor_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 3),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(1097),
        image='data/png/Weiche_horizontal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_hor_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 4),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(17411),
        image='data/png/Weiche_horizontal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_hor_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(5633),
        image='data/png/Weiche_horizontal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_ver_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 6),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(34864),
        image='data/png/Weiche_vertikal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_ver_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(32872),
        image='data/png/Weiche_vertikal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_ver_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(49186),
        image='data/png/Weiche_vertikal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['switch_ver_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(2, 9),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(37408),
        image='data/png/Weiche_vertikal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['diamond_crossing_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(3, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(33825),
        image='data/png/Gleis_Diamond_Crossing.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['single_slip_top_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(3, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(35889),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    buttons['single_slip_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(3, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(33897),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    buttons['single_slip_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(3, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(50211),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    buttons['single_slip_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(3, 9),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(38433),
        image='data/png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    buttons['double_slip_top_left_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(4, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(52275),
        image='data/png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    buttons['double_slip_bottom_left_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(4, 3),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(38505),
        image='data/png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    buttons['symmetrical_top_left_top_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(4, 6),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(2136),
        image='data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    buttons['symmetrical_top_right_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(4, 7),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(16458),
        image='data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    buttons['symmetrical_bottom_left_bottom_right_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(4, 8),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(20994),
        image='data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    buttons['symmetrical_top_left_bottom_left_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(4, 9),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(6672),
        image='data/png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    buttons['delete_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(5, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(0),
        image='data/png/eraser.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    buttons['reset_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 6),
        padding=(0, 0),
        columnspan=2,
        command=lambda: open_reset_frame(frames['track_builder_menu_frame']),
        text='RESET',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['train_builder_button'] = Button(
        root=frames['track_builder_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(6, 2),
        padding=(0, 0),
        columnspan=4,
        command=builder_track_to_train,
        text='Trains',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    frames['track_builder_menu_frame'].frame.rowconfigure(0, weight=1)
    frames['track_builder_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['track_builder_menu_frame'].frame.columnconfigure(1, weight=1)
    frames['track_builder_menu_frame'].frame.rowconfigure(
        tuple(range(1,7)), weight=2
    )
    frames['track_builder_menu_frame'].frame.columnconfigure(
        tuple(range(2,10)), weight=2
    )
    frames['track_builder_menu_frame'].frame.grid_propagate(False)

def build_builder_track_help_frame():
    frames['builder_track_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("help_texts/builder_track_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['builder_track_help_text'] = Text(
        root=frames['builder_track_help_frame'].frame,
        width=frames['builder_track_help_frame'].width,
        height=frames['builder_track_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_track_help_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_track_help_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_track_help_frame'].frame.grid_propagate(False)

def toggle_builder_track_help():
    if 'builder_track_help_frame' in frames:
        frames['builder_track_help_frame'].toggle_visibility()
        frames['builder_track_help_frame'].frame.rowconfigure(0, weight=1)
        frames['builder_track_help_frame'].frame.columnconfigure(0, weight=1)
        frames['builder_track_help_frame'].frame.grid_propagate(False)
    else:
        build_builder_track_help_frame()

def builder_track_to_train():
    if 'track_builder_menu_frame' in frames:
        frames['track_builder_menu_frame'].destroy_frame()
        del frames['track_builder_menu_frame']
    if 'builder_track_help_frame' in frames:
        frames['builder_track_help_frame'].destroy_frame()
        del frames['builder_track_help_frame']

    canvases['builder_grid_canvas'].current_selection = None

    build_train_builder_menu_frame()

def builder_train_to_track():
    if 'train_builder_menu_frame' in frames:
        frames['train_builder_menu_frame'].destroy_frame()
        del frames['train_builder_menu_frame']
    if 'builder_train_help_frame' in frames:
        frames['builder_train_help_frame'].destroy_frame()
        del frames['builder_train_help_frame']

    canvases['builder_grid_canvas'].current_selection = None

    build_track_builder_menu_frame()

def build_train_builder_menu_frame():
    frames['train_builder_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_builder_train_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['back_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 1),
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

    buttons['train_north_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 2),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(1),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    buttons['train_east_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 3),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(2),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    buttons['train_south_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 4),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(3),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    buttons['train_west_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=int(font_scale * 80),
        height=int(font_scale * 80),
        grid_pos=(1, 5),
        padding=(0, 0),
        command=lambda: canvases['builder_grid_canvas'].select(4),
        image='data/png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    buttons['reset_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=10,
        height=1,
        grid_pos=(1, 7),
        padding=(0, 0),
        command=lambda: open_reset_frame(frames['train_builder_menu_frame']),
        text='RESET',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    frames['train_config_list_canvas_frame'] = Frame(
        root=frames['train_builder_menu_frame'].frame,
        width=frames['train_builder_menu_frame'].width * 0.75,
        height=frames['train_builder_menu_frame'].height * 0.6,
        grid_pos=(2, 2),
        padding=(0, 0),
        columnspan=6,
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['finish_building_button'] = Button(
        root=frames['train_builder_menu_frame'].frame,
        width=14,
        height=1,
        grid_pos=(3, 2),
        padding=(0, 0),
        columnspan=3,
        command=builder_train_grid_to_env,
        text='Finish Building' if build_mode == 'build' else 'Finish Modifying',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    labels['builder_status_label'] = Label(
        root=frames['train_builder_menu_frame'].frame,
        grid_pos=(3, 6),
        padding=(0, 0),
        sticky='w',
        columnspan=4,
        text='',
        font=('Arial', int(font_scale * base_font * error_scale), 'bold'),
        foreground_color='#000000',
        background_color='#000000',
        visibility=True,
    )

    frames['train_builder_menu_frame'].frame.rowconfigure(0, weight=1)
    frames['train_builder_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['train_builder_menu_frame'].frame.columnconfigure(1, weight=1)
    frames['train_builder_menu_frame'].frame.rowconfigure(1, weight=2)
    frames['train_builder_menu_frame'].frame.columnconfigure(
        tuple(range(2,8)), weight=2
    )
    frames['train_builder_menu_frame'].frame.rowconfigure((2, 3), weight=2)
    frames['train_builder_menu_frame'].frame.grid_propagate(False)

    canvases['train_config_list'] = TrainListCanvas(
        root=frames['train_config_list_canvas_frame'].frame,
        width=frames['train_config_list_canvas_frame'].width,
        height=frames['train_config_list_canvas_frame'].height,
        x=frames['train_config_list_canvas_frame'].width * 0,
        y=frames['train_config_list_canvas_frame'].height * 0,
        background_color='#000000',
        border_width=0,
        grid=canvases['builder_grid_canvas'],
        train_data=current_df,
        outer_frame=frames['train_builder_menu_frame'].frame,
        base_font=base_font,
        font_scale=font_scale,
    )
    canvases['builder_grid_canvas'].train_list = canvases['train_config_list']

def build_builder_train_help_frame():
    frames['builder_train_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("help_texts/builder_train_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['builder_train_help_text'] = Text(
        root=frames['builder_train_help_frame'].frame,
        width=frames['builder_train_help_frame'].width,
        height=frames['builder_train_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_train_help_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_train_help_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_train_help_frame'].frame.grid_propagate(False)

def toggle_builder_train_help():
    if 'builder_train_help_frame' in frames:
        frames['builder_train_help_frame'].toggle_visibility()
        frames['builder_train_help_frame'].frame.rowconfigure(0, weight=1)
        frames['builder_train_help_frame'].frame.columnconfigure(0, weight=1)
        frames['builder_train_help_frame'].frame.grid_propagate(False)
    else:
        build_builder_train_help_frame()

def builder_train_grid_to_env():
    global current_img, current_builder_backup_array, current_builder_backup_df, \
        current_modify_backup_array, current_modify_backup_df

    if len(current_df) == 0:
        labels['builder_status_label'].label.config(
            text='No Trains Placed',
            fg='#FF0000',
        )
        frames['train_builder_menu_frame'].frame.update()
        return
    else:
        labels['builder_status_label'].label.config(
            text='...Building...',
            fg='#00FF00',
        )
        frames['train_builder_menu_frame'].frame.update()

    tracks = current_array[0]
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
        "l_arr": current_df['l_arr']
    })

    user_params['agents'] = len(trains)

    env = create_custom_env(tracks, trains, user_params)
    os.makedirs("data", exist_ok=True)
    if save_png(env, "data/running_tmp.png") == -1:
        labels['builder_status_label'].label.config(
            text='Flatland failed to create image.\n'
                 'Please restart the program.',
            fg='#FF0000',
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
    frames['builder_env_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    canvases['builder_env_viewer_canvas'] = EnvCanvas(
        root=frames['builder_env_viewer_frame'].frame,
        width=frames['builder_env_viewer_frame'].width,
        height=frames['builder_env_viewer_frame'].height,
        x=frames['builder_env_viewer_frame'].width * 0,
        y=frames['builder_env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image=current_img,
        rows=user_params['rows'],
        cols=user_params['cols'],
    )

    frames['builder_env_viewer_frame'].frame.rowconfigure(0, weight=1)
    frames['builder_env_viewer_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_env_viewer_frame'].frame.grid_propagate(False)

def build_builder_env_menu():
    frames['builder_env_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
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
        text='Return To Main Menu',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    current_df_to_env_text()
    with open("data/current_df.txt", "r") as file:
        displaytext = file.read()

    texts['builder_env_trains'] = Text(
        root=frames['builder_env_menu_frame'].frame,
        width=frames['builder_env_menu_frame'].width,
        height=frames['builder_env_menu_frame'].height * 0.75,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        text=displaytext,
        font=("Courier", int(font_scale * 15)),
        wrap='word',
        foreground_color='#FFFFFF',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['builder_env_menu_frame'].frame.rowconfigure(0, weight=15)
    frames['builder_env_menu_frame'].frame.rowconfigure(1, weight=1)
    frames['builder_env_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['builder_env_menu_frame'].frame.grid_propagate(False)

def builder_toggle_advanced_para_options():
    labels['remove_label'].toggle_visibility()
    entry_fields['remove_entry'].toggle_visibility()
    labels['speed_label'].toggle_visibility()
    entry_fields['speed_entry'].toggle_visibility()
    labels['malfunction_label'].toggle_visibility()
    entry_fields['malfunction_entry'].toggle_visibility()
    labels['min_duration_label'].toggle_visibility()
    entry_fields['min_duration_entry'].toggle_visibility()
    labels['max_duration_label'].toggle_visibility()
    entry_fields['max_duration_entry'].toggle_visibility()
    return

def switch_builder_to_main():
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
    def str_to_bool(s):
        if isinstance(s, str):
            s = s.lower()
            if s == "true" or s == 'tru' or s == 'yes' or s == 'y':
                return True
            elif s == "false" or s == 'no' or s == 'n':
                return False
        raise ValueError(f"Invalid boolean string: {s}")

    err_count = 0

    for field in entry_fields:
        key = field.split('_')[0]
        if key not in default_params:
            continue
        if key in ['answer', 'clingo', 'lpFiles', 'agents', 'cities', 'seed',
                   'grid', 'intercity', 'incity']:
            continue

        data = entry_fields[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'grid' or key == 'remove':
                data = str_to_bool(data)
            elif key == 'speed':
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

            labels[f'{key}_error_label'].hide_label()
        except Exception as e:
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

        # input constraints
        if key=='malfunction' and data[1] == 0:
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

        if key=='speed':
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

        if type(data) is not str:
            user_params[key] = data

    if err_count:
        return -1
    else:
        return 0

def load_builder_env_params():
    for field in entry_fields:
        key = field.split('_')[0]
        if key not in default_params:
            continue
        elif key in ['answer', 'clingo', 'lpFiles', 'agents', 'cities', 'seed',
                     'grid', 'intercity', 'incity']:
            continue
        elif user_params[key] is None:
            continue
        elif key == 'speed':
            string = ''
            for k, v in user_params['speed'].items():
                string = string + f'{k}: {v}, '
            entry_fields[field].insert_string(string[:-2])
        elif key == 'malfunction':
            entry_fields[field].insert_string(
                f'{user_params["malfunction"][0]}/'
                f'{user_params["malfunction"][1]}'
            )
        else:
            entry_fields[field].insert_string(str(user_params[key]))

def open_reset_frame(parent_frame):
    frames['reset_frame'] = Frame(
        root=parent_frame.root,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
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
        font=('Arial', int(font_scale * 40), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
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
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    frames['reset_frame'].frame.rowconfigure(0, weight=2)
    frames['reset_frame'].frame.rowconfigure(1, weight=3)
    frames['reset_frame'].frame.columnconfigure((0, 1), weight=1)
    frames['reset_frame'].frame.grid_propagate(False)

def reset_builder_grid():
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
    build_result_env_viewer()
    build_result_menu()

def build_result_env_viewer():
    frames['result_viewer_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    canvases['result_viewer_canvas'] = ResultCanvas(
        root=frames['result_viewer_frame'].frame,
        width=frames['result_viewer_frame'].width,
        height=frames['result_viewer_frame'].height,
        x=frames['result_viewer_frame'].width * 0,
        y=frames['result_viewer_frame'].height * 0,
        background_color='#333333',
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
    frames['result_menu_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 1),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    buttons['help_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=2,
        height=1,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nw',
        command=toggle_result_help,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['show_time_table_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(1, 1),
        padding=(0, 0),
        command=toggle_result_timetable,
        text='Toggle Time Table',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    buttons['show_gif_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(2, 1),
        padding=(0, 0),
        command=toggle_result_gif,
        text='Toggle GIF',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    frames['path_list_canvas_frame'] = Frame(
        frames['result_menu_frame'].frame,
        width=frames['result_menu_frame'].width * 0.5,
        height=frames['result_menu_frame'].height * 0.25,
        grid_pos=(4,1),
        padding=(0,0),
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    buttons['return_to_menu_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(5, 1),
        padding=(0, 0),
        command=switch_result_to_main,
        text='Return To Main Menu',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    frames['result_menu_frame'].frame.rowconfigure(0, weight=1)
    frames['result_menu_frame'].frame.columnconfigure(0, weight=1)
    frames['result_menu_frame'].frame.rowconfigure((1, 2, 3, 4, 5), weight=2)
    frames['result_menu_frame'].frame.columnconfigure(1, weight=2)
    frames['result_menu_frame'].frame.grid_propagate(False)

    canvases['path_list_canvas'] = PathListCanvas(
        root=frames['path_list_canvas_frame'].frame,
        width=frames['path_list_canvas_frame'].width,
        height=frames['path_list_canvas_frame'].height,
        x=frames['path_list_canvas_frame'].width * 0,
        y=frames['path_list_canvas_frame'].height * 0,
        background_color='#000000',
        border_width=0,
        train_data=current_df,
        grid=canvases['result_viewer_canvas'],
        base_font=base_font,
        font_scale=font_scale,
    )

    buttons['toggle_all_paths_button'] = Button(
        root=frames['result_menu_frame'].frame,
        width=20,
        height=1,
        grid_pos=(3, 1),
        padding=(0, 0),
        command=toggle_all_paths,
        text='Toggle All Paths',
        font=('Arial', int(font_scale * base_font), 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

def build_result_help_frame():
    frames['result_help_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("help_texts/result_help_text.txt", "r") as file:
        help_displaytext = file.read()

    texts['result_help_text'] = Text(
        root=frames['result_help_frame'].frame,
        width=frames['result_help_frame'].width,
        height=frames['result_help_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=help_displaytext,
        font=("Courier", int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['result_help_frame'].frame.rowconfigure(0, weight=1)
    frames['result_help_frame'].frame.columnconfigure(0, weight=1)
    frames['result_help_frame'].frame.grid_propagate(False)

def build_result_timetable_frame():
    frames['result_timetable_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    with open("data/current_df.txt", "r") as file:
        displaytext = file.read()

    texts['result_timetable_text'] = Text(
        root=frames['result_timetable_frame'].frame,
        width=frames['result_timetable_frame'].width,
        height=frames['result_timetable_frame'].height,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nes',
        text=displaytext,
        font=('Courier', int(font_scale * base_font)),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )

    frames['result_timetable_frame'].frame.rowconfigure(0, weight=1)
    frames['result_timetable_frame'].frame.columnconfigure(0, weight=1)
    frames['result_timetable_frame'].frame.grid_propagate(False)

def build_result_gif_frame():
    frames['result_gif_frame'] = Frame(
        root=windows['flatland_window'].window,
        width=screenwidth * 0.5,
        height=screenheight,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    pictures['title_gif'] = GIF(
        root=frames['result_gif_frame'].frame,
        width=frames['result_gif_frame'].width * 0.99,
        height=frames['result_gif_frame'].height * 0.4,
        grid_pos=(0, 0),
        padding=(0, 0),
        sticky='nesw',
        gif=current_gif,
        background_color='#000000',
        visibility=True,
    )

    frames['result_gif_frame'].frame.rowconfigure(0, weight=1)
    frames['result_gif_frame'].frame.columnconfigure(0, weight=1)
    frames['result_gif_frame'].frame.grid_propagate(False)

def toggle_all_paths():
    if ('result_timetable_frame' in frames and
            frames['result_timetable_frame'].visibility):
        frames['result_timetable_frame'].toggle_visibility()
        
    if ('result_gif_frame' in frames and
            frames['result_gif_frame'].visibility):
        frames['result_gif_frame'].toggle_visibility()

    if ('result_help_frame' in frames and
            frames['result_help_frame'].visibility):
        frames['result_help_frame'].toggle_visibility()
        
    canvases['path_list_canvas'].toggle_all_paths()

def toggle_result_help():
    if ('result_timetable_frame' in frames and 
            frames['result_timetable_frame'].visibility):
        frames['result_timetable_frame'].toggle_visibility()
        
    if ('result_gif_frame' in frames and 
            frames['result_gif_frame'].visibility):
        frames['result_gif_frame'].toggle_visibility()
        
    if 'result_help_frame' in frames:
        frames['result_help_frame'].toggle_visibility()
        frames['result_help_frame'].frame.rowconfigure(0, weight=1)
        frames['result_help_frame'].frame.columnconfigure(0, weight=1)
        frames['result_help_frame'].frame.grid_propagate(False)
    else:
        build_result_help_frame()

def toggle_result_timetable():
    if ('result_gif_frame' in frames and 
            frames['result_gif_frame'].visibility):
        frames['result_gif_frame'].toggle_visibility()
        
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
    if ('result_timetable_frame' in frames and 
            frames['result_timetable_frame'].visibility):
        frames['result_timetable_frame'].toggle_visibility()
        
    if ('result_help_frame' in frames and 
            frames['result_help_frame'].visibility):
        frames['result_help_frame'].toggle_visibility()
        
    if 'result_gif_frame' in frames:
        frames['result_gif_frame'].toggle_visibility()
        frames['result_gif_frame'].frame.rowconfigure(0, weight=1)
        frames['result_gif_frame'].frame.columnconfigure(0, weight=1)
        frames['result_gif_frame'].frame.grid_propagate(False)
    else:
        build_result_gif_frame()

def switch_result_to_main():
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

    create_main_menu()





# functions

def create_gif():
    global current_gif

    # TODO: Create gif and save in data folder
    # TODO: Assign path to created gif to current gif like below

    current_gif = 'data/current_gif.gif'

def df_to_timetable_text():
    def format_row(idx, line):
        new_line = (f"| {idx:>8} | {line['e_dep']:>8} | {line['a_dep']:>6} | "
                    f"{line['l_arr']:>6} | {line['a_arr']:>6} |")
        return new_line

    a_dep = (
        current_paths.groupby("trainID")["timestep"]
        .apply(lambda x: x.iloc[0] if len(x) == 1 else x.nsmallest(2).iloc[-1])
        .tolist()
    )
    a_arr = current_paths.groupby("trainID")["timestep"].max().tolist()

    for index, row in current_df.iterrows():
        if row['start_pos'] == row['end_pos']:
            a_dep[index] = '--'
            a_arr[index] = '--'

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

    with open('data/current_df.txt', "w") as file:
        file.write(header + "\n")
        file.write(divider + "\n")
        file.writelines(new_row + "\n" for new_row in new_rows)

def current_df_to_env_text():
    def format_row(index, row):
        new_line = (f"| {index:>8} | {str(row['start_pos']):>14} "
                    f"| {row['dir']:^3} | {str(row['end_pos']):>14} "
                    f"| {row['e_dep']:>7} | {row['l_arr']:>7} |")
        return new_line

    header = ("| Train ID | Start Position | Dir |   "
              "End Position |   E Dep |   L Arr |")
    divider = ("|----------|----------------|-----|"
               "----------------|---------|---------|")

    new_rows = [format_row(index, row) for index, row in current_df.iterrows()]

    with open('data/current_df.txt', "w") as file:
        file.write(header + "\n")
        file.write(divider + "\n")
        file.writelines(new_row + "\n" for new_row in new_rows)

def save_user_data_to_file():
    with open('data/user_params.json', 'w') as file:
        json.dump(user_params, file, indent=4)

def load_user_data_from_file():
    global user_params, user_params_backup

    with open('data/user_params.json', 'r') as file:
        data = json.load(file)

    if data['speed'] is not None:
        data['speed'] = {float(k): float(v) for k, v in data['speed'].items()}
    if data['malfunction'] is not None:
        data['malfunction'] = (data['malfunction'][0], data['malfunction'][1])

    user_params = data
    user_params_backup = data

    # use default if no user parameters given
    for key in user_params:
        if user_params[key] is None or user_params[key] == []:
            user_params[key] = default_params[key]

def load_env_from_file():
    global current_array, current_df, current_img

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
            fg='#00FF00',
        )
        frames['start_menu_frame'].frame.update()
    else:
        labels['main_load_status_label'].label.config(
            text='...Loading...',
            fg='#00FF00',
        )
        frames['main_menu_frame'].frame.update()

    tracks, trains = lp_to_env(file)

    if isinstance(tracks, int) or isinstance(trains, int):
        key = tracks if isinstance(tracks, int) else trains
        if last_menu == 'start':
            labels['start_load_status_label'].label.config(
                text=loading_err_dict[key],
                fg='#FF0000',
            )
            frames['start_menu_frame'].frame.update()
        else:
            labels['main_load_status_label'].label.config(
                text=loading_err_dict[key],
                fg='#FF0000',
            )
            frames['main_menu_frame'].frame.update()
        return

    start_pos = list(zip(trains['y'], trains['x']))
    end_pos = list(zip(trains['y_end'], trains['x_end']))

    current_df = pd.DataFrame({
        'start_pos': start_pos,
        'dir': trains['dir'],
        'end_pos': end_pos,
        'e_dep': trains['e_dep'],
        'l_arr': trains['l_arr']
    })


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

    user_params['rows'] = tracks.shape[0]
    user_params['cols'] = tracks.shape[1]
    user_params['agents'] = len(trains)

    env = create_custom_env(tracks, trains, user_params)
    os.makedirs("data", exist_ok=True)
    if save_png(env, "data/running_tmp.png") == -1:
        if last_menu == 'start':
            labels['start_load_status_label'].label.config(
                text='Flatland failed to create image.\n'
                     'Please restart the program.',
                fg='#FF0000',
            )
            frames['start_menu_frame'].frame.update()
        else:
            labels['main_load_status_label'].label.config(
                text='Flatland failed to create image.\n'
                     'Please restart the program.',
                fg='#FF0000',
            )
            frames['main_menu_frame'].frame.update()
        return

    current_img = 'data/running_tmp.png'

    if last_menu == 'start':
        switch_start_to_main()
    else:
        labels['main_load_status_label'].label.config(
            text='',
            fg='#000000',
        )
        frames['main_menu_frame'].frame.update()
        reload_main_env_viewer()

def save_env_to_file():
    file = filedialog.asksaveasfilename(
        title="Select LP Environment File",
        initialdir='env',
        defaultextension=".lp",
        filetypes=[("Clingo Files", "*.lp"), ("All Files", "*.*")],
    )

    if not file:
        return

    tracks = current_array[0]
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
        "l_arr": current_df['l_arr']
    })

    save_env(tracks, trains, name=file)

def run_simulation():
    global current_paths

    tracks = current_array[0]
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
        "l_arr": current_df['l_arr']
    })

    save_env(tracks, trains)

    current_paths = position_df(
        tracks,
        trains,
        user_params['clingo'],
        user_params['lpFiles'] + ['data/running_tmp.lp'],
        user_params['answer']
    )

    if type(current_paths) == int:
        return current_paths

    delete_tmp_lp()
    return 0
