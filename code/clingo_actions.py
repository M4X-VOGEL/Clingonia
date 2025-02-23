import os
import time
import threading
import subprocess
import pandas as pd


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

def run_clingo(clingo_path, lp_files, answer_number):
    """Gets clingo output by running input files.
    
    Args:
        clingo_path (str): Path to your clingo installation (default is "clingo").
        lp_files (list): Files with your ASP code.
        answer_number (int): Number of the wanted answer.

    Returns:
        [str]: Clingo output with its answers.
    """
    timer_start = time.perf_counter()
    proc = subprocess.Popen(
        [clingo_path] + lp_files + [str(answer_number)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    # Timer-Thread for status updates while Clingo runs.
    def timer():
        counter, frustration = 30, 30
        while proc.poll() is None:
            time.sleep(0.1)
            elapsed = int(time.perf_counter() - timer_start)
            if elapsed == counter:
                # Clingo updates
                print(f"Clingo: \'{clingo_frustration[frustration]}\'")
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
    # Initialize Timer Thread
    timer_thread = threading.Thread(target=timer)
    timer_thread.daemon = True  # Preventing thread from blocking exit
    timer_thread.start()
    # Capture Clingo's output
    stdout, stderr = proc.communicate()
    # End of Thread
    timer_thread.join(timeout=1)
    # Error Handling
    if proc.returncode != 0:
        error_message = stderr.strip()
        if error_message and "Warn" not in error_message:
            print(f"Clingo returned an error:\n{error_message}")
            return -3
    return stdout.strip()



def get_clingo_answer(clingo_output, answer_number):
    """Gets specific clingo answer.

    Args:
        clingo_output (str): Clingo output with its answers.
        answer_number (int): Number of the wanted answer.

    Returns:
        [str]: Chosen clingo answer.
    """
    # Split Output String by Lines
    lines = clingo_output.split('\n')
    # Search for defined Answer
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
    """Gets list of all parameters for each action predicate.

    Args:
        clingo_answer (str): Chosen clingo answer

    Returns:
        [list]: Parameters of all action predicates.
    """
    # Only consider Action Predicates
    actions = [s for s in clingo_answer.split() if "action" in s]
    # Trim Action Predicates
    action_params = []
    for action in actions:
        # Remove redundant Characters
        params = action.replace("action(train(", "")
        params = params[:-1]
        params = params.replace("),", ",")
        # Save trimmed Version
        action_params.append(params)
    return action_params


def create_df(action_params):
    """Creates DataFrame with parameters of all action predicates.
    
    Args:
        action_params (list): Chosen clingo answer.
    
    Returns:
        [pd.DataFrame]: parameters of action predicates (trainID, action, timestep).
    """
    data = []
    for i in range(len(action_params)):
        row = action_params[i].split(',')
        # Ensure correct data type
        row[0], row[2] = int(row[0]), int(row[2])
        data.append(row)
    df_actions = pd.DataFrame(data, columns=["trainID", "action", "timestep"])
    # Sort by ID and Timestep
    df_actions = df_actions.sort_values(by=["trainID", "timestep"], ascending=[True, True])
    return df_actions


def clingo_to_df(clingo_path="clingo", lp_files=[], answer_number=1):
    """Runs clingo program and creates a DataFrame with the reduced output of the stated answer.
    
    Args:
        clingo_path (str): Path to your clingo installation.
        lp_files (list): Files with your ASP code.
        answer_number (int): Number of the wanted answer from the clingo output (default is 1).
    
    Returns:
        [pd.DataFrame]: Reduced output of the stated answer.
    """
    print("\nRun Simulation: START")
    if len(lp_files) < 2:
        print("❌ Error: No .lp files given.")
        return -1  # no lp files
    print("Running Clingo...")
    if clingo_path != "clingo" and not os.path.isfile(f"{clingo_path}.exe"):
        return -2  # invalid clingo path
    output = run_clingo(clingo_path, lp_files, answer_number)
    if output == -3:
        return -3  # clingo error
    answer = get_clingo_answer(output, answer_number)
    if answer == -4 or answer == -5:
        return answer  # invalid answer number
    params = get_action_params(answer)
    df_actions = create_df(params)
    print("✅ Clingo done.")
    return df_actions
