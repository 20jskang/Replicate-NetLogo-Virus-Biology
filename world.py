"""
The simulated world.

Owns the toroidal grid, the population, and the seeded RNG. Drives the per-tick simulation loop in
the order specified by NetLogo's `go`:

    for each person (in shuffled order):
        get_older          (may die of old age)
        move

        if sick:
            recover_or_die (may die of infection)

        if still sick:
            try to infect neighbours

        else (healthy):
            try to reproduce

    apply queued births and deaths

Patches are stored as a dict keyed by integer (x, y) for O(1) same-patch lookups. Person coordinates
are continuous; patch identity is the integer floor of those coordinates.
"""

import random
from collections import defaultdict

from state import State
from person import Person

class World:
    """The simulation orchestrator: grid, population, RNG, tick loop"""

    def __init__(self, params):
        """
        Construct the world from a Params instance and seed the population

        All randomness flows through a single Random seeded from params.random_seed for
        reproducibility
        """

        self.params = params
        self.rng = random.Random(params.random_seed)
        self._population = []
        self._patches = defaultdict(list) # (int_x, int_y) -> list of Person
        self.current_tick = 0

        self._seed_population()

    def tick(self):
        """
        Advance the simulation by one week

        Population is shuffled to mimic NetLogo's `ask turtles` (random agent order). Each agent's
        per-tick lifecycle (get_older -> move -> recover_or_die -> infect-or-reproduce) matches the
        NetLogo `go` procedure

        Births and deaths are queued during iteration and applied at the end to avoid mutating the
        list while iterating
        """
        
        self.current_tick += 1

        ordered = list(self._population)

        # iterate agents in random order each tick
        self.rng.shuffle(ordered)

        deaths = []
        newborns = []

        for p in ordered:
            if p.get_older():
                deaths.append(p)
                continue # dead, skip remaining behaviours this tick

            p.move()
            
            if p.state is State.INFECTED and p.recover_or_die():
                deaths.append(p)
                continue # dead, skip infect step
            
            if p.state is State.INFECTED:
                p.try_infect_neighbours()
            
            else:
                # only healthy agents reproduce; sick agents focus on infecting
                baby = p.try_reproduce()
                if baby is not None:
                    newborns.append(baby)

        for d in deaths:
            self._remove(d)
        
        for n in newborns:
            self._add(n)

    def people_on_patch(self, x, y):
        """Return the list of Persons currently on patch (x, y)"""

        return self._patches[(x, y)]

    def update_patch(self, person, old_patch, new_patch):
        """
        Re-register a Person on the patch grid after they crossed into a new cell. Caller
        (Person.move) is responsible for checking that old_patch != new_patch
        """

        self._patches[old_patch].remove(person)
        self._patches[new_patch].append(person)

    def population_size(self):
        """Current population (alive only)"""

        return len(self._population)

    def count_by_state(self, state):
        """Count of Persons in a given state"""

        return sum(1 for p in self._population if p.state is state)

    def population(self):
        """Returns the current population list"""
        
        return self._population

    # internal helpers -----------------------------------------------------------------------------

    def _seed_population(self):
        """
        Create the initial population

        Mirrors NetLogo's setup-turtles: `initial_infected` start INFECTED, the rest SUSCEPTIBLE.
        Positions and headings are uniformly random; ages are uniformly distributed across the
        lifespan

        Extension: when `extension_enabled` is true, each non-initially-infected person is
        independently set to IMMUNE with probability `vaccination_rate`, representing vaccinated
        individuals at simulation start
        """
        
        for i in range(self.params.number_people):
            x = self.rng.uniform(0, self.params.grid_width)
            y = self.rng.uniform(0, self.params.grid_height)
            heading = self.rng.uniform(0, 360)

            if i < self.params.initial_infected:
                state = State.INFECTED

            elif self.params.extension_enabled and self.rng.random() < self.params.vaccination_rate:
                state = State.IMMUNE

            else:
                state = State.SUSCEPTIBLE
                
            age = self.rng.randint(0, self.params.lifespan_weeks - 1)
            person = Person(x, y, heading, state, age, self)
            self._add(person)

    def _add(self, person):
        """Register a Person in the population list and patch grid"""

        self._population.append(person)
        self._patches[person.patch()].append(person)

    def _remove(self, person):
        """De-register a dead Person from the population list and patch grid"""

        self._population.remove(person)
        self._patches[person.patch()].remove(person)