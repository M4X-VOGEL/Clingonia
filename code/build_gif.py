import os
import imageio.v2 as imageio
from flatland.utils.rendertools import RenderTool
from PIL import Image, ImageDraw, ImageFont
from code.build_png import create_custom_env

DIR_MAP = {'n': 0, 'e': 1, 's': 2, 'w': 3}

def build_gif(tracks, trains, df_pos, env_params, output_gif='data/running_tmp.gif', low_quality_mode=False):
    """Creates the gif of the environment with a frame for every timestep.
    
    Args:
        tracks (list): environment 2D-list of the tracks.
        trains (pd.DataFrame): train configuration.
        df_pos (pd.DataFrame): train positions.
        env_params (dict): user input parameters.
        output_gif (str): path for gif.
        low_quality_mode (int): False for auto resolution; True for low resolution.
    """
    print("\nRendering animation...")
    env = create_custom_env(tracks, trains, env_params)
    # Get max timesteps to determine gif length
    max_timestep = int(df_pos['timestep'].max())
    print(f"{max_timestep+1} Timesteps to render.\nProgress:", end=" ")
    # Directory for gif frames
    tmp_dir = "data/tmp_frames"
    os.makedirs(tmp_dir, exist_ok=True)
    # Separate trains into groups
    groups = {train_id: group.sort_values(by='timestep') 
              for train_id, group in df_pos.groupby('trainID')}
    # Frame list
    images = []
    
    # For each timestep
    for t in range(0, max_timestep + 1):
        print(f"{t}", end=" ", flush=True)
        # For each agent
        for i, agent in enumerate(env.agents):
            if i in groups:
                group = groups[i]
                # Get row with corresponding timestep
                row = group[group['timestep'] == t]
                if row.empty:
                    if env_params["remove"]:
                        # Remove agents
                        agent.position = None
                        agent.direction = None
                    continue
                else:
                    row = row.iloc[0]
                # Update position and direction
                agent.position = (int(row['y']), int(row['x']))
                agent.direction = DIR_MAP[row['dir']]
        
        # Render
        screen_res = calc_gif_resolution(low_quality_mode, env)
        renderer = RenderTool(env, gl="PILSVG", screen_height=screen_res, screen_width=screen_res)
        renderer.reset()
        renderer.render_env(show=False, show_observations=False, show_predictions=False)

        # Save tmp frames
        frame_filename = os.path.join(tmp_dir, f"frame_{t:04d}.png")
        renderer.gl.save_image(frame_filename)
        renderer.reset()
        
        # Draw timestep counter
        draw_timestep(t, frame_filename)
        # Add frame to list
        images.append(imageio.imread(frame_filename))
    
    # Combine frames to one GIF
    imageio.mimsave(output_gif, images, format='GIF', loop=0, duration=500)
    print(f"\n✅ Animation done.")


def calc_gif_resolution(low_quality_mode, env):
    if isinstance(env, list):  # tracks list
        env_dim_max = max(len(env), len(env[0]))
    else:  # RailEnv object
        env_dim_max = max(env.height, env.width)
    screen_res = env_dim_max  # Base value
    if low_quality_mode:  # Low
        if env_dim_max > 1000: screen_res = 2000
        elif env_dim_max > 500: screen_res *= 2
        elif env_dim_max > 10: screen_res *= 9
        else: screen_res *= 18
    else:  # Automatic
        if env_dim_max > 350: screen_res = 3000
        elif env_dim_max > 50: screen_res *= 9
        elif env_dim_max > 10: screen_res *= 18
        else: screen_res *= 100
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
