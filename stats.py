"""
Per-tick metric recorder.

Records one CSV row per simulated tick:
    tick, total, susceptible, infected, immune, pct_infected, pct_immune
"""

import csv

from state import State

class Stats:
    """Streams per-tick simulation metrics to a CSV file"""

    HEADER = ["tick", "total", "susceptible", "infected", "immune", "pct_infected", "pct_immune"]

    def __init__(self, output_path):
        """Open the CSV at `output_path` and write the header"""

        self._file = open(output_path, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(self.HEADER)

    def record_tick(self, world):
        """Compute metrics from the current World state and append"""

        total = world.population_size()
        s = world.count_by_state(State.SUSCEPTIBLE)
        i = world.count_by_state(State.INFECTED)
        r = world.count_by_state(State.IMMUNE)

        pct_i = (100.0 * i / total) if total > 0 else 0.0
        pct_r = (100.0 * r / total) if total > 0 else 0.0

        self._writer.writerow([
            world.current_tick, total, s, i, r,
            f"{pct_i:.4f}", f"{pct_r:.4f}",
        ])

    def close(self):
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False