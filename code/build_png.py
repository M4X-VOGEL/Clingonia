import numpy as np
from code.gen_png import calc_resolution
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import rail_from_grid_transition_map
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen
from flatland.utils.rendertools import RenderTool
from flatland.core.transition_map import GridTransitionMap

# Numeric directions
DIR_MAP = {'n': 0, 'e': 1, 's': 2, 'w': 3}
# Direction change for improperly positioned trains
dir_replacement = {
    # Straights
    ('e', 32800):  's',
    ('w', 32800):  'n',
    ('n', 1025):  'e',
    ('s', 1025):  'w',
    # Curves
    ('s', 4608):  'e',
    ('w', 4608):  'n',
    ('s', 16386):  'w',
    ('e', 16386):  'n',
    ('n', 72):  'w',
    ('e', 72):  's',
    ('n', 2064):  'e',
    ('w', 2064):  's',
    # Switches
    ('w', 37408):  'n',
    ('s', 17411):  'w',
    ('e', 32872):  's',
    ('n', 3089):  'e',
    ('e', 49186):  'n',
    ('n', 1097):  'w',
    ('w', 34864):  's',
    ('s', 5633):  'e',
    # Split
    ('s', 20994):  'w',
    ('e', 16458):  's',
    ('n', 2136):  'e',
    ('w', 6672):  'n',
}

class DummyLine:
    """Line-Object expected by Flatland for line-generation.
    """
    # Essential attributes for agents
    def __init__(self, agent_positions, agent_targets, agent_directions, agent_speeds):
        self.agent_positions = agent_positions
        self.agent_targets = agent_targets
        self.agent_directions = agent_directions
        self.agent_speeds = agent_speeds

def dummy_line_generator(rail, num_agents, hints, *args, **kwargs):
    """Custom Line-Generator for creating a DummyLine.

    Args:
        rail (RailEnv): Reference for track network.
        num_agents (int): Number of agents.
        hints (dict): Extra information.
    """
    if hints is None:  # Flatland may expect hints
        hints = {}
    hints['train_stations'] = []  # Empty for now

    # Attribute placeholder
    agent_positions = [None] * num_agents
    agent_targets = [None] * num_agents
    agent_directions = [None] * num_agents
    agent_speeds = [1.0] * num_agents

    return DummyLine(agent_positions, agent_targets, agent_directions, agent_speeds)


class DummyObservationBuilder:
    """Observation-Builder with no actual observation expected by Flatland.
    """
    # Setting environment (Not in use)
    def set_env(self, env):
        pass

    # Resetting environment
    def reset(self, env=None): 
        pass

    # Single observation for one agent "handle" (Not in use)
    def get(self, handle=0):
        return None

    # For all observations at once (Not in use)
    def get_many(self, handles=None):
        if handles is None:
            handles = []
        return {h: None for h in handles}


def create_custom_env(tracks, trains, params):
    """Creates environment with specified tracks, trains and parameters for the PNG.

    Args:
        tracks (list): 2D-list of track-types.
        trains (pd.DataFrame): Train-configuration.
        params (dict): Environment parameters.
    
    Returns:
        [RailEnv]: Environment.
    """
    invalid_train = None
    invalid_station = None
    # Custom map
    grid_map = GridTransitionMap(params['rows'], params['cols'])
    grid_map.grid = np.array(tracks, dtype=np.uint16)

    # Generator
    rail_generator = rail_from_grid_transition_map(grid_map)

    # Malfunction
    malfunction_rate = params['malfunction'][0]
    malfunction_params = MalfunctionParameters(
        malfunction_rate=malfunction_rate,
        min_duration=params['min'],
        max_duration=params['max']
    )
    malfunction_generator = ParamMalfunctionGen(malfunction_params)

    # Environment
    env = RailEnv(
        width=params['cols'],
        height=params['rows'],
        rail_generator=rail_generator,
        line_generator=dummy_line_generator,
        number_of_agents=params['agents'],
        malfunction_generator=malfunction_generator,
        remove_agents_at_target=params['remove'],
        obs_builder_object=DummyObservationBuilder(),
        random_seed=params['seed']
    )
    env.reset()

    # Trains and stations
    for i, agent in enumerate(env.agents):
        # Train
        row_init = trains.loc[i, 'y']
        col_init = trains.loc[i, 'x']
        agent.initial_position = (row_init, col_init)
        agent.position = agent.initial_position
        # Direction
        dir = trains.loc[i, 'dir']
        train_track = tracks[row_init][col_init]
        if train_track == 0:
            invalid_train = i  # Report train not on track
            print(f"❌ Train {i} not on track.")
        # Redirect improperly oriented trains on tracks
        elif (dir, train_track) in dir_replacement:
            dir = dir_replacement[(dir, train_track)]
        trains.loc[i, 'dir'] = dir
        agent.direction = DIR_MAP[dir]
        agent.initial_direction = agent.direction
        # Station
        row_target = trains.loc[i, 'y_end']
        col_target = trains.loc[i, 'x_end']
        agent.target = (row_target, col_target)
        if row_target < 0 or col_target < 0:
            invalid_station = -(i+1)  # Report missing station
            print(f"❌ Missing Station of Train {i}.")
        else:
            station_track = tracks[row_target][col_target]
            if station_track == 0:
                invalid_station = i  # Report station not on track
                print(f"❌ Station of Train {i} not on track.")

    return env, trains, invalid_train, invalid_station


def initial_render_test():
    """Renders 1x1 environment with track, agent and station to validate the launch.
    
    Returns:
        [int] 0 if okay, else -1.
    """
    # Parameters
    tracks = [[1025]]
    params = {
        'rows': 1,
        'cols': 1,
        'agents': 1,
        'malfunction': (0.0,),
        'min': 1,
        'max': 1,
        'remove': False,
        'seed': 1,
    }
    # Transition map
    grid_map = GridTransitionMap(params['rows'], params['cols'])
    grid_map.grid = np.array(tracks, dtype=np.uint16)
    rail_generator = rail_from_grid_transition_map(grid_map)
    # Malfunction
    malfunction_params = MalfunctionParameters(
        malfunction_rate=0.0,
        min_duration=params['min'],
        max_duration=params['max']
    )
    malfunction_generator = ParamMalfunctionGen(malfunction_params)
    # Environment
    env = RailEnv(
        width=params['cols'],
        height=params['rows'],
        rail_generator=rail_generator,
        line_generator=dummy_line_generator,
        number_of_agents=params['agents'],
        malfunction_generator=malfunction_generator,
        remove_agents_at_target=params['remove'],
        obs_builder_object=DummyObservationBuilder(),
        random_seed=params['seed']
    )
    env.reset()
    # Agent and station
    agent = env.agents[0]
    agent.initial_position = (0, 0)
    agent.position = (0, 0)
    agent.direction = DIR_MAP['e']
    agent.initial_direction = agent.direction
    agent.target = (0, 0)
    # Test rendering
    renderer = RenderTool(env, gl="PILSVG")
    renderer.reset()
    renderer.render_env(
        show=True,
        show_observations=False,
        show_predictions=False
    )


def save_png(env, path="data/running_tmp.png", low_quality_mode=False):
    """Renders and saves the PNG-image.
    
    Args:
        env (RailEnv): Environment.
        path (str): Save location for the image.
    
    Returns:
        [int] if no error then 0, else 1.
    """
    print("Rendering image...")
    # Render image
    try:
        screen_res = calc_resolution(low_quality_mode, env)
        renderer = RenderTool(env, gl="PILSVG", screen_height=screen_res, screen_width=screen_res)
        renderer.reset()
        renderer.render_env(
            show=True,
            show_observations=False,
            show_predictions=False
        )
    except OverflowError as e:
        print("❌ Image could not be generated.")
        return -1
    # Save image
    renderer.gl.save_image(path)
    renderer.reset()
    print("✅ Build done.")
    return 0
