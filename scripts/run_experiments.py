# scripts/run_experiments.py

"""Batch experiment runner, runs every props/exp*.ini and props/ext*.ini across 30 seeds."""

import subprocess
import glob
import os

os.makedirs("data", exist_ok=True)

# discover all replication and extension experiment configs
ini_files = glob.glob("props/exp*.ini") + glob.glob("props/ext*.ini")
if not ini_files:
    print("No props/exp*.ini files found.")
    print("Create some by copying props/default.ini, e.g. props/exp01-baseline.ini")
    exit(1)

# run each experiment with seeds 1-30
# subprocess (not import) for clean RNG state per run
for ini in ini_files:
    for seed in range(1, 31):
        print(f"Running {ini} with seed {seed}")
        subprocess.run(["python", "main.py", ini, str(seed)], check=True)

print("done")