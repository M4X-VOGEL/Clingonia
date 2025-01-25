import os
import pandas as pd

def lp_to_env(lp_file):
    """Extracts a list of tracks and a DataFrame with train-info from a .lp-file.
    
    Args:
        lp_file (str): File of the environment encoded in ASP.
    
    Returns:
        tracks (list): 2D-list with track-types
        trains (pd.DataFrame): Train-configuration.
    """
    path = f"env/{lp_file}"
    if not file_in_directory(path):
        return -1, -1  # FileNotFoundError
    df_tracks, tse_list = prep_tracks_and_trains(path)
    tracks = create_list_of_tracks(df_tracks)
    trains = create_df_of_trains(tse_list)
    return tracks, trains


def file_in_directory(path):
    return os.path.isfile(path)


def prep_tracks_and_trains(path):
    df_tracks = pd.DataFrame(columns=["x", "y", "track"])
    tse_list = []  # list to collect train, start, end
    with open(path, 'r') as lp:
        for _, row in enumerate(lp):
            if row[0] == 'c':  # cell
                add_cell(df_tracks, row)
            else:  # train / start / end
                fill_tse(tse_list, row)
    df_tracks = df_tracks.sort_values(by=['y', 'x'], ascending=[True, True])
    df_tracks[["x", "y", "track"]] = df_tracks[["x", "y", "track"]]
    return df_tracks, tse_list


def add_cell(df_tracks, row):
    cell = row[5:-3].replace('(', '').replace(')', '').split(',')
    y, x = int(cell[0]), int(cell[1])
    track = int(cell[2])
    df_tracks.loc[len(df_tracks)] = [x, y, track]


def fill_tse(tse_list, row):
    if row[0] == 't':  # train
        id = int(row[6:-3])
        tse_list.append(id)
    elif row[0] == 's':  # start
        start = row[6:-3].replace('(', '').replace(')', '').split(',')
        id, e_dep, dir = int(start[0]), int(start[3]), start[4]
        x, y = int(start[1]), int(start[2])
        tse_list.append(["start", id, x, y, e_dep, dir])
    elif row[0] == 'e':  # end
        end = row[4:-3].replace('(', '').replace(')', '').split(',')
        id, l_arr = int(end[0]), int(end[3])
        x_end, y_end = int(end[1]), int(end[2])
        tse_list.append(["end", id, x_end, y_end, l_arr])


def create_list_of_tracks(df_tracks):
    tracks = []
    for _, row in df_tracks.iterrows():
        y, track = int(row['y']), int(row['track'])
        tracks[y].append(track) if y < len(tracks) else tracks.append([track])
    return tracks


def create_df_of_trains(tse_list):
    trains = pd.DataFrame(columns=["id", "x", "y", "dir", "x_end", "y_end", "e_dep", "l_arr"])
    trains_list = sorted([i for i in tse_list if type(i) == int])
    for id in trains_list:
        for l in tse_list:
            if type(l) == list:
                if l[0] == 'start' and l[1] == id:
                    x, y = l[2], l[3]
                    e_dep, dir = l[4], l[5]
                elif l[0] == 'end' and l[1] == id:
                    x_end, y_end = l[2], l[3]
                    l_arr = l[4]
        trains.loc[len(trains)] = [id, x, y, dir, x_end, y_end, e_dep, l_arr]
    return trains


### Test
tracks, trains = lp_to_env("env.lp")
print(tracks)
print()
print(trains)
###
