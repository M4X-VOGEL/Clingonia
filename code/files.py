import os
import shutil

def save_env(tracks, trains, name="data/running_tmp.lp"):
    """Saves the env as a .lp file.

    Args:
        tracks (list): 2D-List of all tracks.
        trains (pd.DataFrame): Train-configuration.
        name (str): Name of the file.  
    """
    ensure_directory("data")
    path = name
    with open(path, 'w') as lp:
        write_trains(trains, lp)
        write_tracks(tracks, lp)


def delete_tmp_lp():
    """Deletes the temporary file of the env.  
    """
    ensure_directory("data")
    path = "data/running_tmp.lp"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Error: running_tmp.lp could not be deleted:\n{e}")


def delete_tmp_png():
    """Deletes the temporary image of the env.  
    """
    ensure_directory("data")
    path = "data/running_tmp.png"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Error: running_tmp.png could not be deleted:\n{e}")


def delete_tmp_gif():
    """Deletes the temporary image of the env.  
    """
    ensure_directory("data")
    path = "data/running_tmp.gif"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Error: running_tmp.gif could not be deleted:\n{e}")


def delete_tmp_frames():
    """Löscht den Ordner 'tmp_frames' samt Inhalt.
    """
    path = "data/tmp_frames"
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            print(f"Error: tmp_frames folder could not be deleted:\n{e}")


def ensure_directory(d):
    os.makedirs(d, exist_ok=True)


def write_trains(trains, lp):
    for _, row in trains.iterrows():
        lp.write(
            f"train({row['id']}).\n"
            f"start({row['id']},({row['y']},{row['x']}),{row['e_dep']},{row['dir']}).\n"
            f"end({row['id']},({row['y_end']},{row['x_end']}),{row['l_arr']}).\n\n"
        )


def write_tracks(tracks, lp):
    for i, row in enumerate(tracks):
        for j, track in enumerate(row):
            lp.write(f"cell(({i},{j}),{track}).\n")
        lp.write(f'\n')
