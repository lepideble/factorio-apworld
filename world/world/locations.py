from random import Random

from BaseClasses import Location, Region

from ..config import game_name
from ..data import technologies, science_packs
from .options import FactorioOptions


_science_location_pools: dict[str, list[str]] = {}

for i, pack in enumerate(science_packs, start=1):
    max_needed: int = 999
    prefix: str = f"AP-{i}-"
    _science_location_pools[pack] = [prefix + str(x).upper().zfill(3) for x in range(1, max_needed + 1)]

location_ids = {}

next_id = 1
for pool in _science_location_pools.values():
    location_ids.update({name: id for id, name in enumerate(pool, start=next_id)})
    next_id += len(pool)
del next_id


class FactorioLocation(Location):
    game = game_name


class FactorioScienceLocation(FactorioLocation):
    complexity: int
    cost: int
    ingredients: dict[str, int]
    count: int = 0

    def __init__(self, player: int, name: str, address: int | None = None, parent: Region | None = None):
        super(FactorioScienceLocation, self).__init__(player, name, address, parent)

        # "AP-{Complexity}-{Cost}"
        self.complexity = int(self.name.split('-')[1]) - 1
        self.cost = int(self.name.split('-')[2])


def get_locations(options: FactorioOptions, random: Random) -> list[FactorioLocation]:
    # Create science locations
    science_location_pool = []

    for pack in options.max_science_pack.get_allowed_packs():
        science_location_pool.extend(_science_location_pools[pack])

    science_locations = []
    for science_location_name in random.sample(science_location_pool, len(technologies)):
        science_locations.append(FactorioScienceLocation(0, science_location_name))

    # Attribute ingredients to science locations
    for science_location in science_locations:
        science_location.ingredients = {science_packs[science_location.complexity]: 1}
        for complexity in range(science_location.complexity):
            if (options.tech_cost_mix > random.randint(0, 99)):
                science_location.ingredients[science_packs[science_location.complexity]] = 1

    # Attribute counts to science locations
    cost_distribution = options.tech_cost_distribution
    min_cost = options.min_tech_cost.value
    max_cost = options.max_tech_cost.value

    match cost_distribution:
        case cost_distribution.option_even:
            science_location_costs = (random.randint(min_cost, max_cost) for _ in science_locations)
        case cost_distribution.option_low:
            science_location_costs = (random.triangular(min_cost, max_cost, min_cost) for _ in science_locations)
        case cost_distribution.option_middle:
            science_location_costs = (random.triangular(min_cost, max_cost, (min_cost + max_cost) // 2) for _ in science_locations)
        case cost_distribution.option_high:
            science_location_costs = (random.triangular(min_cost, max_cost, max_cost) for _ in science_locations)

    science_location_costs = sorted(science_location_costs)

    if options.ramping_tech_costs:
        sorter = lambda location: location.complexity, location.cost
    else:
        sorter = lambda location: location.cost

    for i, location in enumerate(sorted(science_locations, key=sorter)):
        location.count = science_location_costs[i]

    return science_locations
