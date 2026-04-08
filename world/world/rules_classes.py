from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from rule_builder.rules import And, Has, HasAny, Or, Rule, True_

from ..config import game_name
from ..data import machines_available_at_start, recipes_by_product, recipes_unlocked_at_start, space_locations, technologies, technologies_by_recipe_unlocked, technologies_by_space_location_unlocked
from ..data_classes import Base, SpaceLocation, Surface

from .items import upgrades_map, upgrades_levels


T = TypeVar('T')
U = TypeVar('U')


@dataclass
class All(Generic[T]):
    children: list[T]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({', '.join(self.children)})'


@dataclass
class Any(Generic[T]):
    children: list[T]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({', '.join(self.children)})'


type Value[T] = T | All[T] | Any[T]


def _value_map(function: Callable[[T], U], value: Value[T]) -> Value[U]:
    if isinstance(value, All):
        return All([function(child) for child in value.children])

    if isinstance(value, Any):
        return Any([function(child) for child in value.children])

    return function(value)


def _get_name(value: Base | str) -> str:
    if isinstance(value, Base):
        return value.name

    return value


def _value_expand(function, value, *values) -> Rule:
    if len(values) > 0:
        expander = lambda child: _value_expand(lambda *rest: function(child, *rest), *values)
    else:
        expander = function

    if isinstance(value, All):
        if len(value.children) == 0:
            return True_()

        return And(*[expander(child) for child in value.children])

    if isinstance(value, Any):
        if len(value.children) == 0:
            return False_()

        return Or(*[expander(child) for child in value.children])

    return expander(value)


@dataclass()
class AllRule(Rule['FactorioWorld'], game=game_name):
    rules: list[Rule]

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if len(self.rules) == 0:
            return True_().resolve(world)

        return And(*self.rules).resolve(world)

@dataclass()
class AnyRule(Rule['FactorioWorld'], game=game_name):
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
        if self.machine_name in machines_available_at_start:
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
class HasTechnology(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        technology = technologies[self.name]

        if technology.name in upgrades_map:
            item_name = upgrades_map[technology.name]
            level = upgrades_levels[item_name].index(technology) + 1

            return Has(item_name, level).resolve(world)
        else:
            return Has(technology.name).resolve(world)


@dataclass()
class UnlockedRecipe(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.name in recipes_unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by_recipe_unlocked(self.name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks recipe "{self.name}"')

        return AnyRule([HasTechnology(technology.name) for technology in technologies]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


@dataclass()
class UnlockedSpaceLocation(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if space_locations[self.name].unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by_space_location_unlocked(self.name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks space location "{self.name}"')

        return AnyRule([HasTechnology(technology.name) for technology in technologies]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class ReachedSpaceLocation(Rule['FactorioWorld'], game=game_name):
    space_location_name: Value[str]
    surface_name: Value[str]

    def __init__(self, space_location: Value[SpaceLocation | str], surface: Value[Surface | str]):
        super().__init__()
        self.space_location_name = _value_map(_get_name, space_location)
        self.surface_name = _value_map(_get_name, surface)

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        def get_rule(space_location_name: str, surface_name: str) -> Rule:
            if space_locations[space_location_name].accessible_at_start:
                return True_()

            return Has(f'Reach {space_location_name} with {surface_name}')

        return _value_expand(get_rule, self.space_location_name, self.surface_name).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(space_location={self.space_location_name}, surface={self.surface_name})"
