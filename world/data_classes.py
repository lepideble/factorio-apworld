from dataclasses import dataclass

class Base:
    name: str

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

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

    def __iter__(self):
        return map(lambda name: self.data[name], sorted(self.data.keys()))

    def add(self, item: Base):
        self.data[item.name] = item


@dataclass
class SurfaceCondition:
    property: str
    min: float | None
    max: float | None


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


class Surface(Base):
    properties: dict[str, float]

    def __init__(self, name: str, properties: dict[str, float]):
        super().__init__(name)
        self.properties = properties


class Technology(Base):
    unlocked_recipes: set[str]
    unlocked_space_locations: set[str]
    modifiers: list[str]

    def __init__(self, name: str, unlocked_recipes: set[str] = None, unlocked_space_locations: set[str] = None, modifiers: list[str] = None):
        super().__init__(name)
        self.unlocked_recipes = unlocked_recipes if unlocked_recipes is not None else set()
        self.unlocked_space_locations = unlocked_space_locations if unlocked_space_locations is not None else set()
        self.modifiers = modifiers if modifiers is not None else []
