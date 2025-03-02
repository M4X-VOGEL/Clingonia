import sys

def import_error_handling(missing_modules):
    """Handles missing module errors by printing instructions and exiting the program.

    Args:
        missing_modules (list[str]): List of missing module names.
    """
    print('\n❌ Error: Essential python module missing.\n'
          'Make sure that you have all these modules installed:\n'
          'flatland-rl, clingo, imageio, pillow, numpy, pandas, matplotlib.\n'
          'You can check the installation with the Python package installer pip:\n\n'
          '     pip show [NAME]\n'
    )
    print('Pip commands for missing packages:\n')
    # For each missing module, print pip install command
    for module in missing_modules:
        print(f'     pip install {module}')
    print()
    # Exit the program as required modules are not present
    sys.exit()


def initial_import_authorization():
    """Checks that all essential Python modules are installed.

    Imports and runs the initial_import_test from code.files.
    If any modules are missing, calls import_error_handling.
    """
    from code.files import initial_import_test
    missing_modules = initial_import_test()
    if missing_modules:
        import_error_handling(missing_modules)


def initial_render_authorization():
    """Ensures that Flatland can render a simple image.

    Imports and runs initial_render_test from code.build_png.
    Exits the program if an OverflowError is encountered.
    """
    try:
        from code.build_png import initial_render_test
        initial_render_test()
    except OverflowError as e:
        # If rendering fails, print error and exit
        print(f'❌ Error: Launch abnormal. Please try again.\n{e}')
        sys.exit()


def start_clingonia():
    """Starts the Clingonia application.

    Removes temporary data and initializes the Flatland window, start menu, and simulation.
    Exits the program if an exception occurs.
    """
    try:
        from code.views import build_flatland_window, create_start_menu, start_flatland
        from code.files import remove_data_remnants
        remove_data_remnants()
        build_flatland_window()
        create_start_menu()
        start_flatland()
    except Exception as e:
        # If any error occurs during startup, print error and exit
        print(f'❌ Error: Not able to boot up. Please try again.\n{e}')
        sys.exit()


def main():
    """Performs initial authorizations and starts the application.
    """
    initial_import_authorization()  # Check for required Python modules
    initial_render_authorization()  # Test that rendering pipeline is functional
    start_clingonia()


if __name__ == "__main__":
    main()
