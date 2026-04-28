from rule_builder.rules import HasAny, Rule

from ...config import game_name
from ...data.classes import Surface
from .level import ProductionLevel


class HasItem(Rule['FactorioWorld'], game=game_name):
    item_name: str
    level: ProductionLevel
    surface_name: str

    def __init__(self, item: str, surface: Surface|str):
        super().__init__()
        self.item_name = item
        self.surface_name = surface.name if isinstance(surface, Surface) else surface

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return Has(f'{self.surface_name}/{self.item_name}/{self.level.name}')
