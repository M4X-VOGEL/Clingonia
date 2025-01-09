import numpy as np

from custom_widgets import *
from custom_canvas import *


WINDOWS, FRAMES, BUTTONS, LABELS, CANVASES, ENTRY_FIELDS, PICTURES, TEXTS = (
    {}, {}, {}, {}, {}, {}, {}, {}
)

SCREENWIDTH, SCREENHEIGHT = 0, 0

# start condition

def build_flatland_window():
    global WINDOWS, SCREENWIDTH, SCREENHEIGHT
    
    WINDOWS['flatland_window'] = Window(
        width=None,
        height=None,
        fullscreen=True,
        background_color='#000000',
        title='Flatland'
    )
    
    SCREENWIDTH = WINDOWS['flatland_window'].window.winfo_screenwidth()
    SCREENHEIGHT = WINDOWS['flatland_window'].window.winfo_screenheight()

def build_title_frame():
    global WINDOWS, FRAMES, LABELS, PICTURES, SCREENWIDTH, SCREENHEIGHT
    
    FRAMES['title_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    PICTURES['title_image'] = Picture(
        root=FRAMES['title_frame'].frame,
        width=500,
        height=500,
        x=FRAMES['title_frame'].width * 0.20,
        y=FRAMES['title_frame'].height * 0.3,
        image='./env_001--4_2.png',
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    LABELS['title_label'] = Label(
        root=FRAMES['title_frame'].frame,
        x=FRAMES['title_frame'].width * 0.17,
        y=FRAMES['title_frame'].height * 0.15,
        text='FLATLAND',
        font=('Arial', 80, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

def build_start_menu():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['start_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['exit_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=2,
        height=1,
        x=FRAMES['start_menu_frame'].width * 0.95,
        y=FRAMES['start_menu_frame'].width * 0,
        command=WINDOWS['flatland_window'].close_window,
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['start_help_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=2,
        height=1,
        x=FRAMES['start_menu_frame'].width * 0,
        y=FRAMES['start_menu_frame'].height * 0,
        command=build_start_menu_help_frame,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['random_gen_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['start_menu_frame'].width * 0.25,
        y=FRAMES['start_menu_frame'].height * 0.25,
        command=build_random_gen_para_frame,
        text='Generate Random Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['build_env_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['start_menu_frame'].width * 0.25,
        y=FRAMES['start_menu_frame'].height * 0.35,
        command=build_builder_para_frame,
        text='Build Custom Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['load_env_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['start_menu_frame'].width * 0.25,
        y=FRAMES['start_menu_frame'].height * 0.55,
        command=lambda: stub,
        text='Load Custom Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

def build_start_menu_help_frame():
    global WINDOWS, FRAMES, TEXTS, SCREENWIDTH, SCREENHEIGHT
    if 'start_menu_help_frame' in FRAMES:
        FRAMES['start_menu_help_frame'].toggle_visibility()
    else:
        FRAMES['start_menu_help_frame'] = Frame(
            root=WINDOWS['flatland_window'].window,
            width=SCREENWIDTH * 0.5,
            height=SCREENHEIGHT,
            x=SCREENWIDTH * 0,
            y=SCREENWIDTH * 0,
            background_color='#000000',
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
            x=FRAMES['start_menu_help_frame'].width * 0,
            y=FRAMES['start_menu_help_frame'].height * 0,
            text=help_displaytext,
            font=("Arial", 14),
            wrap='word',
            foreground_color='#CCCCCC',
            background_color='#000000',
            border_width=0,
            state='disabled',
        )

# main menu

def build_main_menu_view():
    build_main_menu()
    build_env_viewer_frame()
    build_main_menu_help_frame()
    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].switch_to_frame(
            FRAMES['main_menu_frame']
        )
    elif 'build_menu_frame' in FRAMES:
        FRAMES['build_menu_frame'].switch_to_frame(
            FRAMES['main_menu_frame']
        )
    else:
        FRAMES['result_menu_frame'].switch_to_frame(
            FRAMES['main_menu_frame']
        )
        FRAMES['result_viewer_frame'].switch_to_frame(
            FRAMES['env_viewer_frame']
        )

def build_main_menu():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['main_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    BUTTONS['exit_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=2,
        height=1,
        x=FRAMES['main_menu_frame'].width * 0.95,
        y=FRAMES['main_menu_frame'].width * 0,
        command=WINDOWS['flatland_window'].close_window,
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['help_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=2,
        height=1,
        x=FRAMES['main_menu_frame'].width * 0,
        y=FRAMES['main_menu_frame'].height * 0,
        command=build_main_menu_help_frame,
        text='?',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['random_gen_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.25,
        command=build_random_gen_para_frame,
        text='Generate Random Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['build_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.35,
        command=build_builder_para_frame,
        text='Build Custom Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['modify_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.45,
        command=build_builder_para_frame,
        text='Modify Existing Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['load_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.55,
        command=lambda: stub,
        text='Load Custom Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['save_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.65,
        command=lambda: stub,
        text='Save Custom Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['run_sim_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.75,
        command=build_result_view,
        text='Run Simulation',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
    )

def build_main_menu_help_frame():
    global WINDOWS, FRAMES, TEXTS, SCREENWIDTH, SCREENHEIGHT
    if 'main_menu_help_frame' in FRAMES:
        FRAMES['main_menu_help_frame'].toggle_visibility()
    else:
        FRAMES['main_menu_help_frame'] = Frame(
            root=WINDOWS['flatland_window'].window,
            width=SCREENWIDTH * 0.5,
            height=SCREENHEIGHT,
            x=SCREENWIDTH * 0,
            y=SCREENWIDTH * 0,
            background_color='#000000',
            border_width=0,
            visibility=False
        )

        with open("../help_texts/main_menu_help_text.txt", "r") as file:
            # TODO: change help text
            help_displaytext = file.read()

        TEXTS['main_menu_help_frame'] = Text(
            root=FRAMES['main_menu_help_frame'].frame,
            width=FRAMES['main_menu_help_frame'].width,
            height=FRAMES['main_menu_help_frame'].height,
            x=FRAMES['main_menu_help_frame'].width * 0,
            y=FRAMES['main_menu_help_frame'].height * 0,
            text=help_displaytext,
            font=("Arial", 14),
            wrap='word',
            foreground_color='#CCCCCC',
            background_color='#000000',
            border_width=0,
            state='disabled',
        )

def build_env_viewer_frame():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['env_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    CANVASES['env_viewer_canvas'] = EnvCanvas(
        root=FRAMES['env_viewer_frame'].frame,
        width=FRAMES['env_viewer_frame'].width,
        height=FRAMES['env_viewer_frame'].height,
        x=FRAMES['env_viewer_frame'].width * 0,
        y=FRAMES['env_viewer_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        image='env_001--4_2.png'
    )

# parameter entries

def show_base_para_options(parent_frame: str):
    LABELS['width_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.1,
        text='Environment width:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['width_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.1,
        text='e.g. 40',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['height_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.15,
        text='Environment height:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['height_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.15,
        text='e.g. 40',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['agents_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.2,
        text='Number of agents:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['agents_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.2,
        text='e.g. 4',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['cities_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.25,
        text='Max. number of cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['cities_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.25,
        text='e.g. 4',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['answer_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.3,
        text='Answer to display:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['answer_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.3,
        text='e.g. 1',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

def show_advanced_para_options(parent_frame: str):
    LABELS['seed_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.35,
        text='Random generator seed:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['seed_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.35,
        text='e.g. 1',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['grid_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.4,
        text='Use grid mode:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['grid_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.4,
        text='e.g. False',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['intercity_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.45,
        text='Max. number of rails between cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['intercity_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.45,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['incity_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.5,
        text='Max. number of rail pairs in cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['incity_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.5,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['remove_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.55,
        text='Remove agents on arrival:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['remove_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.55,
        text='e.g. True',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.6,
        text='Speed ratio map for trains:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['speed_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.6,
        text='e.g. {1 : 1}',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.65,
        text='Malfunction rate:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['malfunction_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.65,
        text='e.g. 0/30',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.7,
        text='Min. duration for malfunctions:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['min_duration_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.7,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES[parent_frame].frame,
        x=FRAMES[parent_frame].width * 0.05,
        y=FRAMES[parent_frame].height * 0.75,
        text='Max. duration for malfunction:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['max_duration_entry'] = EntryField(
        root=FRAMES[parent_frame].frame,
        width=10,
        height=1,
        x=FRAMES[parent_frame].width * 0.6,
        y=FRAMES[parent_frame].height * 0.75,
        text='e.g. 6',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

# loop for random generation

def build_random_gen_para_frame():
    global WINDOWS, FRAMES, LABELS, ENTRY_FIELDS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['random_gen_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )
    if 'start_menu_frame' in FRAMES:
        FRAMES['start_menu_frame'].switch_to_frame(FRAMES['random_gen_para_frame'])
    else:
        FRAMES['main_menu_frame'].switch_to_frame(FRAMES['random_gen_para_frame'])
    show_base_para_options('random_gen_para_frame')

    BUTTONS['generate_button'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].width * 0.95,
        command=build_random_gen_viewer,
        text='Generate',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['advanced_options'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].width * 0.95,
        command=lambda : show_advanced_para_options('random_gen_para_frame'),
        text='Advanced Options',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

def build_random_gen_viewer():
    build_env_viewer_frame()
    if 'title_frame' in FRAMES:
        FRAMES['title_frame'].switch_to_frame(FRAMES['env_viewer_frame'])
    build_main_menu_view()

# loop for build menu

def build_builder_para_frame():
    global WINDOWS, FRAMES, LABELS, ENTRY_FIELDS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['builder_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )
    if 'start_menu_frame' in FRAMES:
        FRAMES['start_menu_frame'].switch_to_frame(FRAMES['builder_para_frame'])
    else:
        FRAMES['main_menu_frame'].switch_to_frame(FRAMES['builder_para_frame'])
    show_base_para_options('builder_para_frame')

    BUTTONS['build_button'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].width * 0.95,
        command=build_builder_view,
        text='Build',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['advanced_options'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].width * 0.95,
        command=lambda : show_advanced_para_options('builder_para_frame'),
        text='Advanced Options',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

def build_builder_view():
    build_build_menu_frame()
    build_build_grid_frame()
    if 'start_menu_frame' in FRAMES:
        FRAMES['start_menu_frame'].switch_to_frame(FRAMES['build_menu_frame'])
        FRAMES['title_frame'].switch_to_frame(FRAMES['build_grid_frame'])
    else:
        FRAMES['main_menu_frame'].switch_to_frame(FRAMES['build_menu_frame'])
        FRAMES['env_viewer_frame'].switch_to_frame(FRAMES['build_grid_frame'])

def build_build_menu_frame():
    FRAMES['build_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    BUTTONS['horizontal_straight_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.02,
        y=FRAMES['build_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(32800),
        image='../png/Gleis_horizontal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['vertical_straight_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.14,
        y=FRAMES['build_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(1025),
        image='../png/Gleis_vertikal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['corner_top_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.52,
        y=FRAMES['build_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(2064),
        image='../png/Gleis_kurve_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['corner_top_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.64,
        y=FRAMES['build_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(72),
        image='../png/Gleis_kurve_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['corner_bottom_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.76,
        y=FRAMES['build_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(16386),
        image='../png/Gleis_kurve_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['corner_bottom_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.88,
        y=FRAMES['build_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(4608),
        image='../png/Gleis_kurve_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_hor_top_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.02,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(3089),
        image='../png/Weiche_horizontal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_hor_top_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.14,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(32872),
        image='../png/Weiche_horizontal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_hor_bottom_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.26,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(17411),
        image='../png/Weiche_horizontal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_hor_bottom_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.38,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(38408),
        image='../png/Weiche_horizontal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_ver_top_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.52,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(34864),
        image='../png/Weiche_vertikal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_ver_top_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.64,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(1097),
        image='../png/Weiche_vertikal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_ver_bottom_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.76,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(49186),
        image='../png/Weiche_vertikal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['switch_ver_bottom_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.88,
        y=FRAMES['build_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(5633),
        image='../png/Weiche_vertikal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['diamond_crossing_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.02,
        y=FRAMES['build_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(33825),
        image='../png/Gleis_Diamond_Crossing.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
    )

    BUTTONS['single_slip_top_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.52,
        y=FRAMES['build_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(35889),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
    )

    BUTTONS['single_slip_top_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.64,
        y=FRAMES['build_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(33897),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
    )

    BUTTONS['single_slip_bottom_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.76,
        y=FRAMES['build_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(50211),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
    )

    BUTTONS['single_slip_bottom_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.88,
        y=FRAMES['build_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(38433),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
    )

    BUTTONS['double_slip_top_left_bottom_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.02,
        y=FRAMES['build_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(52275),
        image='../png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
    )

    BUTTONS['double_slip_bottom_left_top_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.14,
        y=FRAMES['build_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(38505),
        image='../png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
    )

    BUTTONS['symmetrical_top_left_top_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.52,
        y=FRAMES['build_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(2136),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
    )

    BUTTONS['symmetrical_top_right_bottom_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.64,
        y=FRAMES['build_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(16458),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
    )

    BUTTONS['symmetrical_bottom_left_bottom_right_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.76,
        y=FRAMES['build_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(20994),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
    )

    BUTTONS['symmetrical_top_left_bottom_left_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.88,
        y=FRAMES['build_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(6672),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
    )

    BUTTONS['train_north_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.02,
        y=FRAMES['build_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(1),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
    )

    BUTTONS['train_east_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.14,
        y=FRAMES['build_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(2),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
    )

    BUTTONS['train_south_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.26,
        y=FRAMES['build_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(3),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
    )

    BUTTONS['train_west_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.38,
        y=FRAMES['build_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(4),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
    )

    BUTTONS['station_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.52,
        y=FRAMES['build_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(5),
        image='../png/Bahnhof_#d50000.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
    )

    BUTTONS['delete_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['build_menu_frame'].width * 0.76,
        y=FRAMES['build_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(0),
        image='../png/eraser.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
    )

    BUTTONS['finish_building_button'] = Button(
        root=FRAMES['build_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['build_menu_frame'].width * 0.25,
        y=FRAMES['build_menu_frame'].width * 0.95,
        command=build_finished_build_viewer,
        text='Finish Building',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
    )

def build_build_grid_frame():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['build_grid_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    CANVASES['build_grid_canvas'] = BuildCanvas(
        root=FRAMES['build_grid_frame'].frame,
        width=FRAMES['build_grid_frame'].width,
        height=FRAMES['build_grid_frame'].height,
        x=FRAMES['build_grid_frame'].width * 0,
        y=FRAMES['build_grid_frame'].height * 0,
        background_color='#333333',
        border_width=0,
        array=np.zeros((3, 40, 40)),
    )

def build_finished_build_viewer():
    build_env_viewer_frame()
    if 'title_frame' in FRAMES:
        FRAMES['title_frame'].switch_to_frame(FRAMES['env_viewer_frame'])
    build_main_menu_view()

# loop for result view

def build_result_view():
    build_result_menu()
    build_result_env_viewer()
    FRAMES['main_menu_frame'].switch_to_frame(FRAMES['result_menu_frame'])
    FRAMES['env_viewer_frame'].switch_to_frame(FRAMES['result_viewer_frame'])

def build_result_menu():
    FRAMES['result_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    BUTTONS['return_to_menu_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['result_menu_frame'].width * 0.25,
        y=FRAMES['result_menu_frame'].width * 0.95,
        command=build_main_menu_view,
        text='Return To Main Menu',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['show_time_table_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['result_menu_frame'].width * 0.25,
        y=FRAMES['result_menu_frame'].width * 0.1,
        command=stub,
        text='Show Time Table',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['show_gif_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['result_menu_frame'].width * 0.25,
        y=FRAMES['result_menu_frame'].width * 0.2,
        command=stub,
        text='Show GIF',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['show_all_paths_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['result_menu_frame'].width * 0.25,
        y=FRAMES['result_menu_frame'].width * 0.3,
        command=stub,
        text='Show All Paths',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

def build_result_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['result_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
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
    )

def stub():
    return