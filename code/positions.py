import pandas as pd
from code.actions import clingo_to_df

def position_df(tracks, trains, clingo_path, lp_files, answer_number):
    """Creates a DataFrame of the x-y-position and direction for the trains at each timestep.
    
    Returns:
        [pd.DataFrame] IDs, Positions, Directions, Timesteps
    """
    df_actions = clingo_to_df(clingo_path, lp_files, answer_number)
    df_actions = df_actions.sort_values(by=["trainID", "timestep"], ascending=[True, True])
    df_pos = pd.DataFrame(columns=["trainID", "x", "y", "dir", "timestep"])
    # Train IDs
    train_ids = []
    for _, row in df_actions.iterrows():
        id = row['trainID']
        action = row["action"]
        t = row["timestep"]
        # Add start position when reaching new ID
        if id not in train_ids:
            x, y, dir = get_start_pos(id, trains)
            df_pos.loc[len(df_pos)] = [id, x, y, dir, t-1]
            train_ids.append(id)
        # Following Positions
        x, y, dir = next_pos(x, y, action, dir, tracks)
        df_pos.loc[len(df_pos)] = [id, x, y, dir, t]
    return df_pos


def get_start_pos(train_id, trains):
    x = trains.loc[trains["id"] == train_id, "x"].iloc[0]
    y = trains.loc[trains["id"] == train_id, "y"].iloc[0]
    dir = trains.loc[trains["id"] == train_id, "dir"].iloc[0]
    return x, y, dir


def next_pos(x, y, action, dir, tracks):
    # Direction change
    if action in ["move_forward", "move_left", "move_right"]:
        dir_new = dir_change(x, y, action, dir, tracks)
        x_new, y_new = pos_change(x, y, dir_new)
    else:  # wait-action
        return x, y, dir
    return x_new, y_new, dir_new
    

def dir_change(x, y, action, dir, tracks):
    # Tracks with dir-change
    dir_tr = [4608,16386,72,2064,
            20994,16458,2136,6672,
            37408,17411,32872,3089,
            49186,1097,34864,5633]
    
    if action == "move_forward":
        track = tracks[y][x]
        if track in dir_tr:
            # Change direction: Curve or Switch-Merge
            if dir == 'n':
                if track == 4608: dir = 'w'
                elif track == 16386: dir = 'e'
                elif track == 16458: dir = 'e'
                elif track == 6672: dir = 'w'
                elif track == 17411: dir = 'e'
                elif track == 5633: dir = 'w'
            elif dir == 'e':
                if track == 4608: dir = 's'
                elif track == 2064: dir = 'n'
                elif track == 20994: dir = 's'
                elif track == 2136: dir = 'n'
                elif track == 37408: dir = 's'
                elif track == 34864: dir = 'n'
            elif dir == 's':
                if track == 72: dir = 'e'
                elif track == 2064: dir = 'w'
                elif track == 16458: dir = 'e'
                elif track == 6672: dir = 'w'
                elif track == 3089: dir = 'w'
                elif track == 1097: dir = 'e'
            elif dir == 'w':
                if track == 16386: dir = 's'
                elif track == 72: dir = 'n'
                elif track == 20994: dir = 's'
                elif track == 2136: dir = 'n'
                elif track == 32872: dir = 'n'
                elif track == 49186: dir = 's'
    elif action == "move_left":
        if dir == 'n': dir = 'w'
        elif dir == 'e': dir = 'n'
        elif dir == 's': dir = 'e'
        elif dir == 'w': dir = 's'
    elif action == "move_right":
        if dir == 'n': dir = 'e'
        elif dir == 'e': dir = 's'
        elif dir == 's': dir = 'w'
        elif dir == 'w': dir = 'n'
    return dir


def pos_change(x, y, dir):
    if dir == 'n': y -= 1
    elif dir == 'e': x += 1
    elif dir == 's': y += 1
    elif dir == 'w': x -= 1
    return x, y
