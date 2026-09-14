# SWEN90004 Assignment 2 - Virus Model

**Authors:** Luka Apps, Ka Chun Lee, Will Kang

Grade
- Code: 6/6
- Report: 12.5/19

## Requirements

- **Python 3.14** (also tested on Python 3.11+)
- **No third-party libraries required** for the simulation.
- Uses only the Python standard library (`random`, `dataclasses`, `enum`, `configparser`, `csv`, `collections`, `math`, `pathlib`, `os`, `sys`).


## Run a single simulation

From the project root:

    python main.py props/default.ini

This runs the simulation with default parameters and writes a CSV to `data/default-seed-42.csv`.

To override the random seed:

    python main.py props/default.ini 7

This runs the same parameters with seed 7, producing `data/default-seed-7.csv`.

## Run all experiments

To regenerate all the experimental data:

    python scripts/run_experiments.py

This runs every `.ini` file in `props/` across 30 random seeds, writing one CSV per (experiment, seed) combination to `data/`. Expected runtime: 30-60 minutes on a typical machine.

## Project structure

    ├── main.py            CLI entry point
    ├── params.py          Parameter loader from .ini files
    ├── world.py           Simulation orchestrator and grid
    ├── person.py          Agent class
    ├── state.py           Health-state enum (SUSCEPTIBLE/INFECTED/IMMUNE)
    ├── stats.py           CSV writer
    ├── props/             Experiment configurations
    │   ├── default.ini    Documented template
    │   ├── exp*.ini       Replication experiments (R1-R5)
    │   └── ext*.ini       Extension experiments (vaccination sweep)
    ├── scripts/
    │   └── run_experiments.py
    └── data/              Pre-generated CSV outputs from our experiments

## Configuration

Each `.ini` file describes one experiment. See `props/default.ini` for the documented template. To create a new experiment, copy `default.ini` and modify parameters.

## Output format

Each simulation writes one row per tick to a CSV with columns:

- `tick`: simulated week (0 = initial state)
- `total`: alive population
- `susceptible`, `infected`, `immune`: state counts
- `pct_infected`, `pct_immune`: percentages

## Reproducibility

All randomness flows through a single seeded `random.Random` instance. Two simulations with identical parameters and seeds produce identical CSV output.
