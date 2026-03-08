from dataclasses import dataclass

from rule_builder.rules import And, HasAny, Or, Rule, True_

from ..config import game_name
from ..data import recipes_by_product, recipes_unlocked_at_start, technologies_by_recipe_unlocked

@dataclass()
class All(Rule['FactorioWorld'], game=game_name):
    rules: list[Rule]

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if len(self.rules) == 0:
            return True_().resolve(world)

        return And(*self.rules).resolve(world)

@dataclass()
class Any(Rule['FactorioWorld'], game=game_name):
    rules: list[Rule]

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if len(self.rules) == 0:
            return False_().resolve(world)

        return Or(*self.rules).resolve(world)

@dataclass()
class HasMachine(Rule['FactorioWorld'], game=game_name):
    machine_name: str
    surface_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.machine_name == 'character':
            return True_().resolve(world)
        else:
            return CanCraft(self.machine_name, self.surface_name).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(machine={self.machine_name}, surface={self.surface_name})"


@dataclass()
class CanCraft(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return HasAny(*[f'Craft {recipe.name} on {self.surface_name}' for recipe in recipes_by_product(self.item_name)]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(item={self.item_name}, surface={self.surface_name})"


@dataclass()
class CanAutomate(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return HasAny(*[f'Automate {recipe.name} on {self.surface_name}' for recipe in recipes_by_product(self.item_name)]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(item={self.item_name}, surface={self.surface_name})"


@dataclass()
class HasRecipe(Rule['FactorioWorld'], game=game_name):
    recipe_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.recipe_name in recipes_unlocked_at_start:
            return True_().resolve(world)

        return HasAny(*[technology.name for technology in technologies_by_recipe_unlocked(self.recipe_name)]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(recipe={self.recipe_name})"
