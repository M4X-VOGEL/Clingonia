import os
import pandas as pd

def save_env(tracks, trains, name="../data/running_tmp.lp"):
    """Saves the env as a .lp file.

    Args:
        tracks (list): 2D-List of all tracks.
        trains (pd.DataFrame): Train-configuration.
        name (str): Name of the file.  
    """
    ensure_directory("../data")
    path = name
    with open(path, 'w') as lp:
        write_trains(trains, lp)
        write_tracks(tracks, lp)


def delete_tmp_lp():
    """Deletes the temporary file of the env.  
    """
    ensure_directory("../data")
    path = "../data/running_tmp.lp"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Fehler: Datei running_tmp.lp konnte nicht gelöscht werden:\n{e}")
    else:
        print("Fehler: Datei running_tmp.lp konnte nicht gefunden werden.")


def delete_tmp_png():
    """Deletes the temporary image of the env.  
    """
    ensure_directory("../data")
    path = "../data/running_tmp.png"
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            print(f"Fehler: Datei running_tmp.lp konnte nicht gelöscht werden:\n{e}")
    else:
        print("Fehler: Datei running_tmp.lp konnte nicht gefunden werden.")


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
