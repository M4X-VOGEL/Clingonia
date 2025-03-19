import os
import time
import threading
import subprocess
import pandas as pd

# HERE YOU CAN ADD OPTIONS FOR THE CLINGO COMMAND LIKE "--stats" TO THE LIST.
clingo_options = []
# Be aware that some options may cause the program to malfunction.

clingo_frustration = {
    30:  "I'm lost in Flatland, again...",
    60:  "tracks won't align, damn it...",
    90:  "man, grass as far as the eye can see...",
    120: "grid's a mess...",
    150: "signals are dead, total blackout...",
    180: "routes are all screwed up...",
    210: "timetable's a mess...",
    240: "whoa, that flatland grass is lush!...",
    270: "trains just fired up!...",
    300: "numbers crashing, this is nuts!...",
    330: "hold on, that rail bend is fascinating!...",
    360: "give me a break, man..."
}

clingo_finisher = {
    1: "Boom! Finished faster than I thought!",
    2: "Done! But these rails had me burning!",
    3: "All that sweat, tears, and blood truly paid off!",
    4: "Finally done! Clinging like a train on busted rails!",
    5: "Tracks laid, but what a ride! Victory's ours!"
}

def seconds_to_str(s):
    """Converts seconds to a human-readable time string.

    Args:
        s (int): Time in seconds.

    Returns:
        str: Formatted time string.
    """
    if s < 60:
        return f"{s}s"
    elif s < 3600:
        minutes = s // 60
        s = s % 60
        return f"{minutes}m{s}s" if s != 0 else f"{minutes}m"
    else:
        hours = s // 3600
        remainder = s % 3600
        minutes = remainder // 60
        s = remainder % 60
        return f"{hours}h{minutes}m{s}s" if s != 0 else f"{hours}h{minutes}m"


def run_clingo(clingo_path, lp_files, answer_number):
    """Runs Clingo on given ASP files and returns its output.

    Args:
        clingo_path (str): Path to Clingo installation.
        lp_files (list[str]): List of ASP files.
        answer_number (int): Desired answer number from Clingo.

    Returns:
        str: Clingo output with its answers, or -3 if Clingo returns an error.
    """
    timer_start = time.perf_counter()  # Timer for Clingo execution time

    # Run Clingo as a subprocess
    proc = subprocess.Popen(
        [clingo_path] + clingo_options + lp_files + [str(answer_number)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    # Timer-Thread to provide status updates while Clingo runs.
    def timer():
        counter, frustration = 30, 30  # Counters
        # Loop until the Clingo process terminates
        while proc.poll() is None:
            time.sleep(0.1)  # Sleep briefly to avoid busy waiting
            elapsed = int(time.perf_counter() - timer_start)
            if elapsed == counter:
                # Clingo updates
                t = seconds_to_str(counter)
                print(f"Clingo: \'{clingo_frustration[frustration]}\' ({t})")
                # Increase counters
                counter += 30
                frustration += 30
                if frustration > 360:
                    frustration = 30  # Loop Clingo quotes
        # Final message with total execution time
        execution_time = time.perf_counter() - timer_start
        if execution_time <= 30:
            pass
        elif execution_time <= 90:
            print(f"Clingo: '{clingo_finisher.get(1, '')}'")
        elif execution_time <= 300:
            print(f"Clingo: '{clingo_finisher.get(2, '')}'")
        elif execution_time <= 1200:
            print(f"Clingo: '{clingo_finisher.get(3, '')}'")
        elif execution_time <= 3600:
            print(f"Clingo: '{clingo_finisher.get(4, '')}'")
        else:
            print(f"Clingo: '{clingo_finisher.get(5, '')}'")
        print(f"🕓 Clingo ran for {execution_time:.2f}s.", flush=True)
    # Start timer thread to output periodic updates
    timer_thread = threading.Thread(target=timer)
    timer_thread.daemon = True  # Preventing thread from blocking exit
    timer_thread.start()
    # Capture Clingo's output
    stdout, stderr = proc.communicate()
    # End thread
    timer_thread.join(timeout=1)
    # Check for Clingo error
    if proc.returncode != 0:
        error_message = stderr.strip()
        # If error is not a warning, print it and return error code
        if error_message and "Warn" not in error_message:
            print(f"❌ Clingo returned an error:\n{error_message}")
            return -3
    return stdout.strip()


def get_clingo_answer(clingo_output, answer_number):
    """Extracts specific answer from Clingo output.

    Args:
        clingo_output (str): Full output from Clingo.
        answer_number (int): Desired answer number.

    Returns:
        str: Chosen Clingo answer, or an error code.
    """
    # Split the Clingo output into individual lines
    lines = clingo_output.split('\n')
    # Iterate over each line to find desired Answer
    for i, line in enumerate(lines):
        # Check for Answer
        if line.strip() == f'Answer: {answer_number}':
            if i + 1 < len(lines):
                # Save Answer
                answer = lines[i+1].strip()
                break
    try:
        return answer
    except UnboundLocalError:
        if answer_number == 1:
            print(f"❌ Clingo returns UNSATISFIABLE")
            return -4
        print(f"❌ Clingo did not provide the requested Answer: {answer_number}.")
        return -5


def get_action_params(clingo_answer):
    """Extracts parameters for each action predicate from Clingo answer.

    Args:
        clingo_answer (str): Selected Clingo answer.

    Returns:
        list[str]: List of parameter strings for each action predicate.
    """
    # Split the answer and filter for "action"
    actions = [s for s in clingo_answer.split() if "action" in s]
    action_params = []
    is_format = True
    # Trim each action string
    for action in actions:
        # Remove redundant Characters
        if "train" in action:
            # This is the common case: action(train(ID), ...)
            params = action.replace("action(train(", "")
        else:
            # This case tolerates: action(ID, ...)
            is_format = False
            params = action.replace("action(", "")
        params = params[:-1]
        params = params.replace("),", ",")
        # Save trimmed Version
        action_params.append(params)
    if not is_format:
        print("⚠️ Use the common fact format: action(train(ID), Action, Timestep).")
    return action_params


def create_df(action_params):
    """Creates a DataFrame from action predicate parameters.

    Args:
        action_params (list[str]): List of action parameter strings.

    Returns:
        pd.DataFrame: DataFrame containing columns trainID, action, and timestep.
    """
    data = []
    # Process each parameter string
    for i in range(len(action_params)):
        row = action_params[i].split(',')
        # Ensure action/3.
        if len(row) != 3:
            print(f"❌ Clingo returned invalid actions.")
            return -6
        # Ensure correct data type
        row[0], row[2] = int(row[0]), int(row[2])
        data.append(row)
    # Create DF with data
    df_actions = pd.DataFrame(data, columns=["trainID", "action", "timestep"])
    # Sort DF by ID and Timestep
    df_actions = df_actions.sort_values(by=["trainID", "timestep"], ascending=[True, True])
    return df_actions


def clingo_to_df(clingo_path="clingo", lp_files=[], answer_number=1):
    """Runs Clingo and converts its output to a DataFrame of action predicates.

    Args:
        clingo_path (str): Path to Clingo installation.
        lp_files (list[str]): List of ASP files.
        answer_number (int): Desired answer number (default is 1).

    Returns:
        pd.DataFrame: DataFrame containing reduced output of specified Clingo answer or an error code.
    """
    print("\nRun Simulation: START")
    # Check if there are lp files for solving the env
    if len(lp_files) < 2:
        print("❌ Error: No .lp files given.")
        return -1  # no lp files
    if answer_number < 1:
        print(f"❌ Invalid answer to display: {answer_number}.")
        return -5
    print("Running Clingo...")
    # Check if clingo_path is valid
    if clingo_path != "clingo" and not os.path.isfile(f"{clingo_path}.exe"):
        return -2  # invalid clingo path
    # Run Clingo and capture its output
    output = run_clingo(clingo_path, lp_files, answer_number)
    if output == -3:
        return -3  # clingo error
    # Extract desired answer
    answer = get_clingo_answer(output, answer_number)
    if answer == -4 or answer == -5:
        return answer  # invalid answer number
    # Extract action parameters
    params = get_action_params(answer)
    # Create the DataFrame
    df_actions = create_df(params)
    if isinstance(df_actions, int):
        return -6  # invalid actions
    print("✅ Clingo done.")
    print(f"\n===\nOutput:\n{output}\n===\n")
    return df_actions
