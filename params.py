"""
Experiment configuration loader.

Reads a .ini file and produces a frozen Params dataclass used by the simulation. Validation happens
at load time.

Expected format:
    [simulation] slider parameters from NetLogo
    [constants]  NetLogo hardcoded values, exposed for experimentation
    [grid]       grid dimensions
    [control]    tick budget, random seed
    [extension]  extension toggle and parameters
"""

import configparser
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Params:
    """Immutable container for all simulation parameters"""

    # slider parameters (from NetLogo)
    number_people: int    # initial population
    infectiousness: float # transmission probability per contact, 0..1
    chance_recover: float # probability of recovery vs death, 0..1
    duration: int         # weeks sick before recover/die check

    # NetLogo hardcoded constants
    initial_infected: int
    carrying_capacity: int
    lifespan_weeks: int
    immunity_duration: int
    birth_rate: float

    # grid
    grid_width: int
    grid_height: int

    # simulation control
    max_ticks: int
    random_seed: int

    # extension: vaccination at initialisation
    # when enabled, each non-initially-infected agent is independently
    # set to IMMUNE with probability `vaccination_rate` at setup
    extension_enabled: bool
    vaccination_rate: float


def load(filename: str) -> Params:
    """Load parameters from a .ini file and return a validated Params"""

    parser = configparser.ConfigParser()
    read_files = parser.read(filename)
    if not read_files:
        raise FileNotFoundError(f"could not read {filename}")

    sim = parser["simulation"]
    const = parser["constants"]
    grid = parser["grid"]
    ctrl = parser["control"]
    ext = parser["extension"]

    p = Params(
        number_people=sim.getint("number_people"),
        infectiousness=sim.getfloat("infectiousness"),
        chance_recover=sim.getfloat("chance_recover"),
        duration=sim.getint("duration"),
        initial_infected=const.getint("initial_infected"),
        carrying_capacity=const.getint("carrying_capacity"),
        lifespan_weeks=const.getint("lifespan_weeks"),
        immunity_duration=const.getint("immunity_duration"),
        birth_rate=const.getfloat("birth_rate"),
        grid_width=grid.getint("width"),
        grid_height=grid.getint("height"),
        max_ticks=ctrl.getint("max_ticks"),
        random_seed=ctrl.getint("random_seed"),
        extension_enabled=ext.getboolean("enabled"),
        vaccination_rate=ext.getfloat("vaccination_rate"),
    )
    _validate(p)
    return p


def with_seed(params: Params, seed: int) -> Params:
    """Return a new Params with the given random seed"""

    return replace(params, random_seed=seed)


def _validate(p: Params) -> None:
    """Raise ValueError on any out of range parameter"""
    
    if not 0.0 <= p.infectiousness <= 1.0:
        raise ValueError(f"infectiousness {p.infectiousness} not in [0,1]")
    if not 0.0 <= p.chance_recover <= 1.0:
        raise ValueError(f"chance_recover {p.chance_recover} not in [0,1]")
    if not 0.0 <= p.birth_rate <= 1.0:
        raise ValueError(f"birth_rate {p.birth_rate} not in [0,1]")
    if not 0.0 <= p.vaccination_rate <= 1.0:
        raise ValueError(f"vaccination_rate {p.vaccination_rate} not in [0,1]")
    if p.number_people < 0:
        raise ValueError(f"number_people {p.number_people} < 0")
    if p.initial_infected > p.number_people:
        raise ValueError("initial_infected exceeds number_people")
    if p.duration <= 0:
        raise ValueError(f"duration {p.duration} must be positive")
    if p.grid_width <= 0 or p.grid_height <= 0:
        raise ValueError("grid dimensions must be positive")
    if p.max_ticks <= 0:
        raise ValueError(f"max_ticks {p.max_ticks} must be positive")