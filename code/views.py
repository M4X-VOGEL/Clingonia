from custom_widgets import *
from custom_canvas import Canvas


WINDOWS, FRAMES, BUTTONS, LABELS, CANVASES, ENTRY_FIELDS, PICTURES, TEXTS = (
    {}, {}, {}, {}, {}, {}, {}, {}
)

SCREENWIDTH, SCREENHEIGHT = 0, 0


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
        command=lambda: FRAMES['random_gen_help_frame'].toggle_visibility(),
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
        command=lambda: FRAMES['random_gen_canvas_frame'].switch_to_frame(
            FRAMES['random_gen_para_frame']
        ),
        text='Generate Random Environment',
        font=('Arial', 20, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

    BUTTONS['create_env_button'] = Button(
        root=FRAMES['main_menu_frame'].frame,
        width=30,
        height=2,
        x=FRAMES['main_menu_frame'].width * 0.25,
        y=FRAMES['main_menu_frame'].height * 0.35,
        command=lambda: stub,
        text='Create Custom Environment',
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
        command=lambda: stub,
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

def build_random_gen_para_frame():
    global WINDOWS, FRAMES, LABELS, ENTRY_FIELDS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['random_gen_para_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    LABELS['width_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.1,
        text='Environment width:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
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
    )

    LABELS['height_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.15,
        text='Environment height:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
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
    )

    LABELS['agents_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.2,
        text='Number of agents:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
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
    )

    LABELS['cities_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.25,
        text='Max. number of cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
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
    )

    LABELS['seed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.3,
        text='Random generator seed:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['seed_entry'] = EntryField(
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
    )

    LABELS['grid_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.35,
        text='Use grid mode:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['grid_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.35,
        text='e.g. False',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['intercity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.4,
        text='Max. number of rails between cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['intercity_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.4,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['incity_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.45,
        text='Max. number of rail pairs in cities:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['incity_entry'] = EntryField(
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
    )

    LABELS['remove_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.5,
        text='Remove agents on arrival:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['remove_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.5,
        text='e.g. True',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['speed_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.55,
        text='Speed ratio map for trains:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['speed_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.55,
        text='e.g. {1 : 1}',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['malfunction_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.6,
        text='Malfunction rate:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['malfunction_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.6,
        text='e.g. 0/30',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['min_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.65,
        text='Min. duration for malfunctions:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['min_duration_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.65,
        text='e.g. 2',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['max_duration_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.7,
        text='Max. duration for malfunction:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['max_duration_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.7,
        text='e.g. 6',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    LABELS['answer_label'] = Label(
        root=FRAMES['random_gen_para_frame'].frame,
        x=FRAMES['random_gen_para_frame'].width * 0.05,
        y=FRAMES['random_gen_para_frame'].height * 0.75,
        text='Answer to display:',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#000000'
    )

    ENTRY_FIELDS['answer_entry'] = EntryField(
        root=FRAMES['random_gen_para_frame'].frame,
        width=10,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.6,
        y=FRAMES['random_gen_para_frame'].height * 0.75,
        text='e.g. 1',
        font=('Arial', 20, 'bold'),
        foreground_color='#FFFFFF',
        background_color='#222222',
        example_color='#777777',
        border_width=0,
    )

    BUTTONS['generate_button'] = Button(
        root=FRAMES['random_gen_para_frame'].frame,
        width=15,
        height=1,
        x=FRAMES['random_gen_para_frame'].width * 0.25,
        y=FRAMES['random_gen_para_frame'].width * 0.95,
        command=lambda: FRAMES['random_gen_para_frame'].switch_to_frame(
            FRAMES['random_gen_canvas_frame']
        ),
        text='Generate',
        font=('Arial', 30, 'bold'),
        foreground_color='#000000',
        background_color='#777777',
        border_width=0,
    )

def build_random_gen_help_frame():
    global WINDOWS, FRAMES, TEXTS, SCREENWIDTH, SCREENHEIGHT

    FRAMES['random_gen_help_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    with open("../help_texts/help_text.txt", "r") as file:
        # TODO: change help text
        help_displaytext = file.read()

    TEXTS['random_gen_help_text'] = Text(
        root=FRAMES['random_gen_help_frame'].frame,
        width=FRAMES['random_gen_help_frame'].width,
        height=FRAMES['random_gen_help_frame'].height,
        x=FRAMES['random_gen_help_frame'].width * 0,
        y=FRAMES['random_gen_help_frame'].height * 0,
        text=help_displaytext,
        font=("Arial", 14),
        wrap='word',
        foreground_color='#CCCCCC',
        background_color='#000000',
        border_width=0,
        state='disabled',
    )

def build_random_gen_canvas_frame():
    global WINDOWS, FRAMES, CANVASES, SCREENWIDTH, SCREENHEIGHT

    FRAMES['random_gen_canvas_frame'] = Frame(
        root=WINDOWS['flatland_window'].window,
        width=SCREENWIDTH * 0.5,
        height=SCREENHEIGHT,
        x=SCREENWIDTH * 0,
        y=SCREENWIDTH * 0,
        background_color='#000000',
        border_width=0,
        visibility=False
    )

    CANVASES['random_gen_canvas'] = Canvas(
        root=FRAMES['random_gen_canvas_frame'].frame,
        width=FRAMES['random_gen_canvas_frame'].width,
        height=FRAMES['random_gen_canvas_frame'].height,
        x=FRAMES['random_gen_canvas_frame'].width * 0,
        y=FRAMES['random_gen_canvas_frame'].height * 0,
        background_color='#000000',
        border_width=0,
    )

def stub():
    return