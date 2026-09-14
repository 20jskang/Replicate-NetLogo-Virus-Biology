"""
Health states a Person can occupy.

The three states form a directed graph of transitions:
    SUSCEPTIBLE -> INFECTED    (via contact, probability `infectiousness`)
    INFECTED    -> IMMUNE      (after `duration` weeks, probability `chance_recover`)
    INFECTED    -> (death)     (after `duration` weeks, probability 1 - `chance_recover`)
    IMMUNE      -> SUSCEPTIBLE (after `immunity_duration` weeks, per NetLogo spec)
    (birth)     -> SUSCEPTIBLE (newborns are always susceptible)

Death from old age can occur in any state.
"""

from enum import Enum

class State(Enum):
    """Health state of a Person. Used for behaviour dispatch and for stats"""

    SUSCEPTIBLE = "S"
    INFECTED = "I"
    IMMUNE = "R"