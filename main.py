from code.views import *


def main():
    build_flatland_window()
    create_start_menu()
    WINDOWS['flatland_window'].run()

if __name__ == "__main__":
    main()