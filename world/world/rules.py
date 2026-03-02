from dataclasses import dataclass

from rule_builder.rules import HasAny, Rule, True_

from ..config import game_name
from ..data import recipes_by_product, recipes_unlocked_at_start, technologies_by_recipe_unlocked

@dataclass()
class HasMachine(Rule['FactorioWorld'], game=game_name):
    machine_name: str
    surface_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.machine_name == 'character':
            return True_().resolve(world)
        else:
            return CanCraft(self.machine_name, self.surface_name).resolve(world)


@dataclass()
class CanCraft(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return HasAny(*[f'Craft {recipe.name} on {self.surface_name}' for recipe in recipes_by_product(self.item_name)]).resolve(world)


@dataclass()
class CanAutomate(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return HasAny(*[f'Automate {recipe.name} on {self.surface_name}' for recipe in recipes_by_product(self.item_name)]).resolve(world)


@dataclass()
class HasRecipe(Rule['FactorioWorld'], game=game_name):
    recipe_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.recipe_name in recipes_unlocked_at_start:
            return True_().resolve(world)

        return HasAny(*[technology.name for technology in technologies_by_recipe_unlocked(self.recipe_name)]).resolve(world)
