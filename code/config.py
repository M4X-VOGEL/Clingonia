"""
Configuration Constants for Flatland Simulation.

- DIR_MAP (dict): Maps cardinal directions to numeric values.
- TRACKS (set): Set of Flatland track IDs grouped by type.
- DEAD_ENDS (set): Set of Flatland dead-end IDs.
- AGENT_COLORS (list): List of hex color codes for Flatland agents.
- CLINGO_OPTIONS (set): Set of valid Clingo options.
- INCOMPATIBLE_CLINGO_OPTIONS (set): Set of Clingo options that cause Clingonia to malfunction.
"""

DIR_MAP = {'n': 0, 'e': 1, 's': 2, 'w': 3}

TRACKS = {
  0,  # Type 0
  32800, 1025, 4608, 16386, 72, 2064,  # Type 1
  37408, 17411, 32872, 3089, 49186, 1097, 34864, 5633,  # Type 2
  33825,  # Type 3
  38433, 50211, 33897, 35889,  # Type 4
  38505, 52275,  # Type 5
  20994, 16458, 2136, 6672  # Type 6
}

DEAD_ENDS = {8192, 4, 128, 256}

AGENT_COLORS = [
    "#d50000", "#c51162", "#aa00ff", "#6200ea", "#304ffe", "#2962ff",
    "#0091ea", "#00b8d4", "#00bfa5", "#00c853", "#64dd17", "#aeea00",
    "#ffd600", "#ffab00", "#ff6d00", "#ff3d00", "#5d4037", "#455a64"
]


CLINGO_OPTIONS = {
    '--configuration', '--tester', '--stats', '-s', '--parse-ext', '--no-parse-ext',
    '--parse-maxsat', '--no-parse-maxsat', '--share', '--learn-explicit', '--sat-prepro',
    '--trans-ext', '--eq', '--backprop', '--no-backprop', '--supp-models', '--no-ufs-check',
    '--no-gamma', '--eq-dfs', '--solve-limit', '--parallel-mode', '-t', '--global-restarts',
    '--distribute', '--integrate', '--enum-mode', '-e', '--project', '--models', '-n',
    '--opt-mode', '--opt-strategy', '--opt-usc-shrink', '--opt-heuristic', '--restart-on-model',
    '--no-restart-on-model', '--lookahead', '--heuristic', '--init-moms', '--no-init-moms',
    '--score-res', '--score-other', '--sign-def', '--sign-fix', '--no-sign-fix', '--berk-huang',
    '--no-berk-huang', '--vsids-acids', '--no-vsids-acids', '--vsids-progress', '--nant',
    '--no-nant', '--dom-mod', '--save-progress', '--init-watches', '--update-mode',
    '--acyc-prop', '--seed', '--partial-check', '--sign-def-disj', '--rand-freq', '--rand-prob',
    '--no-lookback', '--forget-on-step', '--strengthen', '--otfs', '--update-lbd',
    '--update-act', '--reverse-arcs', '--contraction', '--loops', '--restarts', '-r',
    '--reset-restarts', '--local-restarts', '--no-local-restarts', '--counter-restarts',
    '--block-restarts', '--shuffle', '--deletion', '-d', '--del-grow', '--del-cfl', '--del-init',
    '--del-estimate', '--del-max', '--del-glue', '--del-on-restart', '--text', '--const', '-c',
    '--output', '-o', '--output-debug', '--warn', '-W', '--rewrite-minimize', '--keep-facts',
    '--reify-sccs', '--reify-steps', '--help', '-h', '--version', '-v', '--verbose', '-V',
    '--time-limit', '--fast-exit', '--print-portfolio', '--quiet', '-q', '--pre', '--outf',
    '--out-atomf', '--out-ifs', '--out-hide-aux', '--lemma-in', '--lemma-out', '--lemma-out-lbd',
    '--lemma-out-max', '--lemma-out-dom', '--lemma-out-txt', '--hcc-out', '--compute', '--mode'
}


INCOMPATIBLE_CLINGO_OPTIONS = {
    '--help'
}
