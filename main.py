"""
CLI entry point for the Virus simulation.

Usage:
    python main.py <props_file> [seed]

Loads parameters, runs the simulation for `max_ticks` ticks, and writes per-tick metrics to a CSV.
"""

import os
import sys

from params import load, with_seed
from stats import Stats
from world import World

OUTPUT_DIR = "data"

def main(argv):
    """Validate args, load params, run the simulation, write CSV. Returns exit code"""

    if len(argv) < 2:
        print("Usage: python main.py <props_file> [seed] [output_path]", file=sys.stderr)
        return 1

    props_file = argv[1]
    params = load(props_file)

    # optional seed override
    if len(argv) >= 3:
        params = with_seed(params, int(argv[2]))

    # ensure output dir exists, then build output path
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = _default_output_name(props_file, params)

    # build the world and run the simulation, recording stats each tick
    world = World(params)
    with Stats(output_path) as stats:
        # tick 0 baseline (initial state, before any updates)
        stats.record_tick(world)

        for _ in range(params.max_ticks):
            world.tick()
            stats.record_tick(world)

    print(f"wrote {output_path}")
    return 0


def _default_output_name(props_file, params):
    """
    Derive an output CSV name from props file and seed
    """

    base = os.path.splitext(os.path.basename(props_file))[0]
    return os.path.join(OUTPUT_DIR, f"{base}-seed-{params.random_seed}.csv")

if __name__ == "__main__":
    sys.exit(main(sys.argv))