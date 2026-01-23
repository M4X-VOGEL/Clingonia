import os
import shutil
import importlib
import numpy as np
from random import seed, randint
MALFUNCTIONS_EXIST = False

def ensure_directory(d):
    """Creates the specified directory if it does not exist.

    Args:
        d (str): Directory path to create.
    """
    os.makedirs(d, exist_ok=True)


def save_malfunctions(user_params):
    global MALFUNCTIONS_EXIST
    # Requirement check
    fraction = user_params["malfunction"]
    num, denom = fraction[0], fraction[1]
    if not num:
        delete_tmp_malfunctions()
        MALFUNCTIONS_EXIST = False
        return
    MALFUNCTIONS_EXIST = True
    m_reprod = user_params["malfuncRepro"]
    if not m_reprod:
        seed(np.random.randint(-2**31,2**31))
    # Parameters
    rate = int(denom/num)
    max_time = user_params["globalTimeLimit"]
    train_count = user_params["agents"]
    min_malf = user_params["min"]
    max_malf = user_params["max"]
    # File creation
    path = "data/malfunction_tmp.lp"
    with open(path, 'w') as lp:
        # Malfunction generation
        for t in range(max_time):
            if not randint(0, rate-1):
                tid = randint(0, train_count-1)
                dur = randint(min_malf, max_malf)
                # Write malfunction predicates
                lp.write(f"malfunction({tid},{dur},{t}).\n")
    seed(user_params["seed"])


def write_globals(user_params, lp):
    """Writes global predicates to a specified .lp file.

    Args:
        user_params (dict): User parameters.
        lp (file object): .lp file.
    """
    # Write global(MaxTime) predicate
    lp.write(f"global({user_params['globalTimeLimit']}).\n\n")


def write_trains(trains, lp):
    """Writes train predicates to a specified .lp file.

    Args:
        trains (pd.DataFrame): Train configuration.
        lp (file object): .lp file.
    """
    for _, row in trains.iterrows():
        tid, inv_spd = row['id'], row['speed']
        # Write train, speed, start and end predicates
        lp.write(
            f"train({row['id']}).\n"
            f"speed({tid},{inv_spd}).\n"
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
        # Write an extra line after each env row for readability
        lp.write(f'\n')


def save_env(tracks, trains, user_params, name="data/running_tmp.lp"):
    """Saves the environment as a .lp file.

    Args:
        tracks (list[list[int]]): 2D list of all tracks.
        trains (pd.DataFrame): Train configuration.
        user_params (dict): User parameters.
        name (str): Path of .lp file.
    """
    ensure_directory("data")
    path = name
    with open(path, 'w') as lp:
        # Write global, train and track predicates to the file
        write_globals(user_params, lp)
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
    ensure_directory("data")
    path = "data/tmp_frames"
    if os.path.isdir(path):
        try:
            # Recursively delete the directory and its contents
            shutil.rmtree(path)
        except OSError as e:
            print(f"Error: tmp_frames folder could not be deleted:\n{e}")


def delete_tmp_malfunctions():
    """Deletes the temporary .lp file of the malfunctions.
    """
    ensure_directory("data")
    path = "data/malfunction_tmp.lp"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Error: malfunction_tmp.lp could not be deleted:\n{e}")


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
    # Iterate over each required module and try to import it
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
    delete_tmp_malfunctions()
