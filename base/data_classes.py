from dataclasses import dataclass, field
from typing import Literal

@dataclass
class Base:
    name: str

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __hash__(self):
        return hash(self.name)


class Table:
    data: dict[str, Base]

    def __init__(self):
        self.data = {}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key: str):
        return self.data[key]

    def __delitem__(self, key: str):
        del self.data[key]

    def __contains__(self, key: str):
        return key in self.data

    def __iter__(self):
        return map(lambda name: self.data[name], sorted(self.data.keys()))

    def add(self, item: Base):
        self.data[item.name] = item


class Surface(Base):
    properties: dict[str, float]

    def __init__(self, name: str, properties: dict[str, float]):
        super().__init__(name)
        self.properties = properties

    @property
    def is_space_platform(self) -> bool:
        return self.name == 'space-platform'


@dataclass
class SpaceLocation(Base):
    asteroid_chunks: set[str] = field(default_factory=set)
    connections: set[str] = field(default_factory=set)
    unlocked_at_start: bool = False
    accessible_at_start: bool = False


@dataclass
class SurfaceCondition:
    property: str
    min: float | None
    max: float | None

    def accept(self, surface: Surface) -> bool:
        self.accept_value(surface.properties[self.property])

    def accept_value(self, value: float) -> bool:
        if self.min is not None and value < self.min:
            return False

        if self.max is not None and value > self.max:
            return False

        return True

    @classmethod
    def from_data(cls, data):
        return cls(data['property'], data.get('min'), data.get('max'))


class Lab(Base):
    inputs: set[str]
    surface_conditions: list[SurfaceCondition]

    def __init__(self, name: str, inputs: set[str], surface_conditions: list[SurfaceCondition]):
        super().__init__(name)
        self.inputs = inputs
        self.surface_conditions = surface_conditions


class Machine(Base):
    categories: set[str]
    surface_conditions: list[SurfaceCondition]

    def __init__(self, name: str, categories: set[str], surface_conditions: list[SurfaceCondition] = None):
        super().__init__(name)
        self.categories = categories
        self.surface_conditions = surface_conditions if surface_conditions is not None else list()

    def can_be_placed_on(self, surface: Surface) -> bool:
        return all(map(lambda surface_condition: surface_condition.accept(surface), self.surface_conditions))


class Recipe(Base):
    category: str
    ingredients: dict[str, int]
    products: dict[str, int | float] # int means an exact value, float an average
    time: float

    def __init__(self, name: str, category: str, ingredients: dict[str, int], products: dict[str, int | float], time: float):
        super().__init__(name)
        self.category = category
        self.ingredients = ingredients
        self.products = products
        self.time = time


class Technology(Base):
    upgrade: bool
    max_level: int | None | Literal['infinite']
    unlocked_recipes: set[str]
    unlocked_space_locations: set[str]
    modifiers: list[str]

    def __init__(self, name: str, upgrade = False, max_level = None, unlocked_recipes: set[str] = None, unlocked_space_locations: set[str] = None, modifiers: list[str] = None):
        super().__init__(name)
        self.upgrade = upgrade
        self.max_level = max_level
        self.unlocked_recipes = unlocked_recipes if unlocked_recipes is not None else set()
        self.unlocked_space_locations = unlocked_space_locations if unlocked_space_locations is not None else set()
        self.modifiers = modifiers if modifiers is not None else []
