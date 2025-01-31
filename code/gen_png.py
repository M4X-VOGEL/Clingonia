import warnings
import random
import matplotlib.pyplot as plt
import pandas as pd
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen
from flatland.utils.rendertools import RenderTool
from flatland.envs.agent_utils import SpeedCounter

def create_env(env_params):
    """Creates environment based on parameters.
    
    Args:
        env_params (dict): Parameters for environment.

    Returns:
        [RailEnv] Environment.
    """
    # Seed
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
    
    # Generator
    # TODO: Add agents with an alternative generator
    rail_gen = sparse_rail_generator(
        max_num_cities=env_params['cities'],
        seed=used_seed,
        grid_mode=env_params['grid'],
        max_rails_between_cities=env_params['intercity']
    )
    line_gen = sparse_line_generator()
    
    # Environment
    env = RailEnv(
        width=env_params['cols'],
        height=env_params['rows'],
        rail_generator=rail_gen,
        line_generator=line_gen,
        number_of_agents=env_params['agents'],
        malfunction_generator=malfunction_gen
    )
    env.reset()
    
    # Speed
    for idx, agent in enumerate(env.agents):
        agent_speed = float(env_params['speed'].get(idx, 1.0))
        agent.speed_counter = SpeedCounter(speed=agent_speed)
    
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
        # Ignore warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        try:
            # Create environment
            env = create_env(env_params)
            # Tracks extraction
            tracks = extract_tracks(env)
            # Trains extraction
            trains = extract_trains(env)
            # Render image
            renderer = RenderTool(env, screen_height=600, screen_width=600)
            renderer.render_env(show=False)
            # Save image
            image_data = renderer.get_image()
            path = "../data/running_tmp.png"
            plt.imsave(path, image_data)
            print(f"\n✅ Success! Environment generated.")
        except OverflowError as e:
            print(f"\n❌ No environment generated. Suggestions:")
            print("1. Grid Size: try at least 40 rows and 40 cols.")
            print("2. Grid-Mode: set to True.")
            print("3. Cities: reduce amount of cities.")
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
    
    # Numerical directions
    direction_map = {0: 'n', 1: 'e', 2: 's', 3: 'w'}
    
    for agent in env.agents:
        if agent.position is not None:
            trains_data["id"].append(agent.handle)
            trains_data["x"].append(agent.position[0])
            trains_data["y"].append(agent.position[1])
            trains_data["dir"].append(direction_map.get(agent.direction, 'unknown'))
            # Train stations
            x_end, y_end = agent.target[0], agent.target[1]
            trains_data["x_end"].append(x_end)
            trains_data["y_end"].append(y_end)
            # Default values for e_dep and l_arr
            trains_data["e_dep"].append(1)
            trains_data["l_arr"].append(200)
    
    trains_df = pd.DataFrame(trains_data)
    return trains_df
