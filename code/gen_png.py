import math
import random
import warnings
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen
from flatland.envs.agent_utils import SpeedCounter
from flatland.envs.observations import GlobalObsForRailEnv
from flatland.envs.timetable_utils import Line
from flatland.utils.rendertools import RenderTool
from code.build_png import calc_resolution, pil_config
from code.config import TRACKS, DEAD_ENDS

LAST_HINTS = None

def create_agents_from_train_stations(hints, num_agents, np_random):
    """Generates agent positions, directions, and targets from station hints.

    Args:
        hints (dict): Contains 'train_stations', 'city_positions', and 'city_orientations'.
        num_agents (int): Number of agents to generate.
        np_random (np.random.RandomState): Random state for reproducibility.

    Returns:
        tuple: (agents_positions, agents_directions, agents_targets).
    """
    train_stations = hints['train_stations']
    
    agents_positions = []
    agents_directions = []
    agents_targets = []
    
    # Loop over agents to assign start and target stations
    for agent in range(num_agents):
        num_cities = len(train_stations)
        # City to start from
        start_city = np_random.randint(0, num_cities)
        # Target city
        possible_targets = list(range(num_cities))
        possible_targets.remove(start_city)
        target_city = np_random.choice(possible_targets)

        # Choose a station within both cities
        start_station_idx = np_random.randint(0, len(train_stations[start_city]))
        target_station_idx = np_random.randint(0, len(train_stations[target_city]))
        # Station information
        start_station = train_stations[start_city][start_station_idx]
        target_station = train_stations[target_city][target_station_idx]
        
        # Station format: ((x, y),base_direction)
        start_position, base_direction = start_station
        target_position, _ = target_station
        
        # Convert coordinates from np.int64 to int.
        agents_positions.append((int(start_position[0]), int(start_position[1])))
        agents_directions.append(base_direction)
        agents_targets.append((int(target_position[0]), int(target_position[1])))
    
    return agents_positions, agents_directions, agents_targets


def custom_sparse_line_generator(env_params, seed=1):
    """Creates a custom line generator for agent generation.

    Args:
        env_params (dict): Parameters for the environment.
        seed (int, optional): Random seed. Default is 1.

    Returns:
        function: Custom line generator function.
    """
    base_line_gen = sparse_line_generator(env_params["speed"], seed)

    def generator(rail, num_agents, hints, num_resets, np_random):
        global LAST_HINTS
        
        # When there are no hints, generate dummy hints.
        if hints is None or 'train_stations' not in hints or 'city_positions' not in hints or 'city_orientations' not in hints:
            hints = {
                'train_stations': [
                    [((0, 0), 0)],
                    [((env_params['cols']-1, env_params['rows']-1), 0)]
                ],
                'city_positions': [(0, 0), (env_params['cols']-1, env_params['rows']-1)],
                'city_orientations': [0, 0]
            }
        LAST_HINTS = hints  # Save for DF

        # Attempt to generate agents based on the provided hints.
        try:
            agents_positions, agents_directions, agents_targets = create_agents_from_train_stations(hints, num_agents, np_random)
            speeds = [1.0] * num_agents
            line = Line(agent_positions=agents_positions,
                        agent_directions=agents_directions,
                        agent_targets=agents_targets,
                        agent_speeds=speeds)
            return line
        except Exception as e:
            print("Agent generation failed:", e)
            # Use standard generator instead
            return base_line_gen.generate(rail, num_agents, hints, num_resets, np_random)

    return generator


def extract_trains_from_hints(hints, np_random, env_params):
    """Creates a DataFrame of train configuration using station hints.

    Args:
        hints (dict): Station information.
        np_random (np.random.RandomState): Random state for reproducibility.
        env_params (dict): Environment parameters.

    Returns:
        pd.DataFrame: Train configuration.
    """
    num_agents = env_params["agents"]
    agents_positions, agents_directions, agents_targets = create_agents_from_train_stations(hints, num_agents, np_random)
    direction_map = {0: 'n', 1: 'e', 2: 's', 3: 'w'}
    # Default for Lastest Arrival based on Dimensions and number of Agents
    l_arr = math.ceil(3 * max(env_params['rows'], env_params['cols'])) + 2 * num_agents
    # Construct a dictionary for DF columns.
    data = {
        "id": list(range(num_agents)),
        "x": [pos[0] for pos in agents_positions],
        "y": [pos[1] for pos in agents_positions],
        "dir": [direction_map.get(d, 'unknown') for d in agents_directions],
        "x_end": [target[0] for target in agents_targets],
        "y_end": [target[1] for target in agents_targets],
        "e_dep": [1] * num_agents,
        "l_arr": [l_arr] * num_agents 
    }
    df = pd.DataFrame(data)
    return df


def fallback_reset(env):
    """Performs a fallback reset on the environment if rail generation fails.

    Resets various environment internals to recover from grid errors.

    Args:
        env (RailEnv): Flatland environment.

    Returns:
        tuple: (obs, info) from reset.
    """
    print("Handling rail issues...")
    # Check if rail grid is missing
    if env.rail is None or env.rail.grid is None:
        raise RuntimeError("Grid was empty.")
    # Replace any negative values in the grid with 0
    if np.any(env.rail.grid < 0):
        env.rail.grid[env.rail.grid < 0] = 0
    # Reset agents
    env.reset_agents()
    env.agent_positions = np.zeros((env.height, env.width), dtype=int) - 1
    env._update_agent_positions_map(ignore_old_positions=False)
    # Reset information
    env.obs_builder.reset()
    env._elapsed_steps = 0
    env.dones = dict.fromkeys(list(range(env.get_num_agents())) + ["__all__"], False)
    # Get observations and environment information
    obs = env._get_observations()
    info = env.get_info_dict()
    return obs, info


def get_allowed_dirs(track):
    """Determines allowed directions for a given track type.

    Args:
        track (int): Track type.

    Returns:
        list[int]: Allowed direction codes (0: 'n', 1: 'e', 2: 's', 3: 'w').
    """
    # If there is no track, return an empty list
    if track == 0: return []
    # List for allowed directions
    allowed_dirs = []
    # Define track IDs that allow movement in each direction
    tracks_to_n = [32800, 4608, 16386, 37408,
                   17411, 32872, 49186, 34864,
                   5633, 33825, 38433, 50211,
                   33897, 35889, 38505, 52275,
                   20994, 16458, 6672]
    tracks_to_e = [1025, 4608, 2064, 37408,
                   17411, 3089, 1097, 34864,
                   5633, 33825, 38433, 50211,
                   33897, 35889, 38505, 52275,
                   20994, 2136, 6672]
    tracks_to_s = [32800, 72, 2064, 37408,
                   32872, 3089, 49186, 1097,
                   34864, 33825, 38433, 50211,
                   33897, 35889, 38505, 52275,
                   16458, 2136, 6672]
    tracks_to_w = [1025, 16386, 72, 17411,
                   32872, 3089, 49186, 1097,
                   5633, 33825, 38433, 50211,
                   33897, 35889, 38505, 52275,
                   20994, 16458, 2136]
    # Append numeric direction if track is in corresponding list
    if track in tracks_to_n: allowed_dirs.append(0)
    if track in tracks_to_e: allowed_dirs.append(1)
    if track in tracks_to_s: allowed_dirs.append(2)
    if track in tracks_to_w: allowed_dirs.append(3)
    return allowed_dirs


def validate_track(env, row, col):
    """Validates and adjusts the track transition for a given cell.

    Checks for dead-ends and known problematic track values.
    Replaces invalid or unknown track transitions with appropriate defaults,
    and updates the environment's grid accordingly.

    Args:
        env (RailEnv): Flatland environment.
        row (int): Row index of cell.
        col (int): Column index of cell.

    Returns:
        int: Validated track value.
    """
    transition = env.rail.get_full_transitions(row, col)
    # If track is a dead-end, replace it with a straight track
    if transition in DEAD_ENDS:
        print("> Dead-end at (" + str(row) + "," + str(col) + ") replaced.")
        if transition == 4 or transition == 256:
            transition = 1025
        else:
            transition = 32800
    # If the transition is non-zero but invalid, fix it
    elif transition != 0:
        if transition not in TRACKS:
            # Known problem cases
            if transition in {1285, 1281, 1029}:
                transition = 1025
            elif transition in {41120, 40992, 32928}:
                transition = 32800
            elif transition in {40996}:
                transition = 49186
            elif transition in {32932}:
                transition = 32872
            elif transition in {32804}:
                transition = 49186
            elif transition in {9473}:
                transition = 5633
            elif transition in {9221}:
                transition = 17411
            else:
                # Unknown problem cases
                print(f"> UNKNOWN: {transition} at ({row},{col}) removed.")
                transition = 0
            print(f"> Invalid track at ({row},{col}) replaced.")
    # Update env with validated transition
    env.rail.grid[row, col] = transition
    return int(transition)


def extract_tracks(env):
    """Extracts a 2D list of track types from the environment.

    Args:
        env (RailEnv): Flatland environment.

    Returns:
        list[list[int]]: 2D list representing track types for each cell.
    """
    tracks = []
    for row in range(env.height):
        track_row = []
        for col in range(env.width):
            # Validate track and add it to the row
            track = validate_track(env, row, col)
            track_row.append(track)
        # Append the row to the tracks list
        tracks.append(track_row)
    return tracks


def extract_trains(env):
    """Extracts train configuration from the environment.

    Args:
        env (RailEnv): Flatland environment.

    Returns:
        pd.DataFrame: DataFrame with columns ["id", "x", "y", "dir", "x_end", "y_end", "e_dep", "l_arr"].
    """
    trains_data = {
        "id": [],
        "x": [],
        "y": [],
        "dir": [],
        "x_end": [],
        "y_end": [],
        "e_dep": [],
        "l_arr": []
    }
    direction_map = {0: 'n', 1: 'e', 2: 's', 3: 'w'}
    # Default for Lastest Arrival based on Dimensions and number of Agents
    l_arr = math.ceil(3 * max(env.height, env.width)) + 2 * len(env.agents)
    # Agents
    for agent in env.agents:
        if agent.position is not None:
            trains_data["id"].append(agent.handle)
            trains_data["x"].append(agent.position[0])
            trains_data["y"].append(agent.position[1])
            trains_data["dir"].append(direction_map.get(agent.direction, 'unknown'))
            x_end, y_end = agent.target[0], agent.target[1]
            trains_data["x_end"].append(x_end)
            trains_data["y_end"].append(y_end)
            trains_data["e_dep"].append(1)
            trains_data["l_arr"].append(l_arr)
    # Create DF from train data
    trains_df = pd.DataFrame(trains_data)
    return trains_df


def seconds_to_str(seconds):
    """Converts seconds to a human-readable time string.

    Args:
        seconds (float): Time in seconds.

    Returns:
        str: Formatted time string.
    """
    # Round up to full seconds
    sec = math.ceil(seconds)
    if sec < 60:
        return f"{sec}s"
    elif sec < 3600:
        minutes = sec // 60
        sec = sec % 60
        return f"{minutes}m{sec}s"
    else:
        hours = sec // 3600
        remainder = sec % 3600
        minutes = remainder // 60
        sec = remainder % 60
        return f"{hours}h{minutes}m{sec}s"


def render_time_prediction(timesteps, cells):
    """Predicts rendering time based on timesteps and cell count.

    Args:
        timesteps (int): Number of timesteps.
        cells (int): Total number of cells in environment.

    Returns:
        str: Estimated render time as a formatted string.
    """
    # Estimate rendering time based on the total number of cells
    if cells < 30: sec = 1.2 * timesteps
    elif cells < 50: sec = 1.3 * timesteps
    elif cells < 80: sec = 1.4 * timesteps
    elif cells < 1180:
        # Runtime increases linearly from 80 to 1180
        sec = (1.4 + (cells-80) * 0.3/1100) * timesteps
    else:
        # Benchmark: 2.25 seconds runtime for 2000 cells
        # Runtime increases linearly by 25% every 1000 cells
        sec = 2.25 * (1 + 0.25 * ((cells-2000)/1000)) * timesteps
    # Convert estimated time to a formatted string
    return seconds_to_str(sec)


def create_env(env_params):
    """Creates a Flatland environment based on the provided parameters.

    Args:
        env_params (dict): Environment parameters.

    Returns:
        RailEnv: Generated Flatland environment.
    """
    used_seed = env_params['seed']
    random.seed(used_seed)
    
    # Malfunction
    mf1, mf2 = env_params['malfunction']
    malfunction_rate = (mf1/mf2) if mf2 != 0 else 0.0
    malfunction_params = MalfunctionParameters(
        malfunction_rate=malfunction_rate,
        min_duration=env_params['min'],
        max_duration=env_params['max']
    )
    malfunction_gen = ParamMalfunctionGen(parameters=malfunction_params)
    
    def rail_gen_test(width, height, number_of_agents, num_resets, np_random):
        try:
            # Attempt to generate rails using the original generator
            rail, optionals = rail_gen_original(width, height, number_of_agents, num_resets, np_random)
            return rail, optionals
        except Exception as e:
            print("Handling rail generator issues...")
            # If rail generation fails, incrementally increase the grid size.
            max_attempts = 5
            for i in range(1, max_attempts + 1):
                new_width = width + i
                new_height = height + i
                try:
                    rail, optionals = rail_gen_original(new_width, new_height, number_of_agents, num_resets, np_random)
                    break
                except Exception as e2:
                    if i == max_attempts:
                        raise e2  # Raise exception if all attempts fail
            # Trim the rail grid back to desired dimensions
            cropped_grid = rail.grid[:width, :height]
            rail.grid = cropped_grid
            return rail, optionals

    # Original Rail Generator
    rail_gen_original = sparse_rail_generator(
        max_num_cities=env_params['cities'],
        seed=used_seed,
        grid_mode=env_params['grid'],
        max_rails_between_cities=env_params['intercity'],
        max_rail_pairs_in_city=env_params['incity']
    )

    # Test Rail Generator
    rail_gen = rail_gen_test

    # Custom Line Generator
    line_gen = custom_sparse_line_generator(env_params, used_seed)

    observation_builder = GlobalObsForRailEnv()
    
    # Environment
    env = RailEnv(
        width=env_params['cols'],
        height=env_params['rows'],
        rail_generator=rail_gen,
        line_generator=line_gen,
        number_of_agents=env_params['agents'],
        obs_builder_object=observation_builder,
        malfunction_generator=malfunction_gen,
        remove_agents_at_target=False
    )

    try:
        obs, info = env.reset()
    except Exception as e:
        obs, info = fallback_reset(env)
    
    # Ensure that all agents have positions
    if any(agent.position is None or agent.position[0] < 0 or agent.position[1] < 0 for agent in env.agents):
        np_random = np.random.RandomState(seed=env_params['seed'])
        agents_positions, agents_directions, agents_targets = create_agents_from_train_stations(LAST_HINTS, env_params['agents'], np_random)
        for idx, agent in enumerate(env.agents):
            agent.position = agents_positions[idx]
            agent.direction = agents_directions[idx]
            agent.target = agents_targets[idx]
    # Speed
    for idx, agent in enumerate(env.agents):
        agent_speed = float(env_params['speed'].get(idx, 1.0))
        agent.speed_counter = SpeedCounter(speed=agent_speed)
    # Validate that initial agent direction matches with track
    for agent in env.agents:
        if agent.position is not None:
            row, col = agent.position
            # Track
            track = int(env.rail.get_full_transitions(row, col))
            # Get allowed direction of track
            allowed_dirs = get_allowed_dirs(track)
            # Set direction
            if allowed_dirs:
                if agent.direction not in allowed_dirs:
                    # Randomly assign a valid direction if current one is invalid
                    agent.direction = allowed_dirs[random.randint(0, len(allowed_dirs)-1)]
            else:
                # If no allowed directions, adjust using city orientation hints
                pos = (row, col)
                for city_idx, stations in enumerate(LAST_HINTS.get('train_stations', [])):
                    # Get station coordinates
                    station_coords = [ (int(s[0][0]), int(s[0][1])) for s in stations ]
                    if pos in station_coords:
                        # Use city_orientations.
                        desired_dir = LAST_HINTS.get('city_orientations', [])[city_idx]
                        if agent.direction != desired_dir:
                            agent.direction = desired_dir
                        break
    return env


def gen_env(env_params):
    """Generates a Flatland environment and saves a PNG of it.

    Args:
        env_params (dict): Parameters for environment.

    Returns:
        tuple: 2D list of track types and a DataFrame of train configuration,
               or error codes if generation fails.
    """
    # Suppress specific warnings during generation
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        print("\nGenerating environment...")
        try:
            # Environment, Tracks, Trains
            env = create_env(env_params)
            tracks = extract_tracks(env)
            trains = extract_trains(env)
            # If no trains are generated, use hints to extract trains
            if trains.empty:
                np_random = np.random.RandomState(seed=env_params['seed'])
                trains = extract_trains_from_hints(LAST_HINTS, np_random, env_params)
            # Render image
            est_render_time = render_time_prediction(1, env.height*env.width)
            print(f"Rendering image (~{est_render_time})...")
            if env.width * env.height > 1000000:
                low_quality_mode = True  # Force low quality on large environments
            else:
                low_quality_mode = env_params['lowQuality']
            screen_res = calc_resolution(low_quality_mode, tracks)
            graphics_lib = "PIL" if low_quality_mode else "PILSVG"  # Rendering lib based on quality
            renderer = RenderTool(env, gl=graphics_lib, screen_height=screen_res, screen_width=screen_res)
            if graphics_lib == "PIL":
                pil_config(renderer)
            renderer.render_env(show=False)
            # Save image
            image_data = renderer.get_image()
            path = "data/running_tmp.png"
            plt.imsave(path, image_data)
            print("✅ Environment generated.")
        except OverflowError as e:
            print(f"❌ Environment could not be generated:\n{e}")
            return -1, -1
        except Exception as e:
            print(f"❌ No Environment generated:\n{e}")
            return -2, -2

    return tracks, trains
