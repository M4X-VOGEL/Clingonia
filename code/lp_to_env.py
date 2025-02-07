import os
import pandas as pd

def lp_to_env(lp_file):
    """Extracts a list of tracks and a DataFrame with train-info from a .lp-file.
    
    Args:
        lp_file (str): Path to file with the environment encoded in ASP.
    
    Returns:
        tracks (list): 2D-list with track-types
        trains (pd.DataFrame): Train-configuration.
    """
    if not file_in_directory(lp_file):
        return -1, -1  # FileNotFoundError
    df_tracks, tse_list = prep_tracks_and_trains(lp_file)
    if isinstance(df_tracks, int) or isinstance(tse_list, int):
        return df_tracks, tse_list  # Error Codes (-2,-3,-4,-5)
    tracks = create_list_of_tracks(df_tracks)
    trains = create_df_of_trains(tse_list)
    return tracks, trains


def file_in_directory(path):
    return os.path.isfile(path)


def prep_tracks_and_trains(path):
    df_tracks = pd.DataFrame(columns=["x", "y", "track"])
    tse_list = []  # list to collect train, start, end
    with open(path, 'r') as lp:
        for line in lp:
            # Separate every predicate of the line
            predicates = line.strip().split('.')
            for pred in predicates:
                pred = pred.strip()
                if not pred:
                    continue
                if pred.startswith("cell"):
                    rc = add_cell(df_tracks, pred)
                    if rc != 0: return rc, rc  # Error
                else:  # train / start / end
                    rc = fill_tse(tse_list, pred)
                    if rc != 0: return rc, rc  # Error
    df_tracks = df_tracks.sort_values(by=['y', 'x'], ascending=[True, True])
    return df_tracks, tse_list


def add_cell(df_tracks, pred):
    # Extract variables
    params = pred[5:-1]
    cell = params.replace('(', '').replace(')', '').split(',')
    if len(cell) != 3:
        return -2  # Report invalid cells
    # Add row to DF
    try:
        y, x = int(cell[0]), int(cell[1])
        track = int(cell[2])
    except ValueError:
        return -2  # Report invalid cells
    df_tracks.loc[len(df_tracks)] = [x, y, track]
    return 0


def fill_tse(tse_list, pred):
    # train(ID)
    if pred.startswith("train"):
        # Extract variables
        params = pred[6:-1]
        train = [p.strip() for p in params.split(',')]
        if len(train) != 1:
            return -3  # Report invalid trains
        try:
            id = int(train[0])
        except ValueError:
            return -3  # Report invalid trains
        tse_list.append(id)

    # start(ID, (Y,X), EarliestDeparture, Direction)
    elif pred.startswith("start"):
        params = pred[6:-1].replace('(', '').replace(')', '')
        start = [p.strip() for p in params.split(',')]
        if len(start) != 5:
            return -4  # Report invalid start
        try:
            id = int(start[0])
            y, x = int(start[1]), int(start[2])
            e_dep = int(start[3])
            dir = start[4]
        except ValueError:
            return -4  # Report invalid start
        tse_list.append(["start", id, x, y, e_dep, dir])

    # end(ID, (Y,X), LatestArrival)
    elif pred.startswith("end"):
        params = pred[4:-1].replace('(', '').replace(')', '')
        end = [p.strip() for p in params.split(',')]
        if len(end) != 4:
            return -5  # Report invalid end
        try:
            id = int(end[0])
            y_end, x_end = int(end[1]), int(end[2])
            l_arr = int(end[3])
        except ValueError:
            return -5  # Report invalid end
        tse_list.append(["end", id, x_end, y_end, l_arr])
    return 0


def create_list_of_tracks(df_tracks):
    tracks = []
    for _, row in df_tracks.iterrows():
        y, track = int(row['y']), int(row['track'])
        # Fill with rows until row y exists
        while len(tracks) <= y:
            tracks.append([])
        # Add track to row y
        tracks[y].append(track)
    return tracks


def create_df_of_trains(tse_list):
    trains = pd.DataFrame(columns=["id", "x", "y", "dir", "x_end", "y_end", "e_dep", "l_arr"])
    trains_list = sorted([i for i in tse_list if isinstance(i, int)])
    for id in trains_list:
        for l in tse_list:
            if isinstance(l, list):
                if l[0] == 'start' and l[1] == id:
                    x, y = l[2], l[3]
                    e_dep, dir = l[4], l[5]
                elif l[0] == 'end' and l[1] == id:
                    x_end, y_end = l[2], l[3]
                    l_arr = l[4]
        trains.loc[len(trains)] = [id, x, y, dir, x_end, y_end, e_dep, l_arr]
    return trains
