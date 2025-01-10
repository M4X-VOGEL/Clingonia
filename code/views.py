from custom_widgets import *
from custom_canvas import *


WINDOWS, FRAMES, BUTTONS, LABELS, CANVASES, ENTRY_FIELDS, PICTURES, TEXTS = (
    {}, {}, {}, {}, {}, {}, {}, {}
)

SCREENWIDTH, SCREENHEIGHT = 0, 0





# start menu

def create_start_menu():
    build_flatland_window()
    build_title_frame()
    build_start_menu_frame()

def build_flatland_window():
    global WINDOWS, SCREENWIDTH, SCREENHEIGHT
    
    WINDOWS['flatland_window'] = Window(
        width=None,
        height=None,
        fullscreen=True,
        background_color='#00FF00',
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
        background_color='#000000',
        visibility=True,
    )

    LABELS['title_label'] = Label(
        root=FRAMES['title_frame'].frame,
        x=FRAMES['title_frame'].width * 0.17,
        y=FRAMES['title_frame'].height * 0.15,
        text='FLATLAND',
        font=('Arial', 80, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

def build_start_menu_frame():
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
        command=exit_stub,
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['start_help_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=2,
        height=1,
        x=FRAMES['start_menu_frame'].width * 0,
        y=FRAMES['start_menu_frame'].height * 0,
        command=toggle_start_menu_help,
        text='?',
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
        x=FRAMES['start_menu_frame'].width * 0.25,
        y=FRAMES['start_menu_frame'].height * 0.25,
        command=switch_start_to_random_gen,
        text='Generate Random Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['build_env_button'] = Button(
        root=FRAMES['start_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['start_menu_frame'].width * 0.25,
        y=FRAMES['start_menu_frame'].height * 0.35,
        command=switch_start_to_builder,
        text='Build Custom Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
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
        visibility=True,
    )

def build_start_menu_help_frame():
    global WINDOWS, FRAMES, TEXTS, SCREENWIDTH, SCREENHEIGHT

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
        visibility=True,
    )

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
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
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
    build_main_menu()
    build_main_menu_env_viewer()

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
        visibility=True
    )

    BUTTONS['exit_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=2,
        height=1,
        x=FRAMES['main_menu_frame'].width * 0.95,
        y=FRAMES['main_menu_frame'].width * 0,
        command=exit_stub,
        text='X',
        font=('Arial', 25, 'bold'),
        foreground_color='#FF0000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['help_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=2,
        height=1,
        x=FRAMES['main_menu_frame'].width * 0,
        y=FRAMES['main_menu_frame'].height * 0,
        command=toggle_main_menu_help,
        text='?',
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
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.25,
        command=switch_main_to_random_gen,
        text='Generate Random Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['build_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.35,
        command=switch_main_to_builder,
        text='Build Custom Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['modify_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.45,
        command=switch_main_to_builder,
        text='Modify Existing Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
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
        visibility=True,
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
        visibility=True,
    )

    BUTTONS['run_sim_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.75,
        command=create_result_menu,
        text='Run Simulation',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

def build_main_menu_help_frame():
    global WINDOWS, FRAMES, TEXTS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['main_menu_help_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
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
        x=FRAMES['main_menu_help_frame'].width * 0,
        y=FRAMES['main_menu_help_frame'].height * 0,
        text=help_displaytext,
        font=("Arial", 14),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
        visibility=True,
    )#

def build_main_menu_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['main_menu_env_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
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





# random generation

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
        visibility=True
    )

    BUTTONS['generate_button'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].width * 0.95,
        command=random_gen_para_to_env_frame,
        text='Generate',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['advanced_options'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].width * 0.95,
        command=random_gen_toggle_advanced_para_options,
        text='Advanced Options',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['width_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.1,
        text='Environment width:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['width_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.1,
        text='e.g. 40',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['height_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.15,
        text='Environment height:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['height_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.15,
        text='e.g. 40',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['agents_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.2,
        text='Number of agents:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['agents_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.2,
        text='e.g. 4',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['cities_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.25,
        text='Max. number of cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['cities_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.25,
        text='e.g. 4',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['answer_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.3,
        text='Answer to display:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['answer_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.3,
        text='e.g. 1',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['seed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.35,
        text='Seed:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['seed_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.35,
        text='e.g. 1',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['grid_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.4,
        text='Use grid mode:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['grid_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.4,
        text='e.g. False',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['intercity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.45,
        text='Max. number of rails between cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['intercity_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.45,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['incity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.5,
        text='Max. number of rail pairs in cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['incity_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.5,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['remove_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.55,
        text='Remove agents on arrival:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['remove_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.55,
        text='e.g. True',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.6,
        text='Speed ratio map for trains:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['speed_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.6,
        text='e.g. {1 : 1}',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.65,
        text='Malfunction rate:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['malfunction_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.65,
        text='e.g. 0/30',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.7,
        text='Min. duration for malfunctions:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['min_duration_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.7,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.75,
        text='Max. duration for malfunction:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['max_duration_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.75,
        text='e.g. 6',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

def random_gen_para_to_env_frame():
    # TODO: save random gen parameters

    if 'random_gen_para_frame' in FRAMES:
        FRAMES['random_gen_para_frame'].destroy_frame()
        del FRAMES['random_gen_para_frame']

    build_random_gen_env_viewer()
    build_random_gen_env_menu()

def build_random_gen_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['random_gen_env_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
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
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['random_gen_env_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['return_to_menu_button'] = Button(
        root=FRAMES['random_gen_env_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['random_gen_env_menu_frame'].width * 0.25,
        y=FRAMES['random_gen_env_menu_frame'].width * 0.95,
        command=switch_random_gen_to_main,
        text='Return To Main Menu',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

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





# builder

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
        visibility=True
    )

    BUTTONS['build_button'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].width * 0.95,
        command=builder_para_to_grid,
        text='Build',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    BUTTONS['advanced_options'] = Button(
        root=FRAMES['builder_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].width * 0.95,
        command=builder_toggle_advanced_para_options,
        text='Advanced Options',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['width_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.1,
        text='Environment width:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['width_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.1,
        text='e.g. 40',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['height_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.15,
        text='Environment height:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['height_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.15,
        text='e.g. 40',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['agents_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.2,
        text='Number of agents:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['agents_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.2,
        text='e.g. 4',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['cities_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.25,
        text='Max. number of cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['cities_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.25,
        text='e.g. 4',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['answer_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.3,
        text='Answer to display:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=True,
    )

    ENTRY_FIELDS['answer_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.3,
        text='e.g. 1',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=True,
    )

    LABELS['seed_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.35,
        text='Seed:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['seed_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.35,
        text='e.g. 1',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['grid_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.4,
        text='Use grid mode:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['grid_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.4,
        text='e.g. False',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['intercity_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.45,
        text='Max. number of rails between cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['intercity_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.45,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['incity_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.5,
        text='Max. number of rail pairs in cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['incity_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.5,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['remove_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.55,
        text='Remove agents on arrival:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['remove_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.55,
        text='e.g. True',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.6,
        text='Speed ratio map for trains:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['speed_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.6,
        text='e.g. {1 : 1}',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.65,
        text='Malfunction rate:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['malfunction_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.65,
        text='e.g. 0/30',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.7,
        text='Min. duration for malfunctions:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['min_duration_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.7,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES['builder_para_frame'].frame,
        x=FRAMES['builder_para_frame'].width * 0.05,
        y=FRAMES['builder_para_frame'].height * 0.75,
        text='Max. duration for malfunction:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000',
        visibility=False,
    )

    ENTRY_FIELDS['max_duration_entry'] = EntryField(
        root=FRAMES['builder_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['builder_para_frame'].width * 0.6,
        y=FRAMES['builder_para_frame'].height * 0.75,
        text='e.g. 6',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
        visibility=False,
    )

def builder_para_to_grid():
    # TODO: save builder parameters

    if 'builder_para_frame' in FRAMES:
        FRAMES['builder_para_frame'].destroy_frame()
        del FRAMES['builder_para_frame']

    build_builder_menu_frame()
    build_builder_grid_frame()

def build_builder_menu_frame():
    FRAMES['builder_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['finish_building_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['builder_menu_frame'].width * 0.25,
        y=FRAMES['builder_menu_frame'].width * 0.95,
        command=builder_grid_to_env,
        text='Finish Building',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#FF0000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['horizontal_straight_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.02,
        y=FRAMES['builder_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(32800),
        image='../png/Gleis_horizontal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['vertical_straight_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.14,
        y=FRAMES['builder_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(1025),
        image='../png/Gleis_vertikal.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_top_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.52,
        y=FRAMES['builder_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(2064),
        image='../png/Gleis_kurve_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_top_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.64,
        y=FRAMES['builder_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(72),
        image='../png/Gleis_kurve_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_bottom_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.76,
        y=FRAMES['builder_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(16386),
        image='../png/Gleis_kurve_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['corner_bottom_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.88,
        y=FRAMES['builder_menu_frame'].width * 0.05,
        command=lambda: CANVASES['build_grid_canvas'].select(4608),
        image='../png/Gleis_kurve_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_top_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.02,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(3089),
        image='../png/Weiche_horizontal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_top_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.14,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(32872),
        image='../png/Weiche_horizontal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_bottom_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.26,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(17411),
        image='../png/Weiche_horizontal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_hor_bottom_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.38,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(38408),
        image='../png/Weiche_horizontal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_top_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.52,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(34864),
        image='../png/Weiche_vertikal_oben_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_top_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.64,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(1097),
        image='../png/Weiche_vertikal_oben_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_bottom_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.76,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(49186),
        image='../png/Weiche_vertikal_unten_rechts.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['switch_ver_bottom_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.88,
        y=FRAMES['builder_menu_frame'].width * 0.2,
        command=lambda: CANVASES['build_grid_canvas'].select(5633),
        image='../png/Weiche_vertikal_unten_links.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['diamond_crossing_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.02,
        y=FRAMES['builder_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(33825),
        image='../png/Gleis_Diamond_Crossing.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        visibility=True,
    )

    BUTTONS['single_slip_top_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.52,
        y=FRAMES['builder_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(35889),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    BUTTONS['single_slip_top_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.64,
        y=FRAMES['builder_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(33897),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    BUTTONS['single_slip_bottom_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.76,
        y=FRAMES['builder_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(50211),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['single_slip_bottom_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.88,
        y=FRAMES['builder_menu_frame'].width * 0.35,
        command=lambda: CANVASES['build_grid_canvas'].select(38433),
        image='../png/Weiche_Single_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['double_slip_top_left_bottom_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.02,
        y=FRAMES['builder_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(52275),
        image='../png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['double_slip_bottom_left_top_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.14,
        y=FRAMES['builder_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(38505),
        image='../png/Weiche_Double_Slip.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['symmetrical_top_left_top_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.52,
        y=FRAMES['builder_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(2136),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    BUTTONS['symmetrical_top_right_bottom_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.64,
        y=FRAMES['builder_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(16458),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['symmetrical_bottom_left_bottom_right_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.76,
        y=FRAMES['builder_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(20994),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['symmetrical_top_left_bottom_left_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.88,
        y=FRAMES['builder_menu_frame'].width * 0.5,
        command=lambda: CANVASES['build_grid_canvas'].select(6672),
        image='../png/Weiche_Symetrical.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    BUTTONS['train_north_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.02,
        y=FRAMES['builder_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(1),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['train_east_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.14,
        y=FRAMES['builder_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(2),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=270,
        visibility=True,
    )

    BUTTONS['train_south_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.26,
        y=FRAMES['builder_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(3),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=180,
        visibility=True,
    )

    BUTTONS['train_west_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.38,
        y=FRAMES['builder_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(4),
        image='../png/Zug_Gleis_#0091ea.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=90,
        visibility=True,
    )

    BUTTONS['station_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.52,
        y=FRAMES['builder_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(5),
        image='../png/Bahnhof_#d50000.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

    BUTTONS['delete_button'] = Button(
        root=FRAMES['builder_menu_frame'].frame,
        width=100,
        height=100,
        x=FRAMES['builder_menu_frame'].width * 0.76,
        y=FRAMES['builder_menu_frame'].width * 0.65,
        command=lambda: CANVASES['build_grid_canvas'].select(0),
        image='../png/eraser.png',
        foreground_color='#000000',
        background_color='#000000',
        border_width=0,
        rotation=0,
        visibility=True,
    )

def build_builder_grid_frame():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['builder_grid_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
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
        array=np.zeros((3, 40, 40)),
    )

def builder_grid_to_env():
    # TODO: save builder array and dataframe

    if 'builder_menu_frame' in FRAMES:
        FRAMES['builder_menu_frame'].destroy_frame()
        del FRAMES['builder_menu_frame']
    if 'builder_grid_frame' in FRAMES:
        FRAMES['builder_grid_frame'].destroy_frame()
        del FRAMES['builder_grid_frame']

    build_builder_env_viewer()
    build_builder_env_menu()

def build_builder_env_viewer():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['builder_env_viewer_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
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

def build_builder_env_menu():
    global WINDOWS, FRAMES, BUTTONS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['builder_env_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['return_to_menu_button'] = Button(
        root=FRAMES['builder_env_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['builder_env_menu_frame'].width * 0.25,
        y=FRAMES['builder_env_menu_frame'].width * 0.95,
        command=switch_builder_to_main,
        text='Return To Main Menu',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
    )

def builder_toggle_advanced_para_options():
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

def switch_builder_to_main():
    # TODO: save builder env

    if 'builder_env_viewer_frame' in FRAMES:
        FRAMES['builder_env_viewer_frame'].destroy_frame()
        del FRAMES['builder_env_viewer_frame']
    if 'builder_env_menu_frame' in FRAMES:
        FRAMES['builder_env_menu_frame'].destroy_frame()
        del FRAMES['builder_env_menu_frame']

    create_main_menu()





# result menu

def create_result_menu():
    build_result_menu()
    build_result_env_viewer()

def build_result_menu():
    FRAMES['result_menu_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0.5,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=True
    )

    BUTTONS['return_to_menu_button'] = Button(
        root=FRAMES['result_menu_frame'].frame,
        width=20,
        height=1,
        x=FRAMES['result_menu_frame'].width * 0.25,
        y=FRAMES['result_menu_frame'].width * 0.95,
        command=switch_result_to_main,
        text='Return To Main Menu',
        font=('Arial', 25, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
        visibility=True,
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
        visibility=True,
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
        visibility=True,
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
        visibility=True,
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

def switch_result_to_main():
    # TODO: Is there anything to save in the result view?

    if 'result_viewer_frame' in FRAMES:
        FRAMES['result_viewer_frame'].destroy_frame()
        del FRAMES['result_viewer_frame']
    if 'result_menu_frame' in FRAMES:
        FRAMES['result_menu_frame'].destroy_frame()
        del FRAMES['result_menu_frame']

    create_main_menu()





# stubs

def exit_stub():
    global WINDOWS
    WINDOWS['flatland_window'].close_window()

def stub():
    return



# TODOS

# GUI
# TODO: add Back buttons in random gen, builder menus
# TODO: add help buttons in random gen, builder and result menus
# TODO: change train and station placement in builder menu to
#  editable dataframe version in separate frame
# TODO: add path selector in result view

# BACKEND
# TODO: add save data functions for random gen, builder, stat and main menus
# TODO: save data in files / datastructures and pass it to ÄD and flatland
# TODO: add flatland environment generation from parameters and array for
#  random gen, builder menus
