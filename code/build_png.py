from warnings import filterwarnings
import numpy as np
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import rail_from_grid_transition_map
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen
from flatland.utils.rendertools import RenderTool
from flatland.core.transition_map import GridTransitionMap
from code.config import DIR_MAP, AGENT_COLORS

filterwarnings("ignore", category=RuntimeWarning)

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


def calc_resolution(low_quality_mode, env):
    if isinstance(env, list):  # tracks list
        env_dim_max = max(len(env), len(env[0]))
    else:  # RailEnv object
        env_dim_max = max(env.height, env.width)
    screen_res = env_dim_max  # Base value
    if low_quality_mode:  # Low
        if env_dim_max > 1000: screen_res = 6000
        elif env_dim_max > 600: screen_res *= 6
        elif env_dim_max > 160: screen_res *= 9
        elif env_dim_max > 100: screen_res *= 12
        elif env_dim_max > 50: screen_res *= 18
        elif env_dim_max > 20: screen_res *= 30
        elif env_dim_max > 10: screen_res *= 50
        elif env_dim_max > 3: screen_res *= 100
        else: screen_res *= 200
    else:  # Automatic
        if env_dim_max > 1000: screen_res = 9000
        elif env_dim_max > 600: screen_res *= 9
        elif env_dim_max > 400: screen_res *= 12
        elif env_dim_max > 300: screen_res *= 15
        elif env_dim_max > 200: screen_res *= 18
        elif env_dim_max > 100: screen_res *= 30
        elif env_dim_max > 80: screen_res *= 40
        elif env_dim_max > 50: screen_res *= 50
        elif env_dim_max > 30: screen_res *= 80
        elif env_dim_max > 20: screen_res *= 100
        elif env_dim_max > 10: screen_res *= 200
        elif env_dim_max > 3: screen_res *= 300
        else: screen_res *= 400
    return screen_res


def pil_setup():
    try:
        from flatland.core.transition_map import Grid4Transitions
        if not hasattr(Grid4Transitions, "is_valid"):
            def is_valid(self, cell_transition):
                return cell_transition != 0
            Grid4Transitions.is_valid = is_valid
    except ImportError:
        pass


def pil_config(renderer):
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    custom_colors = [hex_to_rgb(c) for c in AGENT_COLORS]
    renderer.gl.agent_colors = custom_colors
    renderer.gl.n_agent_colors = len(custom_colors)
    
    # Custom colors for agents
    def custom_get_cmap(name, lut):
        def cmap(idx):
            return custom_colors[idx % len(custom_colors)]
        return cmap
    renderer.gl.get_cmap = custom_get_cmap

    # Remove elapsed time text
    original_text = renderer.gl.text
    def patched_text(x, y, text, *args, **kwargs):
        if text.startswith("elapsed:"):
            return
        return original_text(x, y, text, *args, **kwargs)
    renderer.gl.text = patched_text

    # Center agents
    original_plot_single_agent = renderer.renderer.plot_single_agent
    def centered_plot_single_agent(self, position_row_col, direction, color="r", target=None, static=False, selected=False):
        rt = self.__class__
        pos = np.array(position_row_col)
        if pos.ndim == 0 or pos.size == 0:
            return
        xyPos = np.matmul(pos, rt.row_col_to_xy) + rt.x_y_half
        if static:
            color = self.gl.adapt_color(color, lighten=True)
        # Agent size
        self.gl.scatter(*xyPos, color=color, layer=1, marker="o", s=16)
        direction_row_col = rt.transitions_row_col[direction]
        direction_xy = np.matmul(direction_row_col, rt.row_col_to_xy)
        xy_dir_line = np.array([xyPos, xyPos + direction_xy / 2]).T
        self.gl.plot(*xy_dir_line, color=color, layer=1, lw=5, ms=0, alpha=0.6)
        if selected:
            self._draw_square(xyPos, 1, color)
        if target is not None:
            target_row_col = np.array(target)
            target_xy = np.matmul(target_row_col, rt.row_col_to_xy) + rt.x_y_half
            self._draw_square(target_xy, 1/3, color, layer=1)
    renderer.renderer.plot_single_agent = centered_plot_single_agent.__get__(renderer.renderer, renderer.renderer.__class__)

    # Change color of cells with no track to canvas_color
    original_scatter = renderer.gl.scatter
    def patched_scatter(x, y, color, *args, **kwargs):
        if color == "r" and kwargs.get("s", None) == 30:
            color = "#313338"
            kwargs["s"] = 0
        return original_scatter(x, y, color, *args, **kwargs)
    renderer.gl.scatter = patched_scatter


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
    try:
        obs, info = env.reset()
    except ValueError as e:
        print("⚠️ Warning: No agents specified.")

    # Trains and stations
    for i, agent in enumerate(env.agents):
        id = trains.loc[i, 'id']
        # Train
        row_start = trains.loc[i, 'y']
        col_start = trains.loc[i, 'x']
        agent.initial_position = (row_start, col_start)
        agent.position = agent.initial_position
        # Direction
        dir = trains.loc[i, 'dir']
        train_track = tracks[row_start][col_start]
        if train_track == 0:
            invalid_train = id  # Report train not on track
            print(f"❌ Train {id} not on track.")
        # Redirect improperly oriented trains on tracks
        elif (dir, train_track) in dir_replacement:
            dir = dir_replacement[(dir, train_track)]
            print(f"⚠️ Train {id} at ({row_start},{col_start}): Invalid orientation corrected.")
        trains.loc[i, 'dir'] = dir
        agent.direction = DIR_MAP[dir]
        agent.initial_direction = agent.direction
        # Station
        row_target = trains.loc[i, 'y_end']
        col_target = trains.loc[i, 'x_end']
        agent.target = (row_target, col_target)
        if row_target < 0 or col_target < 0:
            invalid_station = -(i+1)  # Report missing station
            print(f"❌ Missing Station of Train {id}.")
        else:
            station_track = tracks[row_target][col_target]
            if station_track == 0:
                invalid_station = id  # Report station not on track
                print(f"❌ Station of Train {id} not on track.")


    return env, trains, invalid_train, invalid_station


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
        if env.width * env.height > 1000000:
            low_quality_mode = True
        screen_res = calc_resolution(low_quality_mode, env)
        graphics_lib = "PIL" if low_quality_mode else "PILSVG"
        renderer = RenderTool(env, gl=graphics_lib, screen_height=screen_res, screen_width=screen_res)
        renderer.reset()
        pil_config(renderer)
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


pil_setup()
