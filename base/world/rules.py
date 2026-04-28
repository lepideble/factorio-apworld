import dataclasses

from rule_builder.rules import And, False_, Has, HasAny, Or, Rule, True_

from ..config import game_name
from ..data.classes import Recipe, Surface
from ..data.raw import recipes_unlocked_at_start, technologies
from ..data.utils import technologies_by_recipe_unlocked, upgrades_levels, upgrades_map
from .production.event import get_production_item_name


@dataclasses.dataclass()
class All(Rule['FactorioWorld'], game=game_name):
    rules: list[Rule]

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if len(self.rules) == 0:
            return True_().resolve(world)

        return And(*self.rules).resolve(world)


@dataclasses.dataclass()
class Any(Rule['FactorioWorld'], game=game_name):
    rules: list[Rule]

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if len(self.rules) == 0:
            return False_().resolve(world)

        return Or(*self.rules).resolve(world)


class HasTechnology(Rule['FactorioWorld'], game=game_name):
    technology_name: str

    def __init__(self, technology: Technology|str):
        super().__init__()
        self.technology_name = technology.name if isinstance(technology, Technology) else technology

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.technology_name in upgrades_map:
            item_name = upgrades_map[self.technology_name]
            level = upgrades_levels[item_name].index(technologies[self.technology_name]) + 1

            return Has(item_name, level).resolve(world)
        else:
            return Has(self.technology_name).resolve(world)


class HasMiningWithFluid(Rule['FactorioWorld'], game=game_name):
    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return Any([HasTechnology(technology) for technology in technologies if 'mining-with-fluid' in technology.modifiers]).resolve(world)


class HasRecipe(Rule['FactorioWorld'], game=game_name):
    recipe_name: str

    def __init__(self, recipe: Recipe|str):
        super().__init__()
        self.recipe_name = recipe.name if isinstance(recipe, Surface) else recipe

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.recipe_name in recipes_unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by_recipe_unlocked(self.recipe_name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks recipe "{self.recipe_name}"')

        if world.options.split_technologies:
            technologies = [technology for technology in technologies if technology.name in upgrades_map]

        return (Has(f'recipe: {self.recipe_name}') | Any([HasTechnology(technology) for technology in technologies])).resolve(world)


class HasItem(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str
    automated: bool

    def __init__(self, item: str, surface: Surface|str, automated: bool = False):
        super().__init__()
        self.item_name = item
        self.surface_name = surface.name if isinstance(surface, Surface) else surface
        self.automated = automated

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.automated:
            return Has(get_production_item_name(self.surface_name, self.item_name, True)).resolve(world)
        else:
            return HasAny(
                get_production_item_name(self.surface_name, self.item_name, True),
                get_production_item_name(self.surface_name, self.item_name, False),
            ).resolve(world)
