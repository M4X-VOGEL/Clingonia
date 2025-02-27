import os
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
from flatland.utils.rendertools import RenderTool
from code.build_png import create_custom_env, pil_config
from code.config import DIR_MAP

images = []  # Frame list for GIF

# Re-rendering parameters
old_env_counter = 0  # Detector for environment change
old_low_q = None  # Detector for quality change

def build_gif_from_frames(output_gif, fps):
    """Saves the collected frames as a GIF.

    Args:
        output_gif (str): File path to save the GIF.
        fps (float): Frames per second.
    """
    global images
    ms_per_timestep = int(1000/fps)
    # Save all frames in images as a GIF
    imageio.mimsave(output_gif, images, format='GIF', loop=0, duration=ms_per_timestep)


def calc_gif_resolution(low_quality_mode, env):
    """Calculates the screen resolution for GIF rendering based on environment size and quality mode.

    Args:
        low_quality_mode (bool): Flag to use low resolution settings.
        env (RailEnv or list): Environment object or 2D list of tracks.

    Returns:
        int: Screen resolution.
    """
    # Determine env dimensions based on input
    if isinstance(env, list):  # tracks list
        env_dim_max = max(len(env), len(env[0]))
    else:  # RailEnv object
        env_dim_max = max(env.height, env.width)
    screen_res = env_dim_max  # Base value is maximum dimension
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
    """Draws the current timestep at the bottom right of the image.

    Args:
        t (int): Current timestep.
        frame_filename (str): File path of the image frame to annotate.
    """
    with Image.open(frame_filename) as img:
        draw = ImageDraw.Draw(img)  # Drawing context
        text = f"{t}"  # Timestep as string
        font = ImageFont.load_default()
        # Use text bounding box for size and position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding = 2
        position = (img.width - text_width - padding, img.height - text_height - padding)
        draw.text(position, text, fill="black")  # Draw timestep
        img.save(frame_filename)  # Save modified image


def render_gif(tracks, trains, df_pos, env_params, env_counter, output_gif='data/running_tmp.gif', fps=2, low_quality_mode=False):
    """Creates an animated GIF of the environment by rendering each timestep or reusing cached frames.

    Args:
        tracks (list[list[int]]): 2D list of track types.
        trains (pd.DataFrame): Train configuration.
        df_pos (pd.DataFrame): Train positions.
        env_params (dict): Environment parameters.
        env_counter (int): Environment counter to detect changes.
        output_gif (str): File path to save the GIF.
        fps (float): Frames per second.
        low_quality_mode (bool): Flag for low resolution rendering.

    Returns:
        None if successful, or returns early if caching applies.
    """
    global images, old_env_counter, old_low_q
    # Check if env and quality stayed the same since last render
    if images and old_env_counter == env_counter and old_low_q == low_quality_mode:
        # No re-render needed: reuse cached frames
        build_gif_from_frames(output_gif, fps)
        return
    images = []
    print("\nRendering animation...")
    env,_,_,_ = create_custom_env(tracks, trains, env_params)  # Environment for rendering
    # Get timestep range to determine gif length
    min_timestep = int(df_pos['timestep'].min())
    max_timestep = int(df_pos['timestep'].max())
    print(f"{max_timestep-min_timestep+1} Timesteps to render.\nProgress:", end=" ")
    # Temporary directory to store gif frames
    tmp_dir = "data/tmp_frames"
    os.makedirs(tmp_dir, exist_ok=True)
    # Separate trains into groups
    groups = {id: group.sort_values(by='timestep') 
              for id, group in df_pos.groupby('trainID')}
    
    # Map IDs to their corresponding agent objects for custom id settings
    agent_by_id = {id: agent for id, agent in zip(trains['id'], env.agents)}
    
    # Loop over each timestep to render frame
    for t in range(min_timestep, max_timestep + 1):
        print(f"{t}", end=" ", flush=True)
        # For each train
        for id, group in groups.items():
            if id not in agent_by_id:
                continue  # Skip ID if there is no agent assigned
            agent = agent_by_id[id]
            row = group[group['timestep'] == t]  # Line of current timestep
            if row.empty:
                if env_params["remove"]:
                    # Remove train if data is missing and remove flag is set
                    agent.position = None
                    agent.direction = None
                continue
            else:
                row = row.iloc[0]  # Use the first matching row
            # Update train's position and direction
            agent.position = (int(row['y']), int(row['x']))
            agent.direction = DIR_MAP[row['dir']]
        
        # Render image
        if env.width * env.height > 1000000:
            low_quality_mode = True  # Force low quality on large environments
        screen_res = calc_gif_resolution(low_quality_mode, env)
        graphics_lib = "PIL" if low_quality_mode else "PILSVG"  # Rendering lib based on quality
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
        frame_filename = os.path.join(tmp_dir, f"frame_{t:04d}.png")  # Filename for current frame
        renderer.gl.save_image(frame_filename)
        renderer.reset()
        
        # Draw timestep on frame
        draw_timestep(t, frame_filename)
        # Add frame to list
        images.append(imageio.imread(frame_filename))
    
    # Combine frames into one GIF
    build_gif_from_frames(output_gif, fps)
    # Update caching parameters
    old_env_counter = env_counter
    old_low_q = low_quality_mode
    print(f"\n✅ Animation done.")
