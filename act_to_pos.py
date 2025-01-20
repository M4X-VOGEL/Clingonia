import pandas as pd
import csv

output_file = "data/positions.csv"

actions_file = "data/action_params.csv"
df_actions = pd.read_csv(actions_file)
df_actions = df_actions.sort_values(by=["trainID", "timestep"], ascending=[True, True])

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
    "dir": ['s','n']
})
###

def act_to_pos():

    with open(output_file, mode='w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')

        # Write CSV Headers
        writer.writerow(["trainID", 'x', 'y', "dir", "timestep"])

        # Train IDs
        train_ids = []

        # Position for each action
        for i, row in df_actions.iterrows():
            id = row['trainID']
            action = row["action"]
            t = row["timestep"]

            # Write start position when reaching new ID
            if id not in train_ids:
                x, y, dir = get_start_pos(id)
                writer.writerow([id, x, y, dir, t-1])
                train_ids.append(id)

            # Following Positions
            x, y, dir = next_pos(x, y, action, dir)
            writer.writerow([id, x, y, dir, t])


def get_start_pos(train_id):
    x = trains[trains["id"] == train_id]["x"].values[0]
    y = trains[trains["id"] == train_id]["y"].values[0]
    dir = trains[trains["id"] == train_id]["dir"].values[0]
    return x, y, dir


def next_pos(x, y, action, dir):
    # Direction change
    if action in ["move_forward", "move_left", "move_right"]:
        dir_new = dir_change(x, y, action, dir)
        x_new, y_new = pos_change(x, y, dir_new)
    else:  # wait-action
        return x, y, dir
    return x_new, y_new, dir_new
    

def dir_change(x, y, action, dir):
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


# Call
act_to_pos()
