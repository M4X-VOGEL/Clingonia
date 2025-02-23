"""
Configuration Constants for Flatland Simulation.

- DIR_MAP (dict): Maps cardinal directions to numeric values.
- TRACKS (set): Set of Flatland track IDs grouped by type.
- DEAD_ENDS (set): Set of Flatland dead-end IDs.
- AGENT_COLORS (list): List of hex color codes for Flatland agents.
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
