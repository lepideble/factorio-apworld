from BaseClasses import Location, Region

from ...config import game_name
from ...data.raw import items
from .ids import location_ids

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
                'type': 'craft-item' if self.item_name in items else 'craft-fluid',
                'item' if self.item_name in items else 'fluid': self.item_name,
            },
        }
