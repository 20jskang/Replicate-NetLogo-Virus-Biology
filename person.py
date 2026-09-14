"""
One individual in the simulated population.

Per-tick lifecycle (mirrors NetLogo's `go`):
    1. get_older      (age + decrement immunity + advance sick-time)
    2. move           (heading-based continuous motion)
    3. recover_or_die (only if sick, may die)
    4. either infect  (if still sick) or reproduce (if healthy)

Death is signalled by methods returning True; the World removes dead Persons after iteration. All
randomness flows through World.rng.

Position model:
    Continuous floating point (x, y) and heading in degrees (NetLogo convention: 0 = north, 90 = 
    east). Patch identity is the integer floor of the coordinates.
"""

import math

from state import State

class Person:
    """A single agent: continuous position, heading, state"""

    def __init__(self, x, y, heading, state, age_weeks, world):
        """
        Construct a Person at (x, y) with the given heading and state

        Initial age can be non-zero so the starting population is spread across lifespans, avoiding
        synchronised early die-offs. Newborns use age=1 to match NetLogo's `hatch [set age 1]`
        """

        self.x = x
        self.y = y
        self.heading = heading
        self.state = state
        self.age_weeks = age_weeks
        self.sick_weeks = 0        # only meaningful when state == INFECTED
        self.immune_weeks = 0      # only meaningful when state == IMMUNE
        self.world = world

    def patch(self):
        """Return this Person's current patch (integer cell coordinates)"""

        return (int(self.x), int(self.y))

    # behaviour methods (one per stage of a tick) --------------------------------------------------

    def get_older(self):
        """
        Age by one week, advance immunity/sick counters, check old age death

        Mirrors NetLogo's `get-older`. Returns True on old-age death
        """

        self.age_weeks += 1

        if self.age_weeks > self.world.params.lifespan_weeks:
            return True
        
        if self.state is State.IMMUNE:
            self.immune_weeks += 1

            if self.immune_weeks >= self.world.params.immunity_duration:
                # immunity has run out, return to susceptible
                self.state = State.SUSCEPTIBLE
                self.immune_weeks = 0

        elif self.state is State.INFECTED:
            self.sick_weeks += 1

        return False

    def move(self):
        """
        Heading-based continuous movement with toroidal wrap

        Mirrors NetLogo's `rt random 100 / lt random 100 / fd 1`: net rotation is the difference of
        two uniform [0, 100) draws, then forward 1 unit. Re-registers on a new patch if the
        integer-floor patch has changed
        """

        rng = self.world.rng

        # right random 100, then left random 100 -> net rotation is uniform in (-100, 100)
        self.heading = (self.heading + rng.uniform(0, 100) - rng.uniform(0, 100)) % 360
        old_patch = self.patch()

        rad = math.radians(self.heading)

        # 0 deg = north, 90 = east. cos(heading) for dy, sin(heading) for dx
        new_x = self.x + math.sin(rad)
        new_y = self.y + math.cos(rad)

        # toroidal wrap on continuous coordinates
        new_x %= self.world.params.grid_width
        new_y %= self.world.params.grid_height

        self.x = new_x
        self.y = new_y

        new_patch = self.patch()
        if new_patch != old_patch:
            self.world.update_patch(self, old_patch, new_patch)

    def recover_or_die(self):
        """
        Resolve infection if duration has elapsed. Returns True on death.

        Mirrors NetLogo's `recover-or-die`. Note the strict `>`: the check fires the tick AFTER
        sick-time reaches duration
        """

        if self.state is not State.INFECTED:
            return False
        
        if self.sick_weeks <= self.world.params.duration:
            return False
        
        # sick-time has exceeded duration, recover or die
        if self.world.rng.random() < self.world.params.chance_recover:
            self.state = State.IMMUNE
            self.sick_weeks = 0
            self.immune_weeks = 0
            return False
        
        return True

    def try_infect_neighbours(self):
        """
        If infected, roll `infectiousness` against each susceptible on the same patch.

        Mirrors NetLogo's `infect`. Immune turtles are unaffected
        """

        if self.state is not State.INFECTED:
            return
        
        rng = self.world.rng
        infectiousness = self.world.params.infectiousness

        for other in self.world.people_on_patch(*self.patch()):
            if other is self:
                continue # don't try to infect yourself

            if other.state is State.SUSCEPTIBLE and rng.random() < infectiousness:
                other.become_infected()

    def try_reproduce(self):
        """
        Reproduce with probability `birth_rate` if healthy and below capacity.

        Mirrors NetLogo's `reproduce`: newborn inherits parent's location, rotates 45 deg left,
        steps 1 forward. Newborn is SUSCEPTIBLE, age=1. Returns the newborn or None
        """

        if self.state is State.INFECTED:
            return None
        
        if self.world.population_size() >= self.world.params.carrying_capacity:
            return None
        
        if self.world.rng.random() >= self.world.params.birth_rate:
            return None

        # newborn inherits the parent's location/heading, then performs lt 45 fd 1
        new_heading = (self.heading - 45) % 360
        rad = math.radians(new_heading)

        new_x = (self.x + math.sin(rad)) % self.world.params.grid_width
        new_y = (self.y + math.cos(rad)) % self.world.params.grid_height

        return Person(new_x, new_y, new_heading, State.SUSCEPTIBLE, 1, self.world)

    # helpers --------------------------------------------------------------------------------------

    def become_infected(self):
        """Transition to INFECTED, resetting the sickness counter"""

        self.state = State.INFECTED
        self.sick_weeks = 0