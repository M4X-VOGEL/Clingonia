import os
import pandas as pd
from code.config import TRACKS, DEAD_ENDS

def file_in_directory(path):
    """Checks whether a file exists at the given path.

    Args:
        path (str): File path.

    Returns:
        bool: True if file exists, False otherwise.
    """
    return os.path.isfile(path)


def add_global(pred):
    """Parses the global predicate and returns its MaxTime.

    Predicate format: global(MaxTime)

    Args:
        pred (str): Predicate string from the .lp file.

    Returns:
        int: passed maximum time or 100 if an error occurs.
    """
    # Extract maximum time number
    max_time = pred[7:-1]
    try:
        max_time = int(max_time)
        if max_time < 1:
            raise ValueError()
    except ValueError:
        print(f"⚠️ global(MaxTime) Warning: MaxTime must be a single integer greater than 0.")
        print(f"> automatically replaced by global(100).")
        max_time = 100
    return max_time


def add_cell(df_tracks, pred):
    """Parses a cell predicate and adds it as a row in the tracks DataFrame.

    Predicate format: cell((X,Y), Track)

    Args:
        df_tracks (pd.DataFrame): DataFrame to which the cell will be added.
        pred (str): Predicate string from the .lp file.

    Returns:
        int: 0 if successful; negative error code if an error occurs.
    """
    # Extract variables
    params = pred[5:-1]
    cell = params.replace('(', '').replace(')', '').split(',')
    if len(cell) != 3:
        return -2  # Report invalid cells
    
    # Add row to DF
    try:
        y, x = int(cell[0].strip()), int(cell[1].strip())
        if x < 0 or y < 0:
            print(f"❌ Error: Negative coordinates are not allowed.")
            return -12  # Report cells with negative coordinates
        track = int(cell[2].strip())
        # Check if track is a dead-end
        if track in DEAD_ENDS:
            print(f"❌ cell(({y},{x}),_) Dead end is not allowed.")
            return -14  # Report dead end
        # Check if track is invalid
        elif track not in TRACKS:
            track = 0  # Remove track and provide empty cell
            print(f"⚠️ cell(({y},{x}),_) Warning: Invalid track type was replaced by 0.")
    except ValueError:
        return -2  # Report invalid cells
    # Add cell data to DF
    df_tracks.loc[len(df_tracks)] = [x, y, track]
    return 0


def fill_tse(tse_list, pred):
    """Parses train, start, or end predicates and appends the information to tse_list.

    Expected formats:
        - train(ID)
        - start(ID, (X,Y), EarliestDeparture, Direction)
        - end(ID, (X,Y), LatestArrival)

    Args:
        tse_list (list): List to collect train, start, and end information.
        pred (str): Predicate string from the .lp file.

    Returns:
        int: 0 if successful; negative error code if an error occurs.
    """
    if pred.startswith("train"):
        # Extract variables
        params = pred[6:-1]
        train = [p.strip() for p in params.split(',')]
        if len(train) != 1:
            return -3  # Report invalid trains
        try:
            id = int(train[0])
            if id < 0:
                print(f"⚠️ train({id}) Warning: Invalid ID.")
                return -11  # Report invalid Train ID
        except ValueError:
            return -3  # Report invalid trains
        # Add ID to tse_list
        tse_list.append(id)

    elif pred.startswith("start"):
        # Extract variables
        params = pred[6:-1].replace('(', '').replace(')', '')
        start = [p.strip() for p in params.split(',')]
        if len(start) != 5:
            return -4  # Report invalid start
        try:
            id = int(start[0])
            y, x = int(start[1]), int(start[2])
            e_dep = int(start[3])
            dir = start[4]
            if e_dep < 0:
                print(f"⚠️ start({id},...) Warning: Earliest dep. < 0 changed to 1.")
                e_dep = 1
        except ValueError:
            return -4  # Report invalid start
        # Add start predicate to tse_list
        tse_list.append(["start", id, x, y, e_dep, dir])

    elif pred.startswith("end"):
        # Extract variables
        params = pred[4:-1].replace('(', '').replace(')', '')
        end = [p.strip() for p in params.split(',')]
        if len(end) != 4:
            return -5  # Report invalid end
        try:
            id = int(end[0])
            y_end, x_end = int(end[1]), int(end[2])
            l_arr = int(end[3])
            if l_arr < 1:
                print(f"⚠️ end({id},...) Warning: Latest arr. < 1 not allowed.")
                return -13  # Report invalid LatestArrival
        except ValueError:
            return -5  # Report invalid end
        # Add end predicate to tse_list
        tse_list.append(["end", id, x_end, y_end, l_arr])
    return 0


def prep_tracks_and_trains(path):
    """Parses an .lp file to prepare track and train information.

    Reads the file line by line, splits predicates, and collects:
        - DataFrame of cell predicates.
        - List of train, start, and end predicates.

    Args:
        path (str): Path to .lp file.

    Returns:
        triple: (df_tracks, tse_list, global_max_time) if successful,
                or (error_code, error_code) on error.
    """
    df_tracks = pd.DataFrame(columns=["x", "y", "track"])
    tse_list = []  # list to collect train, start, end
    global_max_time = 100  # Default value for global(MaxTime)
    with open(path, 'r') as lp:
        for line in lp:
            # Separate every predicate of the line
            predicates = line.strip().split('.')
            for pred in predicates:
                pred = pred.strip()
                if not pred: continue  # Skip empty lines
                elif "%" in pred: break  # Skip comments
                # global
                elif pred.startswith("global"):
                    global_max_time = add_global(pred)
                # cell
                elif pred.startswith("cell"):
                    rc = add_cell(df_tracks, pred)
                    if rc != 0: return rc, rc  # Error -2
                # train, start, end
                else:
                    rc = fill_tse(tse_list, pred)
                    if rc != 0: return rc, rc  # Error -3,-4,-5
    # Sort by y, then x in ascending order
    df_tracks = df_tracks.sort_values(by=['y', 'x'], ascending=[True, True])
    return df_tracks, tse_list, global_max_time


def create_list_of_tracks(df_tracks):
    """Converts the tracks DataFrame into a 2D list representation.

    Args:
        df_tracks (pd.DataFrame): Cell information.

    Returns:
        list[list[int]]: 2D list of track types.
    """
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
    """Creates a DataFrame of train configuration from predicate data.

    Args:
        tse_list (list): Train, start, and end predicates.

    Returns:
        pd.DataFrame: DataFrame with columns [id, x, y, dir, x_end, y_end, e_dep, l_arr].
    """
    # List of trainIDs
    train_ids = sorted([p for p in tse_list if isinstance(p, int)])
    # Dictionaries for start and end
    start_dict, end_dict = {}, {}
    for p in tse_list:
        if isinstance(p, list):
            if p[0] == 'start':
                start_dict[p[1]] = p
            elif p[0] == 'end':
                end_dict[p[1]] = p
    
    trains = pd.DataFrame(columns=["id", "x", "y", "dir", "x_end", "y_end", "e_dep", "l_arr"])
    # For each ID, add it if both start and end exist
    for id in train_ids:
        if id not in start_dict or id not in end_dict:
            continue  # Skip trains without start and/or end
        # start variables
        s = start_dict[id]
        x, y = s[2], s[3]
        e_dep, dir = s[4], s[5]
        # end variables
        e = end_dict[id]
        x_end, y_end = e[2], e[3]
        l_arr = e[4]
        # Add row
        trains.loc[len(trains)] = [id, x, y, dir, x_end, y_end, e_dep, l_arr]
    return trains


def validate_direction(direction):
    """Validates the direction string.

    Args:
        direction (str): Direction value.

    Returns:
        int: 0 if valid; -6 if invalid.
    """
    allowed = ['n', 'e', 's', 'w']
    if direction not in allowed:
        return -6
    return 0


def validate_cell_with_track_exists(x, y, df_tracks):
    """Checks if a cell at the given coordinates exists and has a track.

    Args:
        x (int): x-coordinate.
        y (int): y-coordinate.
        df_tracks (pd.DataFrame): Cell information.

    Returns:
        int: 0 if cell exists; -8 if cell is missing.
    """
    # Check if cell with given x, y exists
    condition = (df_tracks['x'] == x) & (df_tracks['y'] == y)
    if not condition.any():
        return -8  # Report non-existant cell
    # Extract track
    track = df_tracks.loc[condition, 'track'].iloc[0]
    if track == 0:
        print(f"⚠️ cell({y},{x},{track}) Warning: Train or Station not on a track.")
    return 0


def validate_train_consistency(tse_list):
    """Ensures that every train has both a start and an end, and that LatestArrival is not before EarliestDeparture.

    Args:
        tse_list (list): Train, start, and end predicates.

    Returns:
        int: 0 if consistent; negative error code otherwise.
    """
    train_ids = set()
    start_dict = {}
    end_dict = {}

    # Process each predicate
    for pred in tse_list:
        if isinstance(pred, int):  # train
            train_ids.add(pred)
        elif isinstance(pred, list):  # start or end
            if pred[0] == 'start':
                # Check, if there is a train(ID) for this start(ID,...)
                if pred[1] not in train_ids:
                    print("⚠️ Warning: There is a start(ID,...) without train(ID).")
                    continue
                start_dict[pred[1]] = pred
            elif pred[0] == 'end':
                # Check, if there is a train(ID) for this end(ID,...)
                if pred[1] not in train_ids:
                    print("⚠️ Warning: There is an end(ID,...) without train(ID).")
                    continue
                end_dict[pred[1]] = pred
    
    # Check that every train has both start and end predicate
    for id in train_ids:
        # Every train needs start and end
        if id not in start_dict or id not in end_dict:
            return -7
        # Latest arrival cannot be before earliest departure
        e_dep = start_dict[id][4]
        l_arr = end_dict[id][4]
        if l_arr < e_dep:
            return -9
    return 0


def validate_grid_completeness(df_tracks):
    """Checks whether a complete grid can be constructed from cell predicates.

    Returns:
        int: 0 if valid; -10 if any (X,Y) coordinate is missing.
    """
    if df_tracks.empty:
        print("⚠️ Warning: Grid is empty.")
        return -10

    # Determine the grid boundaries based on cell coordinates
    min_x = df_tracks['x'].min()
    max_x = df_tracks['x'].max()
    min_y = df_tracks['y'].min()
    max_y = df_tracks['y'].max()

    # Check for missing cells
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if not ((df_tracks['x'] == x) & (df_tracks['y'] == y)).any():
                print(f"⚠️ Warning: cell({y},{x},_) missing.")
                return -10
    return 0


def validate(tse_list, df_tracks):
    """Validates predicate consistency, start directions, and grid completeness.

    Args:
        tse_list (list): Train, start, and end predicates.
        df_tracks (pd.DataFrame): Cell predicates.

    Returns:
        int: 0 if valid; negative error code if invalid.
    """
    # For each predicate
    for pred in tse_list:
        if isinstance(pred, list):
            # Check start direction and coordinates
            if pred[0] == 'start':
                # Direction
                rc = validate_direction(pred[5])
                if rc != 0:
                    return rc
                # Coordinates
                rc = validate_cell_with_track_exists(pred[2], pred[3], df_tracks)
                if rc != 0:
                    return rc
            # Check end coordinates
            elif pred[0] == 'end':
                # Coordinates
                rc = validate_cell_with_track_exists(pred[2], pred[3], df_tracks)
                if rc != 0:
                    return rc
    # Validate consistency of train(...), start(...), end(...)
    rc = validate_train_consistency(tse_list)
    if rc != 0:
        return rc
    # Validate grid completeness
    rc_grid = validate_grid_completeness(df_tracks)
    if rc_grid != 0:
        return rc_grid
    return 0


def load_env(lp_file):
    """Loads an environment from an .lp file by extracting tracks and train configuration.

    Args:
        lp_file (str): Path to .lp file containing ASP-encoded environment.

    Returns:
        triple: 2D list of track types, DataFrame with train configuration and global(MaxTime),
               or error codes if loading fails.
    """
    print(f"\nLoading environment {os.path.basename(lp_file)}...")
    if not file_in_directory(lp_file):
        print("❌ File Not Found Error: No environment loaded.")
        return -1, -1  # FileNotFoundError -1
    # Ensure the file has correct extension
    if not lp_file.endswith(".lp"):
        print("❌ Load Error: Environment must be a .lp file.")
        return -15, -15  # Report invalid file type
    # Assemble tracks DF and predicate list
    df_tracks, tse_list, global_max_time = prep_tracks_and_trains(lp_file)
    if isinstance(df_tracks, int) or isinstance(tse_list, int):
        print("❌ Load Error: No environment loaded.")
        return df_tracks, tse_list  # Errors -2,-3,-4,-5,-11,-12
    # Validation
    rc = validate(tse_list, df_tracks)
    if rc != 0:
        print("❌ Validation Error: No environment loaded.")
        return rc, rc  # Errors -6,-7,-8,-9,-10
    # Convert df_tracks into a 2D list and tse_list into a DF
    tracks = create_list_of_tracks(df_tracks)
    trains = create_df_of_trains(tse_list)
    return tracks, trains, global_max_time
