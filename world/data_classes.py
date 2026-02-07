class Base:
    name: str

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        return hash(self.name)


class Machine(Base):
    categories: set[str]

    def __init__(self, name: str, categories: set[str]):
        super().__init__(name)
        self.categories = categories


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
    def __init__(self, name: str):
        super().__init__(name)


class Technology(Base):
    unlocked_recipes: set[str]
    unlocked_space_locations: set[str]
    modifiers: list[str]

    def __init__(self, name: str, unlocked_recipes: set[str] = None, unlocked_space_locations: set[str] = None, modifiers: list[str] = None):
        super().__init__(name)
        self.unlocked_recipes = unlocked_recipes if unlocked_recipes is not None else set()
        self.unlocked_space_locations = unlocked_space_locations if unlocked_space_locations is not None else set()
        self.modifiers = modifiers if modifiers is not None else []
