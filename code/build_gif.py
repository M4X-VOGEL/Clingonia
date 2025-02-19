import os
import imageio.v2 as imageio
from flatland.utils.rendertools import RenderTool
from PIL import Image, ImageDraw, ImageFont
from code.build_png import create_custom_env, pil_config

DIR_MAP = {'n': 0, 'e': 1, 's': 2, 'w': 3}
images = []  # Frame list
# Re-rendering parameters
old_env_counter = 0
old_low_q = None

def render_gif(tracks, trains, df_pos, env_params, env_counter, output_gif='data/running_tmp.gif', fps=2, low_quality_mode=False):
    """Creates the gif of the environment with a frame for every timestep.
    
    Args:
        tracks (list): environment 2D-list of the tracks.
        trains (pd.DataFrame): train configuration.
        df_pos (pd.DataFrame): train positions.
        env_params (dict): user input parameters.
        output_gif (str): path for gif.
        fps (float): timesteps per second.
        low_quality_mode (int): False for auto resolution; True for low resolution.
    """
    global images, old_env_counter, old_low_q
    if images and old_env_counter == env_counter and old_low_q == low_quality_mode:
        # Same environment, same quality: no re-render needed
        build_gif_from_frames(output_gif, fps)
        return
    images = []
    print("\nRendering animation...")
    env,_,_,_ = create_custom_env(tracks, trains, env_params)
    # Get timestep range to determine gif length
    min_timestep = int(df_pos['timestep'].min())
    max_timestep = int(df_pos['timestep'].max())
    print(f"{max_timestep+1} Timesteps to render.\nProgress:", end=" ")
    # Directory for gif frames
    tmp_dir = "data/tmp_frames"
    os.makedirs(tmp_dir, exist_ok=True)
    # Separate trains into groups
    groups = {id: group.sort_values(by='timestep') 
              for id, group in df_pos.groupby('trainID')}
    
    # Mapping to handle custom id settings
    agent_by_id = {id: agent for id, agent in zip(trains['id'], env.agents)}
    
    # For each timestep
    for t in range(min_timestep, max_timestep + 1):
        print(f"{t}", end=" ", flush=True)
        # For each agent
        for id, group in groups.items():
            # Skip ID if there is no agent assigned
            if id not in agent_by_id:
                continue
            agent = agent_by_id[id]
            # Line of current timestep
            row = group[group['timestep'] == t]
            if row.empty:
                if env_params["remove"]:
                    # Remove if there data is missing
                    agent.position = None
                    agent.direction = None
                continue
            else:
                row = row.iloc[0]
            # Position and direction
            agent.position = (int(row['y']), int(row['x']))
            agent.direction = DIR_MAP[row['dir']]
        
        # Render image
        if env.width * env.height > 1000000:
            low_quality_mode = True
        screen_res = calc_gif_resolution(low_quality_mode, env)
        graphics_lib = "PIL" if low_quality_mode else "PILSVG"
        renderer = RenderTool(env, gl=graphics_lib, screen_height=screen_res, screen_width=screen_res)
        renderer.reset()
        if graphics_lib == "PIL":
            pil_config(renderer)
        renderer.render_env(
            show=False,
            show_observations=False,
            show_predictions=False
        )
        # Save tmp frames
        frame_filename = os.path.join(tmp_dir, f"frame_{t:04d}.png")
        renderer.gl.save_image(frame_filename)
        renderer.reset()
        
        # Draw timestep counter
        draw_timestep(t, frame_filename)
        # Add frame to list
        images.append(imageio.imread(frame_filename))
    
    # Combine frames to one GIF
    build_gif_from_frames(output_gif, fps)
    old_env_counter = env_counter
    old_low_q = low_quality_mode
    print(f"\n✅ Animation done.")


def build_gif_from_frames(output_gif, fps):
    global images
    ms_per_timestep = int(1000/fps)
    imageio.mimsave(output_gif, images, format='GIF', loop=0, duration=ms_per_timestep)


def calc_gif_resolution(low_quality_mode, env):
    if isinstance(env, list):  # tracks list
        env_dim_max = max(len(env), len(env[0]))
    else:  # RailEnv object
        env_dim_max = max(env.height, env.width)
    screen_res = env_dim_max  # Base value
    if low_quality_mode:  # Low
        if env_dim_max > 1000: screen_res = 6000
        elif env_dim_max > 100: screen_res *= 6
        elif env_dim_max > 50: screen_res *= 9
        elif env_dim_max > 20: screen_res *= 12
        elif env_dim_max > 10: screen_res *= 24
        elif env_dim_max > 3: screen_res *= 40
        else: screen_res *= 150
    else:  # Automatic
        if env_dim_max > 1200: screen_res = 8000
        elif env_dim_max > 800: screen_res *= 6
        elif env_dim_max > 160: screen_res *= 9
        elif env_dim_max > 100: screen_res *= 12
        elif env_dim_max > 80: screen_res *= 18
        elif env_dim_max > 50: screen_res *= 20
        elif env_dim_max > 20: screen_res *= 50
        elif env_dim_max > 10: screen_res *= 100
        elif env_dim_max > 3: screen_res *= 200
        else: screen_res *= 300
    return screen_res


def draw_timestep(t, frame_filename):
    with Image.open(frame_filename) as img:
        draw = ImageDraw.Draw(img)
        text = f"{t}"
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding = 2
        position = (img.width - text_width - padding, img.height - text_height - padding)
        draw.text(position, text, fill="black")
        img.save(frame_filename)
