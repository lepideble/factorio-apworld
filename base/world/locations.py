from __future__ import annotations
from random import Random
from typing import TYPE_CHECKING

from BaseClasses import Location, Region

from ..config import craftsanity_filter, game_name
from ..data import craftable_items, fluids, technologies, science_packs

if TYPE_CHECKING:
    from .options import FactorioOptions


_science_location_pools: dict[str, list[str]] = {}

for i, pack in enumerate(science_packs, start=1):
    max_needed: int = 999
    prefix: str = f"AP-{i}-"
    _science_location_pools[pack] = [prefix + str(x).upper().zfill(3) for x in range(1, max_needed + 1)]

craftsanity_item_pool = [item_name for item_name in craftable_items if item_name not in science_packs and craftsanity_filter(item_name)]


location_ids = {}

next_id = 1
for pool in _science_location_pools.values():
    location_ids.update({name: id for id, name in enumerate(pool, start=next_id)})
    next_id += len(pool)
for item_name in craftsanity_item_pool:
    location_ids[f'Craft {item_name}'] = next_id
    next_id += 1
del next_id


class FactorioLocation(Location):
    game = game_name

    def __init__(self, player: int, name: str, parent: Region | None = None):
        super().__init__(player, name, location_ids[name], parent)


class FactorioScienceLocation(FactorioLocation):
    complexity: int
    cost: int
    ingredients: dict[str, int]
    count: int = 0

    def __init__(self, player: int, name: str, parent: Region | None = None):
        super().__init__(player, name, parent)

        # "AP-{Complexity}-{Cost}"
        self.complexity = int(self.name.split('-')[1]) - 1
        self.cost = int(self.name.split('-')[2])

    @property
    def data(self):
        return {
            'id': f'ap-{self.address}-',
            'name': self.name,
            'unit': {
                'count': self.count,
                'ingredients': [(name, count) for name, count in self.ingredients.items()],
            },
            'research_trigger': None,
        }


class FactorioCraftLocation(FactorioLocation):
    item_name: str

    def __init__(self, player: int, item_name: str, parent: Region | None = None):
        super(FactorioCraftLocation, self).__init__(player, f'Craft {item_name}', parent)

        self.item_name = item_name

    @property
    def data(self):
        return {
            'id': f'ap-{self.address}-',
            'name': self.name,
            'unit': None,
            'research_trigger': {
                'type': 'craft-fluid' if self.item_name in fluids else 'craft-item',
                'fluid' if self.item_name in fluids else 'item': self.item_name,
            },
        }


def get_locations(options: FactorioOptions, random: Random) -> list[FactorioLocation]:
    locations_to_create = len(technologies)

    # Crate craftsanity locations
    craftsanity_location_count = min(options.craftsanity.value, locations_to_create)
    craftsanity_items = random.sample(craftsanity_item_pool, craftsanity_location_count)
    craftsanity_locations = [FactorioCraftLocation(0, item_name) for item_name in craftsanity_items]

    locations_to_create -= len(craftsanity_locations)


    # Create science locations
    science_location_pool = []

    for pack in options.max_science_pack.get_allowed_packs():
        science_location_pool.extend(_science_location_pools[pack])

    science_locations = []
    for science_location_name in random.sample(science_location_pool, locations_to_create):
        science_locations.append(FactorioScienceLocation(0, science_location_name))

    # Attribute ingredients to science locations
    for science_location in science_locations:
        science_location.ingredients = {science_packs[science_location.complexity]: 1}
        for complexity in range(science_location.complexity):
            if (options.tech_cost_mix > random.randint(0, 99)):
                science_location.ingredients[science_packs[complexity]] = 1

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

    science_locations.sort(key=lambda location: (location.complexity, location.cost))

    return craftsanity_locations + science_locations
