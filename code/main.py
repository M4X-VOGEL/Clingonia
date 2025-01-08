from views import *


def main():
    build_flatland_window()
    build_title_frame()
    build_main_menu()
    build_random_gen_para_frame()
    build_random_gen_help_frame()
    build_random_gen_canvas_frame()
    WINDOWS['flatland_window'].run()

if __name__ == "__main__":
    main()