from dataclasses import dataclass

from rule_builder.rules import And, HasAny, Or, Rule, True_

from ..config import game_name
from ..data import recipes_by_product, recipes_unlocked_at_start, space_locations_unlocked_at_start, technologies_by_recipe_unlocked, technologies_by_space_location_unlocked

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
class UnlockedRecipe(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.name in recipes_unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by_recipe_unlocked(self.name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks recipe "{self.name}"')

        return HasAny(*[technology.name for technology in technologies]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


@dataclass()
class UnlockedSpaceLocation(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.name in space_locations_unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by_space_location_unlocked(self.name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks space location "{self.name}"')

        return HasAny(*[technology.name for technology in technologies]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
