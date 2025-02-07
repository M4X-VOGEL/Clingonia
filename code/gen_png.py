import warnings
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen
from flatland.utils.rendertools import RenderTool
from flatland.envs.agent_utils import SpeedCounter
from flatland.envs.observations import GlobalObsForRailEnv
from flatland.envs.timetable_utils import Line

LAST_HINTS = None

def create_agents_from_train_stations(hints, num_agents, np_random):
    """Generates agents out of station information from hints.
    
    Args:
        hints (dict): 'train_stations', 'city_positions' und 'city_orientations'.
        num_agents (int): number of agents to be generated.
        np_random (np.random.RandomState): for reproducability.
    
    Returns:
        [tuple] Agent positions, directions und targets.
    """
    train_stations = hints['train_stations']
    if len(train_stations) < 2:  # Check for minimum of 2 cities
        raise ValueError("Mindestens zwei Städte benötigt, um Start- und Zielbahnhöfe zu unterscheiden.")
    
    agents_positions = []
    agents_directions = []
    agents_targets = []
    
    for agent_idx in range(num_agents):
        # Logic to determine start and end for agents.
        if agent_idx % 2 == 0:
            city_start = 0
            city_target = 1
        else:
            city_start = 1
            city_target = 0
        
        # Choose random station in each city
        start_station_idx = np_random.randint(0, len(train_stations[city_start]))
        target_station_idx = np_random.randint(0, len(train_stations[city_target]))
        
        start_station = train_stations[city_start][start_station_idx]
        target_station = train_stations[city_target][target_station_idx]
        
        # Station format: ((x, y),base_direction)
        start_position, base_direction = start_station
        target_position, _ = target_station
        
        # np.int64 to int
        agents_positions.append((int(start_position[0]), int(start_position[1])))
        agents_directions.append(base_direction)
        agents_targets.append((int(target_position[0]), int(target_position[1])))
    
    return agents_positions, agents_directions, agents_targets


def custom_sparse_line_generator(speed_ratio_map=None, seed=1):
    """Custom line generator to be able to generate agents.
    """
    base_line_gen = sparse_line_generator(speed_ratio_map, seed)

    def generator(rail, num_agents, hints, num_resets, np_random):
        global LAST_HINTS
        
        # When there are no hint, generate dummy hints.
        if hints is None or 'train_stations' not in hints or 'city_positions' not in hints or 'city_orientations' not in hints:
            hints = {
                'train_stations': [[((0, 0),)] for _ in range(1)],
                'city_positions': [(0, 0)],
                'city_orientations': [0]
            }
        LAST_HINTS = hints  # Save for DF

        # Agent generation based on stations
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


def extract_trains_from_hints(hints, num_agents, np_random):
    """Creates trains DF with the hints.
    
    Args:
        hints (dict).
        num_agents (int).
        np_random (np.random.RandomState).
    
    Returns:
        [pd.DataFrame] Agent configuration.
    """
    agents_positions, agents_directions, agents_targets = create_agents_from_train_stations(hints, num_agents, np_random)
    direction_map = {0: 'n', 1: 'e', 2: 's', 3: 'w'}
    data = {
        "id": list(range(num_agents)),
        "x": [pos[0] for pos in agents_positions],
        "y": [pos[1] for pos in agents_positions],
        "dir": [direction_map.get(d, 'unknown') for d in agents_directions],
        "x_end": [target[0] for target in agents_targets],
        "y_end": [target[1] for target in agents_targets],
        "e_dep": [1] * num_agents,  # Default value 1
        "l_arr": [200] * num_agents  # Default value 200
    }
    df = pd.DataFrame(data)
    return df


def create_env(env_params):
    """Creates environment based on parameters.
    
    Args:
        env_params (dict): Parameters for environment.
    
    Returns:
        [RailEnv] Environment.
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
    
    # Rail Generator
    rail_gen = sparse_rail_generator(
        max_num_cities=env_params['cities'],
        seed=used_seed,
        grid_mode=env_params['grid'],
        max_rails_between_cities=env_params['intercity'],
        max_rail_pairs_in_city=env_params['incity']
    )

    # Custom Line Generator
    line_gen = custom_sparse_line_generator(env_params['speed'], used_seed)

    observation_builder = GlobalObsForRailEnv()
    
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

    obs, info = env.reset()  # obs and info only necessary for correct agent initilization
    
    # Ensure that agents have positions
    if any(agent.position is None for agent in env.agents):
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
                    agent.direction = allowed_dirs[random.randint(0, len(allowed_dirs)-1)]
            # No allowed directions: get city orientation
            else:
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


def get_allowed_dirs(track):
    # No track
    if track == 0: return []
    # List for allowed directions
    allowed_dirs = []
    # All tracks
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
    # Fill allowed directions
    if track in tracks_to_n: allowed_dirs.append(0)
    if track in tracks_to_e: allowed_dirs.append(1)
    if track in tracks_to_s: allowed_dirs.append(2)
    if track in tracks_to_w: allowed_dirs.append(3)
    return allowed_dirs


def gen_env(env_params, low_quality_mode=False):
    """Creates environment and corresponding png.
    
    Args:
        env_params (dict): Parameters for environment.
        low_quality_mode (bool): Low image resolution setting.
    
    Returns:
        [list]: tracks
        [pd.DataFrame]: trains
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        print("\nGenerating environment...")
        try:
            # Environment, Tracks, Trains
            env = create_env(env_params)
            tracks = extract_tracks(env)
            trains = extract_trains(env)
            if trains.empty:
                # Use hints
                np_random = np.random.RandomState(seed=env_params['seed'])
                trains = extract_trains_from_hints(LAST_HINTS, env_params['agents'], np_random)
            # Render
            screen_res = calc_resolution(low_quality_mode, tracks)
            renderer = RenderTool(env, screen_height=screen_res, screen_width=screen_res)
            renderer.render_env(show=False)
            # Save image
            image_data = renderer.get_image()
            path = "data/running_tmp.png"
            plt.imsave(path, image_data)
            print("✅ Environment generated.")
        except OverflowError as e:
            print("❌ Environment could not be generated.")
            return -1, -1
    return tracks, trains


def extract_tracks(env):
    tracks = []
    for row in range(env.height):
        track_row = []
        for col in range(env.width):
            transition = env.rail.get_full_transitions(row, col)
            track_row.append(transition)
        tracks.append(track_row)
    tracks = [[int(cell) for cell in row] for row in tracks]
    return tracks


def extract_trains(env):
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
            trains_data["e_dep"].append(1)  # Default value 1
            trains_data["l_arr"].append(200)  # Default value 200
    trains_df = pd.DataFrame(trains_data)
    return trains_df


def calc_resolution(low_quality_mode, env):
    if isinstance(env, list):  # tracks list
        env_dim_max = max(len(env), len(env[0]))
    else:  # RailEnv object
        env_dim_max = max(env.height, env.width)
    screen_res = env_dim_max  # Base value
    if low_quality_mode:  # Low
        if env_dim_max > 1000: screen_res = 4000
        elif env_dim_max > 160: screen_res *= 4
        else: screen_res *= 9
    else:  # Automatic
        if env_dim_max > 1000: screen_res = 9000
        elif env_dim_max > 160: screen_res *= 9
        elif env_dim_max > 120: screen_res *= 12
        elif env_dim_max > 100: screen_res *= 15
        elif env_dim_max > 80: screen_res *= 18
        elif env_dim_max > 50: screen_res *= 20
        elif env_dim_max > 30: screen_res *= 30
        elif env_dim_max > 20: screen_res *= 50
        elif env_dim_max > 10: screen_res *= 100
        elif env_dim_max > 5: screen_res *= 150
        else: screen_res *= 300
    return screen_res
