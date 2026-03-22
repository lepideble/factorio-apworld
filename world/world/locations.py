from BaseClasses import Location, Region

from ..config import game_name
from ..data import science_packs


science_location_pools: dict[str, list[str]] = {}

for i, pack in enumerate(science_packs, start=1):
    max_needed: int = 999
    prefix: str = f"AP-{i}-"
    science_location_pools[pack] = [prefix + str(x).upper().zfill(3) for x in range(1, max_needed + 1)]

location_ids = {}

next_id = 1
for pool in science_location_pools.values():
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

    def __init__(self, player: int, name: str, address: int, parent: Region):
        super(FactorioScienceLocation, self).__init__(player, name, address, parent)

        # "AP-{Complexity}-{Cost}"
        self.complexity = int(self.name.split('-')[1]) - 1
        self.cost = int(self.name.split('-')[2])

        self.ingredients = {science_packs[self.complexity]: 1}
        for complexity in range(self.complexity):
            if (parent.multiworld.worlds[self.player].options.tech_cost_mix >
                    parent.multiworld.worlds[self.player].random.randint(0, 99)):
                self.ingredients[science_packs[complexity]] = 1
