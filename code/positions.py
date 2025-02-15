import os
import pandas as pd
import platform
import subprocess
from code.clingo_actions import clingo_to_df

invalid_path = None
# Directional changes - (DirIn, Type): DirOut
fw_tracks = {
    # Curves
    ('n', 4608):  'w',
    ('e', 4608):  's',
    ('n', 16386): 'e',
    ('w', 16386): 's',
    ('s', 72):    'e',
    ('w', 72):    'n',
    ('s', 2064):  'w',
    ('e', 2064):  'n',
    # Switches
    ('e', 37408): 's',
    ('n', 17411): 'e',
    ('w', 32872): 'n',
    ('s', 3089):  'w',
    ('w', 49186): 's',
    ('s', 1097):  'e',
    ('e', 34864): 'n',
    ('n', 5633):  'w',
    # Splits
    ('e', 20994): 's',
    ('w', 20994): 's',
    ('n', 16458): 'e',
    ('s', 16458): 'e',
    ('e', 2136):  'n',
    ('w', 2136):  'n',
    ('n', 6672):  'w',
    ('s', 6672):  'w'
}

to_left_tracks = {
    # Switches
    ('n', 37408): 'w',
    ('w', 17411): 's',
    ('s', 32872): 'e',
    ('e', 3089): 'n',
    # Crossings
    ('n', 38433): 'w',
    ('w', 50211): 's',
    ('s', 33897): 'e',
    ('e', 35889): 'n',
    ('n', 38505): 'w',
    ('s', 38505): 'e',
    ('e', 52275): 'n',
    ('w', 52275): 's',
    # Splits
    ('n', 20994): 'w',
    ('w', 16458): 's',
    ('s', 2136): 'e',
    ('e', 6672): 'n'
}

to_right_tracks = {
    # Switches
    ('n', 49186): 'e',
    ('w', 1097): 'n',
    ('s', 34864): 'w',
    ('e', 5633): 's',
    # Crossings
    ('e', 38433): 's',
    ('n', 50211): 'e',
    ('w', 33897): 'n',
    ('s', 35889): 'w',
    ('e', 38505): 's',
    ('w', 38505): 'n',
    ('n', 52275): 'e',
    ('s', 52275): 'w',
    # Splits
    ('n', 20994): 'e',
    ('w', 16458): 'n',
    ('s', 2136): 'w',
    ('e', 6672): 's'
}

def position_df(tracks, trains, clingo_path, lp_files, answer_number):
    """
    Creates a DataFrame of the x-y-position and direction for the trains at each timestep.
    
    Returns:
        [pd.DataFrame] IDs, Positions, Directions, Timesteps
    """
    # Actions into DF
    df_actions_original = clingo_to_df(clingo_path, lp_files, answer_number)
    if isinstance(df_actions_original, int): return df_actions_original  # Error Handling
    # Save original df_actions to provide a faulty list of action predicates, later.
    df_actions = df_actions_original.copy(deep=True)
    # Actions to positions
    df_pos = build_df_pos(df_actions, trains, tracks)
    # Adjust actions, if end position is incorrect
    print("Valdidating actions...")
    df_actions, df_pos = adjust_actions(df_pos, trains, df_actions, tracks)
    # Put invalid action-predicate paths
    write_act_err_txt(df_actions_original, df_actions, trains)
    # Make sure that every train has a position
    df_pos = ensure_train_spawns(df_pos, trains)
    print("Run Simulation: DONE")
    # Audio Feedback
    beep_feedback()
    return df_pos

def build_df_pos(df_actions, trains, tracks):
    """Creates position DF based on action DF.
    """
    df_pos = pd.DataFrame(columns=["trainID", "x", "y", "dir", "timestep"])
    train_ids = {}
    # Calculate positions based on actions
    for _, row in df_actions.iterrows():
        id = row['trainID']
        action = row["action"]
        t = row["timestep"]
        # Set start position
        if id not in train_ids:
            x, y, dir = get_start_pos(id, trains)
            # Set start at timestep t-1
            df_pos.loc[len(df_pos)] = [id, x, y, dir, t-1]
            train_ids[id] = (x, y, dir)
        else:
            # Use last position for next positions
            x, y, dir = train_ids[id]
        # Calculate next positions
        x_new, y_new, dir_new = next_pos(id, x, y, action, dir, tracks)
        df_pos.loc[len(df_pos)] = [id, x_new, y_new, dir_new, t]
        train_ids[id] = (x_new, y_new, dir_new)
    return df_pos

def adjust_actions(df_pos, trains, df_actions, tracks):
    """Adjusts the actions, such that the paths' last positions match the station position.
    """
    global invalid_path
    changed = True
    last_train_for_print = None
    first_run = True
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
            
            # Check if an adjustment is needed
            if not (x_last == x_end and y_last == y_end) or invalid_path == train:
                invalid_path = None
                idxs = df_actions[df_actions['trainID'] == train].index
                idx_to_drop = idxs[0]
                df_actions.drop(index=idx_to_drop, inplace=True)
                df_actions.reset_index(drop=True, inplace=True)
                changed = True
                # Print progress
                if last_train_for_print != train:
                    if first_run:
                        print(f"> T{train}: ", end="")
                        first_run = False
                    else:
                        print(f"\n> T{train}: ", end="")
                    last_train_for_print = train
                print(".", end="", flush=True)
                # Break with change to rebuild df_pos
                break
        # Rebuild df_pos if change happened
        if changed:
            df_pos = build_df_pos(df_actions, trains, tracks)
    print()
    return df_actions, df_pos


def ensure_train_spawns(df_pos, trains):
    is_incomplete = False
    # Get missing trainIDs in df_pos
    missing_trains = set(trains["id"]) - set(df_pos["trainID"])
    for id in missing_trains:
        # Get info of missing train
        train_row = trains.loc[trains["id"] == id].iloc[0]
        x = train_row["x"]
        y = train_row["y"]
        dir_val = train_row["dir"]
        new_row = {
            "trainID": id,
            "x": x,
            "y": y,
            "dir": dir_val,
            "timestep": 0
        }
        x_end = train_row["x_end"]
        y_end = train_row["y_end"]
        if x != x_end and y != y_end:
            is_incomplete = True
        # Add new row to df_pos
        df_pos = pd.concat([df_pos, pd.DataFrame([new_row])], ignore_index=True)
    # Sort df_pos
    df_pos = df_pos.sort_values(by=["trainID", "timestep"]).reset_index(drop=True)
    if is_incomplete:
        print("⚠️ Validiation done with warning:\n"
              "The actions generated by Clingo might be invalid/incomplete.\n"
              "The afflicted agents will only spawn.\n"
              "You may inspect their actions in the \'ActErr Log\'."
        )
    else:
        print("✅ Valdidation done.")
    return df_pos


def beep_feedback():
    sys_platform = platform.system()
    if sys_platform == "Windows":
        import winsound
        winsound.Beep(600, 200)
        winsound.Beep(800, 250)
    elif sys_platform == "Darwin":  # macOS (system sound)
        subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
    else:  # Linux and other
        print('\a')


def get_start_pos(id, trains):
    x = trains.loc[trains["id"] == id, "x"].iloc[0]
    y = trains.loc[trains["id"] == id, "y"].iloc[0]
    dir = trains.loc[trains["id"] == id, "dir"].iloc[0]
    return x, y, dir


def next_pos(id, x, y, action, dir, tracks):
    # Direction change
    if action in ["move_forward", "move_left", "move_right"]:
        dir_new = dir_change(id, x, y, action, dir, tracks)
        x_new, y_new = pos_change(x, y, dir_new)
        return x_new, y_new, dir_new
    else:  # wait-action
        return x, y, dir


def dir_change(id, x, y, action, dir, tracks):
    global invalid_path, fw_tracks, to_left_tracks, to_right_tracks
    # Check, if coordinates are valid
    if not (0 <= y < len(tracks) and 0 <= x < len(tracks[0])):
        # Invalid: No dir change: path will be adjusted later
        if invalid_path == None:
            invalid_path = id
        return dir

    track = tracks[y][x]

    # Check for the action type, if current track allows direction change
    if action == "move_forward":
        if (dir, track) in fw_tracks:
            return fw_tracks[(dir, track)]
    elif action == "move_left":
        if (dir, track) in to_left_tracks:
            return to_left_tracks[(dir, track)]
        if invalid_path == None:
            invalid_path = id
    elif action == "move_right":
        if (dir, track) in to_right_tracks:
            return to_right_tracks[(dir, track)]
        if invalid_path == None:
            invalid_path = id
    # If track does not allow the action: No dir change: path will be adjusted later
    return dir


def pos_change(x, y, dir):
    if dir == 'n': y -= 1
    elif dir == 'e': x += 1
    elif dir == 's': y += 1
    elif dir == 'w': x -= 1
    return x, y


def write_act_err_txt(original, adjusted, trains):
    # Identify trains with invalid path
    act_err_trains = set(original["trainID"]) - set(adjusted["trainID"])
    if not act_err_trains:  # Empty ActErr log
        with open("data/act_err.txt", "w") as f, open("data/act_err_min.txt", "w") as f_min:
            f.write("")
            f_min.write("")
        return
    # Filter original actions for trains with invalid path with sorting
    df_act_err = original[original["trainID"].isin(act_err_trains)]
    df_act_err = df_act_err.sort_values(by=["trainID", "timestep"])
    # Write DF to act_err.txt
    os.makedirs("data", exist_ok=True)
    with open("data/act_err.txt", 'w') as f, open("data/act_err_min.txt", 'w') as f_min:
        # Write header for detailed file
        header = "ACT_ERR Overview\n" + \
                 "---------------------------------------------------------------\n" + \
                 "Clingonia provides a detailed overview\n" + \
                 "of actions generated by Clingo for trains\n" +\
                 "whose paths could not be visualized.\n\n" + \
                 "Clingonia's Findings:\n" + \
                 "Even after removing an arbitrary number of spawn moves,\n" + \
                 "the provided actions fail to guide the train\n" + \
                 "to its intended destination.\n" + \
                 "One exception: train spawns directly at its destination.\n\n" + \
                 "To allow you to verify that Clingonia is correct,\n" + \
                 "you can inspect the action predicates provided by Clingo below.\n" + \
                 "---------------------------------------------------------------\n\n\n"
        f.write(header)
        # Write header for reduced file
        f_min_additional_header = "* Please note that wait periods have been replaced with \'...\'\n" + \
                                  "* Format description: [action] ([timestep])\n\n\n"
        f_min.write(header)
        f_min.write(f_min_additional_header)
        
        for id in sorted(act_err_trains):
            # Train header information
            e_dep = trains.loc[trains["id"] == id, "e_dep"].iloc[0]
            l_arr = trains.loc[trains["id"] == id, "l_arr"].iloc[0]
            dir = trains.loc[trains["id"] == id, "dir"].iloc[0]
            x = trains.loc[trains["id"] == id, "x"].iloc[0]
            y = trains.loc[trains["id"] == id, "y"].iloc[0]
            x_end = trains.loc[trains["id"] == id, "x_end"].iloc[0]
            y_end = trains.loc[trains["id"] == id, "y_end"].iloc[0]

            # Train header
            f.write(f"=== Train {id} log:\n=== start({id},({y},{x}),{e_dep},{dir}) -> end({id},({y_end},{x_end}),{l_arr})\n")
            f_min.write(f"=== Train {id} log:\n=== ({y},{x},{dir}) -> ({y_end},{x_end})\n")
            
            # Filter for trainID
            df_train_actions = df_act_err[df_act_err["trainID"] == id]
            # Writing preparation
            wait_interruption = False
            prev_t = None
            missing_t = []
            for _, row in df_train_actions.iterrows():
                action = row["action"]
                t = row["timestep"]
                # Identify missing timesteps
                if prev_t != t-1 and prev_t is not None:
                    # Intervall of missing timesteps
                    gap = list(range(prev_t + 1, t))
                    # If over 2 timesteps are missing, summarize as interval
                    if len(gap) > 2:
                        missing_t.append(f"{gap[0]}-{gap[-1]}")
                    else:
                        missing_t.extend(gap)
                prev_t = t
                # Write log
                f.write(f"action(train({id}),{action},{t}).\n")
                if action != "wait":
                    f_min.write(f"{action} ({t})\n")
                    wait_interruption = False
                elif not wait_interruption:
                    wait_interruption = True
                    f_min.write(f"...\n")
            # Write list of missing timesteps
            if missing_t:
                missing_str = "[" + ", ".join(str(x) for x in missing_t) + "]"
                f.write(f"=== Train {id} - Missing Timesteps: {missing_str}\n\n\n")
                f_min.write(f"=== Train {id} - Missing Timesteps: {missing_str}\n\n\n")
            else:
                f.write(f"=== Train {id} has no missing timesteps.\n\n\n")
                f_min.write(f"=== Train {id} has no missing timesteps.\n\n\n")
