import os
import shutil
import importlib

def ensure_directory(d):
    """Creates the specified directory if it does not exist.

    Args:
        d (str): Directory path to create.
    """
    os.makedirs(d, exist_ok=True)


def write_trains(trains, lp):
    """Writes train predicates to a specified .lp file.

    Args:
        trains (pd.DataFrame): Train configuration.
        lp (file object): .lp file.
    """
    for _, row in trains.iterrows():
        lp.write(
            f"train({row['id']}).\n"
            f"start({row['id']},({row['y']},{row['x']}),{row['e_dep']},{row['dir']}).\n"
            f"end({row['id']},({row['y_end']},{row['x_end']}),{row['l_arr']}).\n\n"
        )


def write_tracks(tracks, lp):
    """Writes cell predicates for the tracks to a specified .lp file.

    Args:
        tracks (list[list[int]]): 2D list of track types.
        lp (file object): .lp file.
    """
    for i, row in enumerate(tracks):
        for j, track in enumerate(row):
            lp.write(f"cell(({i},{j}),{track}).\n")
        lp.write(f'\n')


def save_env(tracks, trains, name="data/running_tmp.lp"):
    """Saves the environment as a .lp file.

    Args:
        tracks (list[list[int]]): 2D list of all tracks.
        trains (pd.DataFrame): Train configuration.
        name (str): Path of .lp file.
    """
    ensure_directory("data")
    path = name
    with open(path, 'w') as lp:
        write_trains(trains, lp)
        write_tracks(tracks, lp)


def delete_tmp_lp():
    """Deletes the temporary .lp file of the environment.
    """
    ensure_directory("data")
    path = "data/running_tmp.lp"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Error: running_tmp.lp could not be deleted:\n{e}")


def delete_tmp_png():
    """Deletes the temporary PNG of the environment.
    """
    ensure_directory("data")
    path = "data/running_tmp.png"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Error: running_tmp.png could not be deleted:\n{e}")


def delete_tmp_gif():
    """Deletes the temporary GIF of the environment.
    """
    ensure_directory("data")
    path = "data/running_tmp.gif"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Error: running_tmp.gif could not be deleted:\n{e}")


def delete_tmp_frames():
    """Deletes the temporary folder containing GIF frames.
    """
    path = "data/tmp_frames"
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            print(f"Error: tmp_frames folder could not be deleted:\n{e}")


def initial_import_test():
    """Checks for essential Python modules required by the program.

    Returns:
        list[str]: Missing module names.
    """
    required_modules = [
        'flatland',
        'clingo',
        'imageio',
        'PIL',
        'numpy',
        'pandas',
        'matplotlib'
    ]
    missing_modules = []
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            if module == 'flatland':
                missing_modules.append('flatland-rl')
            elif module == 'PIL':
                missing_modules.append('pillow')
            else:
                missing_modules.append(module)
    return missing_modules


def remove_data_remnants():
    """Removes all temporary files and directories.
    """
    delete_tmp_lp()
    delete_tmp_png()
    delete_tmp_gif()
    delete_tmp_frames()
