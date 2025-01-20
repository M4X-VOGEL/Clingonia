import subprocess
import sys
import csv

### TEST-EINGABE
clingo_path = "clingo"
lp_files = ["asp/flat.lp", "asp/trans.lp", "env/env.lp"]
answer_number = 1
###

def clingo_to_csv(clingo_path="clingo", lp_files=[], answer_number=1):
  """Runs clingo program and writes the reduced output of the stated answer into a CSV.

  Args:
    clingo_path (str): Path to your clingo installation.
    lp_files (list): Files with your ASP code.
    answer_number (int): Number of the wanted answer from the clingo output (default is 1).
  """
  # Check, if no .lp files were given
  if lp_files == []: print("Error: No .lp files given."); sys.exit()
  output = run_clingo(clingo_path, lp_files, answer_number)
  answer = get_clingo_answer(output, answer_number)
  params = get_action_params(answer)
  write_action_params_in_CSV(params, "action_params.csv")


def run_clingo(clingo_path, lp_files, answer_number):
  """Gets clingo output by running input files.

  Args:
    clingo_path (str): Path to your clingo installation (default is "clingo").
    lp_files (list): Files with your ASP code.
    answer_number (int): Number of the wanted answer.

  Returns:
    [str]: Clingo output with its answers.
  """
  # Run Clingo
  result = subprocess.run([clingo_path] + lp_files + [str(answer_number)], capture_output=True, text=True)
  # Error Handling
  if result.returncode != 0:
    error_message = result.stderr.strip()
    # Ignore empty Errors and all Warnings
    if error_message != "" and not "Warn" in error_message:
      print("Error: Invalid clingo path and/or files:")
      print("--> given clingo path: '" + clingo_path + "'")
      print("--> given .lp files:", lp_files)
      sys.exit()
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
    print(f"Error: Clingo did not provide the requested Answer: {answer_number}.")
    sys.exit()


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
  train_ids = []
  action_params = []
  for action in actions:
    # Remove redundant Characters
    params = action.replace("action(train(", "")
    params = params[:-1]
    params = params.replace("),", ",")
    # Skip move to starting position
    if params[0] not in train_ids:
      train_ids.append(params[0])
      continue
    # Save trimmed Version
    action_params.append(params)
  return action_params


def write_action_params_in_CSV(action_params, file_name):
  """Writes header and parameters for all action predicates into a CSV.

  Args:
    action_params (list): Chosen clingo answer.
    file_name: (str): CSV file name.
  """
  # Open CSV File
  with open(f"data/{file_name}", "w", newline="", encoding="utf-8") as csvfile:
    # Use CSV Writer, writing no Quotation Marks
    writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
    # Write Header
    writer.writerow(["trainID", "action", "timestep"])
    # Write 3 Parameters of each Action Predicate in a Line
    for params in action_params:
      writer.writerow(params.split(','))


# Main Call
clingo_to_csv(clingo_path, lp_files, answer_number)
