import pandas as pd
import winsound
from code import clingo_actions
pd.set_option('display.max_rows', None)  # Anzeige aller DF-Zeilen

def position_df(tracks, trains, clingo_path, lp_files, answer_number):
    """
    Creates a DataFrame of the x-y-position and direction for the trains at each timestep.
    
    Returns:
        [pd.DataFrame] IDs, Positions, Directions, Timesteps
    """
    df_actions = clingo_actions.clingo_to_df(clingo_path, lp_files, answer_number)
    if type(df_actions) == int: return df_actions  # Error Handling
    df_pos = build_df_pos(df_actions, trains, tracks)
    print("Valdidating actions...")
    # Adjust actions, if end position is incorrect
    df_actions, df_pos = adjust_actions(df_pos, trains, df_actions, tracks)
    # Make sure that every train has a position
    df_pos = ensure_train_spawns(df_pos, trains)
    print("Run Simulation: DONE")
    # Audio Feedback
    winsound.Beep(600, 200)
    winsound.Beep(800, 250)
    return df_pos

def build_df_pos(df_actions, trains, tracks):
    """Creates position DF based on action DF.
    """
    df_pos = pd.DataFrame(columns=["trainID", "x", "y", "dir", "timestep"])
    train_ids = {}
    # Calculate positions based on actions
    for _, row in df_actions.iterrows():
        train_id = row['trainID']
        action = row["action"]
        t = row["timestep"]
        # Set start position
        if train_id not in train_ids:
            x, y, dir = get_start_pos(train_id, trains)
            # Set start at timestep t-1
            df_pos.loc[len(df_pos)] = [train_id, x, y, dir, t-1]
            train_ids[train_id] = (x, y, dir)
        else:
            # Use last position for next positions
            x, y, dir = train_ids[train_id]
        # Calculate next positions
        x_new, y_new, dir_new = next_pos(x, y, action, dir, tracks)
        df_pos.loc[len(df_pos)] = [train_id, x_new, y_new, dir_new, t]
        train_ids[train_id] = (x_new, y_new, dir_new)
    return df_pos

def adjust_actions(df_pos, trains, df_actions, tracks):
    """Adjusts the last position with the station position.
    """
    changed = True
    while changed:
        changed = False
        for train in df_actions['trainID'].unique():
            df_pos_train = df_pos[df_pos['trainID'] == train]
            if df_pos_train.empty:
                continue  # Jump to next ID
            last_pos = df_pos_train.iloc[-1]
            x_last, y_last = last_pos['x'], last_pos['y']
            
            # Get station position
            train_row = trains[trains['id'] == train]
            if train_row.empty:
                continue
            x_end = train_row['x_end'].iloc[0]
            y_end = train_row['y_end'].iloc[0]
            
            # Remove unnecessary spawn actions or
            # remove every action, if actions do not reach the target
            if not (x_last == x_end and y_last == y_end):
                idxs = df_actions[df_actions['trainID'] == train].index
                idx_to_drop = idxs[0]
                df_actions.drop(index=idx_to_drop, inplace=True)
                df_actions.reset_index(drop=True, inplace=True)
                changed = True
                # Break with change to rebuild df_pos
                break
        # Rebuild df_pos if change happened
        if changed:
            df_pos = build_df_pos(df_actions, trains, tracks)
    return df_actions, df_pos


def ensure_train_spawns(df_pos, trains):
    is_incomplete = False
    # Get missing trainIDs in df_pos
    missing_trains = set(trains["id"]) - set(df_pos["trainID"])
    for train_id in missing_trains:
        is_incomplete = True
        # Get info of missing train
        train_row = trains.loc[trains["id"] == train_id].iloc[0]
        x_val = train_row["x"]
        y_val = train_row["y"]
        dir_val = train_row["dir"]
        e_dep = train_row["e_dep"]
        l_arr = train_row["l_arr"]
        # Determine earliest spawn time
        earliest_spawn = e_dep-1 if e_dep > 0 else e_dep
        # Spawn at earliest spawntime possible
        for spawn_time in range(earliest_spawn, l_arr+1):
            # Check if cell is already occupied
            conflict = df_pos[(df_pos["timestep"] == spawn_time) & (df_pos["x"] == x_val) & (df_pos["y"] == y_val)]
            if conflict.empty:
                # If cell is vacant, create new row
                new_row = {
                    "trainID": train_id,
                    "x": x_val,
                    "y": y_val,
                    "dir": dir_val,
                    "timestep": spawn_time
                }
                # Add new row to df_pos
                df_pos = pd.concat([df_pos, pd.DataFrame([new_row])], ignore_index=True)
                break
            else:
                # If cell is already occupied
                spawn_time += 1
    # Sort df_pos
    df_pos = df_pos.sort_values(by=["trainID", "timestep"]).reset_index(drop=True)
    if is_incomplete:
        print("❌ Valdiation done with warning:\n"
              "The actions produced by the lp-files might be invalid/incomplete.\n"
              "The afflicted agents will only spawn on the earliest possible timestep."
        )
    else:
        print("✅ Valdidation done.")
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
    # Check, if x and y are valid coordinates
    if y < 0 or y >= len(tracks) or x < 0 or x >= len(tracks[0]):
        # Just keep moving forward. df_actions spawn moves reduction incoming.
        return dir
    # Tracks with directional change
    dir_tr = [4608, 16386, 72, 2064,
              20994, 16458, 2136, 6672,
              37408, 17411, 32872, 3089,
              49186, 1097, 34864, 5633]
    
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
