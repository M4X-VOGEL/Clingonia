from views import *


def main():
    build_flatland_window()
    build_title_frame()
    build_start_menu()
    WINDOWS['flatland_window'].run()

if __name__ == "__main__":
    main()