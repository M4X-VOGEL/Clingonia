import ast
import json

from custom_canvas import *


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
DEFAULT_ENV_PARAS = {
    'rows': 40,
    'cols': 40,
    'agents': 4,
    'cities': 4,
    'answer': 1,
    'seed': 1,
    'grid': False,
    'intercity': 2,
    'incity': 2,
    'remove': True,
    'speed': {1 : 1},
    'malfunction': (0, 30),
    'min': 2,
    'max': 6,
}
USER_ENV_PARAS = {
    'rows': None,
    'cols': None,
    'agents': None,
    'cities': None,
    'answer': None,
    'seed': None,
    'grid': None,
    'intercity': None,
    'incity': None,
    'remove': None,
    'speed': None,
    'malfunction': None,
    'min': None,
    'max': None,
}

CURRENT_ARRAY = np.zeros((3,40,40), dtype=int)
CURRENT_DF = pd.DataFrame(
    columns=['start_pos', 'dir', 'end_pos', 'e_dep', 'l_arr']
)

CURRENT_BACKUP_ARRAY = CURRENT_ARRAY.copy()
CURRENT_BACKUP_DF = CURRENT_DF.copy()





# start menu

def build_flatland_window():
    global WINDOWS, SCREENWIDTH, SCREENHEIGHT, FONT_SCALE

    WINDOWS['flatland_window'] = Window(
        width=None,
        height=None,
        fullscreen=True,
        background_color='#00FF00',
        title='Flatland'
    )

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
        padding=(0, 50),
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
        image='./env_001--4_2.png',
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
        command=exit_stub,
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
        command=lambda: stub,
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

def title_to_start_viewer():
    if 'title_frame' in FRAMES:
        FRAMES['title_frame'].destroy_frame()
        del FRAMES['title_frame']

    build_start_menu_env_viewer()

def build_start_menu_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['start_menu_env_viewer_frame'] = Frame(
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

    CANVASES['start_menu_env_viewer_canvas'] = EnvCanvas(
        root=FRAMES['start_menu_env_viewer_frame'].frame,
        width=FRAMES['start_menu_env_viewer_frame'].width,
        height=FRAMES['start_menu_env_viewer_frame'].height,
        x=FRAMES['start_menu_env_viewer_frame'].width * 0,
        y=FRAMES['start_menu_env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image='env_001--4_2.png'
    )

    FRAMES['start_menu_env_viewer_frame'].frame.rowconfigure(0, weight=1)
    FRAMES['start_menu_env_viewer_frame'].frame.columnconfigure(0, weight=1)
    FRAMES['start_menu_env_viewer_frame'].frame.grid_propagate(False)

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
        command=exit_stub,
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
        command=lambda: stub,
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
        command=lambda: stub,
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
        command=switch_main_to_result,
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
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

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
        image='env_001--4_2.png'
    )

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

def switch_main_to_result():
    if 'main_menu_frame' in FRAMES:
        FRAMES['main_menu_frame'].destroy_frame()
        del FRAMES['main_menu_frame']
    if 'main_menu_help_frame' in FRAMES:
        FRAMES['main_menu_help_frame'].destroy_frame()
        del FRAMES['main_menu_help_frame']
    if 'main_menu_env_viewer_frame' in FRAMES:
        FRAMES['main_menu_env_viewer_frame'].destroy_frame()
        del FRAMES['main_menu_env_viewer_frame']

    create_result_menu()





# random generation

def random_gen_change_to_start_or_main():
    global LAST_MENU

    if LAST_MENU == 'start':
        create_start_menu()
    else:
        create_main_menu()

def random_gen_para_to_start():
    save_random_gen_env_params()

    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].destroy_frame()
        del FRAMES['random_gen_para_frame']

    create_start_menu()

def random_gen_para_to_main():
    save_random_gen_env_params()

    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].destroy_frame()
        del FRAMES['random_gen_para_frame']

    create_main_menu()

def build_random_gen_para_frame():
    global WINDOWS, FRAMES, LABELS, ENTRY_FIELDS, SCREENWIDTH, SCREENHEIGHT, \
        DEFAULT_ENV_PARAS

    FRAMES['random_gen_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
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
        text=f'e.g. {DEFAULT_ENV_PARAS["rows"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
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
        text=f'e.g. {DEFAULT_ENV_PARAS["cols"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
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
        text=f'e.g. {DEFAULT_ENV_PARAS["agents"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
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
        text=f'e.g. {DEFAULT_ENV_PARAS["cities"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['answer_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(5, 1),
        padding=(0, 0),
        sticky='nw',
        text='Answer to display:',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['answer_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["answer"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['seed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(6, 1),
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
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["seed"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['grid_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(7, 1),
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
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["grid"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['intercity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(8, 1),
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
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["intercity"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['incity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(9, 1),
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
        grid_pos=(9, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["incity"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['remove_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(10, 1),
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
        grid_pos=(10, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["remove"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(11, 1),
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
        grid_pos=(11, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["speed"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(12, 1),
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
        grid_pos=(12, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["malfunction"][0]}/'
             f'{DEFAULT_ENV_PARAS["malfunction"][1]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(13, 1),
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
        grid_pos=(13, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["min"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        grid_pos=(14, 1),
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
        grid_pos=(14, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["max"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    BUTTONS['generate_button'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(15, 1),
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
        grid_pos=(15, 2),
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
        tuple(range(16)), weight=1
    )
    FRAMES['random_gen_para_frame'].frame.columnconfigure(
        tuple(range(3)), weight=1
    )
    FRAMES['random_gen_para_frame'].frame.grid_propagate(False)

    load_random_gen_env_params()

def random_gen_para_to_env():
    save_random_gen_env_params()

    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].destroy_frame()
        del FRAMES['random_gen_para_frame']

    build_random_gen_env_viewer()
    build_random_gen_env_menu()

def random_gen_env_to_para():
    # TODO: maybe Save random gen Env?

    if 'random_gen_env_viewer_frame' in FRAMES:
        FRAMES['random_gen_env_viewer_frame'].destroy_frame()
        del FRAMES['random_gen_env_viewer_frame']
    if 'random_gen_env_menu_frame' in FRAMES:
        FRAMES['random_gen_env_menu_frame'].destroy_frame()
        del FRAMES['random_gen_env_menu_frame']

    build_random_gen_para_frame()

def build_random_gen_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

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
        image='env_001--4_2.png'
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
    # TODO: Save random gen Env

    if 'random_gen_env_viewer_frame' in FRAMES:
        FRAMES['random_gen_env_viewer_frame'].destroy_frame()
        del FRAMES['random_gen_env_viewer_frame']
    if 'random_gen_env_menu_frame' in FRAMES:
        FRAMES['random_gen_env_menu_frame'].destroy_frame()
        del FRAMES['random_gen_env_menu_frame']

    create_main_menu()

def save_random_gen_env_params():
    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_ENV_PARAS:
            continue

        data = ENTRY_FIELDS[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'grid' or key == 'remove':
                data = data.lower() == 'true'
            elif key == 'speed':
                data = ast.literal_eval(data)
            elif key == 'malfunction':
                data = (int(data.split('/')[0]),int(data.split('/')[1]))
            else:
                data = int(data)
        except Exception as e:
            print(f"Input error for key '{key}': {str(e)}")
            # TODO: display error message next tor Entry field using LABELS[key]

        if type(data) is not str:
            USER_ENV_PARAS[key] = data

    save_dictionary_to_json(USER_ENV_PARAS, '../data/user_params.json')

def load_random_gen_env_params():
    global USER_ENV_PARAS

    data = load_dictionary_from_json('../data/user_params.json')

    if data['speed'] is not None:
        data['speed'] = {int(k): v for k, v in data['speed'].items()}
    if data['malfunction'] is not None:
        data['malfunction'] = (data['malfunction'][0], data['malfunction'][1])

    USER_ENV_PARAS = data

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_ENV_PARAS:
            continue
        elif USER_ENV_PARAS[key] is None:
            continue
        elif key == 'malfunction':
            ENTRY_FIELDS[field].insert_string(
                f'{USER_ENV_PARAS["malfunction"][0]}/'
                f'{USER_ENV_PARAS["malfunction"][1]}'
            )
        else:
            ENTRY_FIELDS[field].insert_string(str(USER_ENV_PARAS[key]))





# builder

def builder_change_to_start_or_main():
    global LAST_MENU

    if LAST_MENU == 'start':
        create_start_menu()
    else:
        create_main_menu()

def builder_para_to_start():
    global BUILD_MODE
    BUILD_MODE = None

    save_builder_env_params()

    if 'builder_para_frame' in FRAMES:
        FRAMES['builder_para_frame'].destroy_frame()
        del FRAMES['builder_para_frame']

    create_start_menu()

def builder_para_to_main():
    global BUILD_MODE
    BUILD_MODE = None

    save_builder_env_params()

    if 'builder_para_frame' in FRAMES:
        FRAMES['builder_para_frame'].destroy_frame()
        del FRAMES['builder_para_frame']

    create_main_menu()

def build_builder_para_frame():
    global WINDOWS, FRAMES, LABELS, ENTRY_FIELDS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['builder_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        grid_pos=(0, 1),
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
        text=f'e.g. {DEFAULT_ENV_PARAS["rows"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
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
        text=f'e.g. {DEFAULT_ENV_PARAS["cols"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['answer_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
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
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        grid_pos=(3, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["answer"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['remove_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(4, 1),
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
        grid_pos=(4, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["remove"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(5, 1),
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
        grid_pos=(5, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["speed"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(6, 1),
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
        grid_pos=(6, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["malfunction"][0]}/'
             f'{DEFAULT_ENV_PARAS["malfunction"][1]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(7, 1),
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
        grid_pos=(7, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["min"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        grid_pos=(8, 1),
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
        grid_pos=(8, 2),
        padding=(0, 0),
        sticky='nw',
        text=f'e.g. {DEFAULT_ENV_PARAS["max"]}',
        font=('Arial', int(FONT_SCALE * BASE_FONT), 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    BUTTONS['build_button'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=15,
        height=1,
        grid_pos=(9, 1),
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
        grid_pos=(9, 2),
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
        tuple(range(10)), weight=1
    )
    FRAMES['builder_para_frame'].frame.columnconfigure(
        tuple(range(3)), weight=1
    )
    FRAMES['builder_para_frame'].frame.grid_propagate(False)

    load_builder_env_params()

def builder_para_to_track_grid():
    global BUILD_MODE, CURRENT_ARRAY, CURRENT_DF, DEFAULT_ENV_PARAS, \
        USER_ENV_PARAS, CURRENT_BACKUP_ARRAY, CURRENT_BACKUP_DF

    save_builder_env_params()

    if 'builder_para_frame' in FRAMES:
        FRAMES['builder_para_frame'].destroy_frame()
        del FRAMES['builder_para_frame']

    if USER_ENV_PARAS['rows'] is not None:
        rows = USER_ENV_PARAS['rows']
    else:
        rows = DEFAULT_ENV_PARAS['rows']

    if USER_ENV_PARAS['cols'] is not None:
        cols = USER_ENV_PARAS['cols']
    else:
        cols = DEFAULT_ENV_PARAS['cols']

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
                        CURRENT_DF.at[index, 'end_pos'] = (np.nan, np.nan)

    CURRENT_BACKUP_ARRAY = CURRENT_ARRAY.copy()
    CURRENT_BACKUP_DF = CURRENT_DF.copy()

    build_track_builder_menu_frame()
    build_builder_grid_frame()

def builder_track_grid_to_para():
    global FRAMES
    # TODO: save builder array and dataframe

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
        command=lambda: CANVASES['builder_grid_canvas'].select(32800),
        image='../png/Gleis_horizontal.png',
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
        command=lambda: CANVASES['builder_grid_canvas'].select(1025),
        image='../png/Gleis_vertikal.png',
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
        image='../png/Gleis_kurve_oben_links.png',
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
        image='../png/Gleis_kurve_oben_rechts.png',
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
        image='../png/Gleis_kurve_unten_rechts.png',
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
        image='../png/Gleis_kurve_unten_links.png',
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
        image='../png/Weiche_horizontal_oben_links.png',
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
        command=lambda: CANVASES['builder_grid_canvas'].select(32872),
        image='../png/Weiche_horizontal_oben_rechts.png',
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
        image='../png/Weiche_horizontal_unten_rechts.png',
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
        command=lambda: CANVASES['builder_grid_canvas'].select(38408),
        image='../png/Weiche_horizontal_unten_links.png',
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
        image='../png/Weiche_vertikal_oben_links.png',
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
        command=lambda: CANVASES['builder_grid_canvas'].select(1097),
        image='../png/Weiche_vertikal_oben_rechts.png',
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
        image='../png/Weiche_vertikal_unten_rechts.png',
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
        command=lambda: CANVASES['builder_grid_canvas'].select(5633),
        image='../png/Weiche_vertikal_unten_links.png',
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
        image='../png/Gleis_Diamond_Crossing.png',
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
        image='../png/Weiche_Single_Slip.png',
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
        image='../png/Weiche_Single_Slip.png',
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
        image='../png/Weiche_Single_Slip.png',
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
        image='../png/Weiche_Single_Slip.png',
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
        image='../png/Weiche_Double_Slip.png',
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
        image='../png/Weiche_Double_Slip.png',
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
        image='../png/Weiche_Symetrical.png',
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
        image='../png/Weiche_Symetrical.png',
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
        image='../png/Weiche_Symetrical.png',
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
        image='../png/Weiche_Symetrical.png',
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
        image='../png/eraser.png',
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
        image='../png/Zug_Gleis_#0091ea.png',
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
        image='../png/Zug_Gleis_#0091ea.png',
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
        image='../png/Zug_Gleis_#0091ea.png',
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
        image='../png/Zug_Gleis_#0091ea.png',
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
    global FRAMES, CANVASES, CURRENT_BACKUP_ARRAY, CURRENT_BACKUP_DF
    # TODO: save builder array and dataframe

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
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

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
        image='env_001--4_2.png'
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

    # TODO: save builder env

    if 'builder_env_viewer_frame' in FRAMES:
        FRAMES['builder_env_viewer_frame'].destroy_frame()
        del FRAMES['builder_env_viewer_frame']
    if 'builder_env_menu_frame' in FRAMES:
        FRAMES['builder_env_menu_frame'].destroy_frame()
        del FRAMES['builder_env_menu_frame']

    create_main_menu()

def save_builder_env_params():
    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_ENV_PARAS:
            continue
        if key in ['agents', 'cities', 'seed', 'grid', 'intercity', 'incity']:
            continue

        data = ENTRY_FIELDS[field].entry_field.get()

        try:
            if data.startswith('e.g.'):
                data = None
            elif data == '':
                data = None
            elif key == 'grid' or key == 'remove':
                data = data.lower() == 'true'
            elif key == 'speed':
                data = ast.literal_eval(data)
            elif key == 'malfunction':
                data = (int(data.split('/')[0]),int(data.split('/')[1]))
            else:
                data = int(data)
        except Exception as e:
            print(f"Input error for key '{key}': {str(e)}")
            # TODO: display error message next tor Entry field using LABELS[key]

        if type(data) is not str:
            USER_ENV_PARAS[key] = data

    save_dictionary_to_json(USER_ENV_PARAS, '../data/user_params.json')

def load_builder_env_params():
    global USER_ENV_PARAS

    data = load_dictionary_from_json('../data/user_params.json')

    if data['speed'] is not None:
        data['speed'] = {int(k): v for k, v in data['speed'].items()}
    if data['malfunction'] is not None:
        data['malfunction'] = (data['malfunction'][0], data['malfunction'][1])

    USER_ENV_PARAS = data

    for field in ENTRY_FIELDS:
        key = field.split('_')[0]
        if key not in DEFAULT_ENV_PARAS:
            continue
        elif key in ['agents', 'cities', 'seed', 'grid', 'intercity', 'incity']:
            continue
        elif USER_ENV_PARAS[key] is None:
            continue
        elif key == 'malfunction':
            ENTRY_FIELDS[field].insert_string(
                f'{USER_ENV_PARAS["malfunction"][0]}/'
                f'{USER_ENV_PARAS["malfunction"][1]}'
            )
        else:
            ENTRY_FIELDS[field].insert_string(str(USER_ENV_PARAS[key]))

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
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

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
        image='env_001--4_2.png',
        paths_df=pd.read_csv('../data/positions.csv')
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
    # TODO: Is there anything to save in the result view?

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

def save_dictionary_to_json(dictionary: dict, file_path: str):
    with open(file_path, 'w') as file:
        json.dump(dictionary, file, indent=4)
    return

def load_dictionary_from_json(file_path: str):
    with open(file_path, 'r') as file:
        dictionary = json.load(file)
    return dictionary

# stubs

def exit_stub():
    global WINDOWS, CURRENT_DF
    WINDOWS['flatland_window'].close_window()

def stub():
    return



# TODOS

# TODO: add flatland environment generation from parameters and array for
#  random gen, builder menus

# TODO: Load and save functions in main menu
# TODO: show time table and gif functions in Results

# TODO: Eingabe für lp files, 'clingo path' und answer im main menu
# TODO: move answer entry to the same eingabe option

# BACKEND
# TODO: add save data functions for random gen, builder, stat and main menus
# TODO: save data in files / datastructures and pass it to ÄD and flatland

# GUI
# TODO: add help buttons in random gen, builder and result menus
