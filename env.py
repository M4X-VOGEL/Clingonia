import os
import pandas as pd

### TEST-EINGABE
tracks = [
    [16386,1025,17411,1025,5633,1025,4608],
    [32800,0,32800,0,32800,0,32800],
    [72,1025,2064,0,72,1025,2064]
    ]
trains = pd.DataFrame({
    "id": [0,1],
    "x": [4,6],
    "y": [1,1],
    "dir": ['s','n'],
    "x_end": [1,0],
    "y_end": [2,1],
    "e_dep": [1,1],
    "l_arr": [20,20]
})
###

def save_env(tracks, trains, name="running_tmp"):
    """Saves the env as a .lp file.

    Args:
        tracks (list): 2D-List of all tracks.
        trains (pd.DataFrame): Train-configuration.
        name (str): Name of the file.  
    """
    ensure_directory("env")
    path = f"env/{name}.lp"
    with open(path, 'w') as lp:
        write_trains(trains, lp)
        write_tracks(tracks, lp)


def delete_tmp_lp():
    """Deletes the temporary file of the env.  
    """
    ensure_directory("env")
    path = "env/running_tmp.lp"
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
    ensure_directory("env")
    path = "env/running_tmp.png"
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


# Calls
save_env(tracks, trains)  # running_tmp.lp
delete_tmp_lp()  # running_tmp.lp löschen
delete_tmp_png()  # running_tmp.png löschen
save_env(tracks, trains, "env")  # env.lp
