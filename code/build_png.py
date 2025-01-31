import numpy as np
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import rail_from_grid_transition_map
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen
from flatland.utils.rendertools import RenderTool
from flatland.core.transition_map import GridTransitionMap

# Numeric directions
DIR_MAP = {'n': 0, 'e': 1, 's': 2, 'w': 3}

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
        agent.direction = DIR_MAP[trains.loc[i, 'dir']]
        agent.initial_direction = agent.direction
        # Station
        row_target = trains.loc[i, 'y_end']
        col_target = trains.loc[i, 'x_end']
        agent.target = (row_target, col_target)

    return env


def save_png(env, path="data/running_tmp.png"):
    """Renders and saves the PNG-image.
    
    Args:
        env (RailEnv): Environment.
        path (str): Save location for the image.
    """
    # Render image
    renderer = RenderTool(env, gl="PILSVG")
    renderer.reset()
    renderer.render_env(
        show=True,
        show_observations=False,
        show_predictions=False
    )
    # Save image
    renderer.gl.save_image(path)
    renderer.reset()
