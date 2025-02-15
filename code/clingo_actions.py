import os
import time
import subprocess
import pandas as pd

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


def run_clingo(clingo_path, lp_files, answer_number):
    """Gets clingo output by running input files.
    
    Args:
        clingo_path (str): Path to your clingo installation (default is "clingo").
        lp_files (list): Files with your ASP code.
        answer_number (int): Number of the wanted answer.

    Returns:
        [str]: Clingo output with its answers.
    """
    # Run Clingo (with timer)
    timer_start = time.perf_counter()
    result = subprocess.run(
        [clingo_path] + lp_files + [str(answer_number)],
        capture_output=True,
        text=True
    )
    timer_end = time.perf_counter()
    # Timer result
    execution_time = timer_end - timer_start
    print(f"🕓 Clingo ran for {execution_time:.2f}s.")
    # Error Handling
    if result.returncode != 0:
        error_message = result.stderr.strip()
        # Ignore empty Errors and all Warnings
        if error_message and "Warn" not in error_message:
            print(f"Clingo returned an error:\n{error_message}")
            return -3
    # Save Output as String
    output = result.stdout.strip()
    return output


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
