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
            print("Custom agent generation failed:", e)
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
    _, mf_max = env_params['malfunction']
    malfunction_rate = (1.0 / mf_max) if mf_max != 0 else 0.0
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
    
    # Validation that the agent direction matches with the track
    for agent in env.agents:
        if agent.position is not None:
            row, col = agent.position
            transitions = env.rail.get_full_transitions(row, col)
            # Get allowed direction of the cell
            if isinstance(transitions, np.ndarray):
                allowed_dirs = [d for d in range(4) if np.any(transitions[d])]
            elif isinstance(transitions, (int, np.integer)):
                allowed_dirs = [d for d in range(4) if ((transitions >> d) & 1) == 1]
            else:
                allowed_dirs = []
            # Straight tracks
            if sorted(allowed_dirs) == [0, 2]:
                if agent.direction not in [0, 2]:
                    agent.direction = 0
            elif sorted(allowed_dirs) == [1, 3]:
                if agent.direction not in [1, 3]:
                    agent.direction = 1
            # Stationary cell with no transitions
            if not allowed_dirs:
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
    """Creates environment and corresponding png.
    
    Args:
        env_params (dict): Parameters for environment.
    
    Returns:
        [list]: tracks
        [pd.DataFrame]: trains
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
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
            renderer = RenderTool(env, screen_height=600, screen_width=600)
            renderer.render_env(show=False)
            # Save image
            image_data = renderer.get_image()
            path = "data/running_tmp.png"
            plt.imsave(path, image_data)
            print("\n✅ Success! Environment generated.")
        except OverflowError as e:
            print("\n❌ No environment generated. Suggestions:")
            print("1. Grid Size: try at least 40 rows and 40 cols.")
            print("2. Grid-Mode: set to True.")
            print("3. Cities: reduce amount of cities.")
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
