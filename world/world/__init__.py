from BaseClasses import Region, Location, Item, ItemClassification
from rule_builder.rules import And, HasAny, Or
from worlds.AutoWorld import World

from ..config import game_name, override_rules
from ..data import machines_by_category, recipes, recipes_by_product, science_packs, surfaces, surfaces_accessible_at_start, technologies, technologies_by_recipe_unlocked

from .items import item_ids
from .locations import location_ids, science_location_pools
from .options import FactorioOptions
from .rules import CanAutomate, CanCraft, HasMachine, HasRecipe

class FactorioItem(Item):
    game = game_name

class FactorioLocation(Location):
    game = game_name

class FactorioScienceLocation(FactorioLocation):
    complexity: int
    cost: int
    ingredients: dict[str, int]
    count: int = 0

    def __init__(self, player: int, name: str, address: int, parent: Region):
        super(FactorioScienceLocation, self).__init__(player, name, address, parent)
        # "AP-{Complexity}-{Cost}"
        self.complexity = int(self.name[3]) - 1
        self.cost = int(self.name[5:])

        self.ingredients = {science_packs[self.complexity]: 1}
        for complexity in range(self.complexity):
            if (parent.multiworld.worlds[self.player].options.tech_cost_mix >
                    parent.multiworld.worlds[self.player].random.randint(0, 99)):
                self.ingredients[science_packs[complexity]] = 1

class FactorioWorld(World):
    game = game_name

    item_name_to_id = item_ids
    location_name_to_id = location_ids

    options_dataclass = FactorioOptions
    options: FactorioOptions

    science_locations: list[FactorioScienceLocation]

    def __init__(self, multiworld, player: int):
        super().__init__(multiworld, player)

    def create_regions(self) -> None:
        # Menu region holds all locations that are not tied to a specific surface
        menu_region = Region('Menu', self.player, self.multiworld)

        self.multiworld.regions.append(menu_region)

        for surface in surfaces:
            region = Region(surface.name, self.player, self.multiworld)
            region.connect(menu_region)

            if surface.name in surfaces_accessible_at_start:
                menu_region.connect(region)

            for recipe in recipes:
                region.add_event(f'Automate {recipe.name} on {surface.name}')
                region.add_event(f'Craft {recipe.name} on {surface.name}')

            self.multiworld.regions.append(region)

        # Create science locations
        science_location_pool = []

        for pack in self.options.max_science_pack.get_allowed_packs():
            science_location_pool.extend(science_location_pools[pack])

        self.science_locations = []
        for science_location_name in self.random.sample(science_location_pool, len(technologies)):
            self.science_locations.append(FactorioScienceLocation(self.player, science_location_name, None, menu_region))

        cost_distribution = self.options.tech_cost_distribution
        min_cost = self.options.min_tech_cost.value
        max_cost = self.options.max_tech_cost.value

        match cost_distribution:
            case cost_distribution.option_even:
                science_location_costs = (self.random.randint(min_cost, max_cost) for _ in self.science_locations)
            case cost_distribution.option_low:
                science_location_costs = (self.random.triangular(min_cost, max_cost, min_cost) for _ in self.science_locations)
            case cost_distribution.option_middle:
                science_location_costs = (self.random.triangular(min_cost, max_cost, (min_cost + max_cost) // 2) for _ in self.science_locations)
            case cost_distribution.option_high:
                science_location_costs = (self.random.triangular(min_cost, max_cost, max_cost) for _ in self.science_locations)

        science_location_costs = sorted(science_location_costs)

        if self.options.ramping_tech_costs:
            sorter = lambda location: location.complexity, location.cost
        else:
            sorter = lambda location: location.cost

        for i, location in enumerate(sorted(self.science_locations, key=sorter)):
            location.count = science_location_costs[i]

        menu_region.locations.extend(self.science_locations)

    def create_items(self) -> None:
        for technology in technologies:
            self.multiworld.itempool.append(self.create_item(technology.name))

    def set_rules(self) -> None:
        for surface in surfaces:
            for recipe in recipes:
                self.set_rule(
                    self.get_location(f'Craft {recipe.name} on {surface.name}'),
                    And(
                        HasRecipe(recipe.name),
                        Or(*[HasMachine(machine.name, surface.name) for machine in machines_by_category(recipe.category) if machine.can_be_placed_on(surface)]),
                        And(*[CanCraft(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()]),
                    ),
                )

                self.set_rule(
                    self.get_location(f'Automate {recipe.name} on {surface.name}'),
                    And(
                        HasRecipe(recipe.name),
                        Or(*[HasMachine(machine.name, surface.name) for machine in machines_by_category(recipe.category) if machine.can_be_placed_on(surface) and machine.name != 'character']),
                        And(*[CanAutomate(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()]),
                    ),
                )

        for science_location in self.science_locations:
            self.set_rule(science_location, And(*[
                HasAny(*[f'Automate {science_pack} on {surface.name}' for surface in surfaces])
                for science_pack in science_location.ingredients.keys()
            ]))

        override_rules(self)

    def create_item(self, name: str) -> FactorioItem:
        technology = technologies[name]

        if len(technology.unlocked_recipes) > 0 or len(technology.unlocked_space_locations) > 0:
            classification = ItemClassification.progression
        elif len(technology.modifiers) > 0:
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.filler

        return FactorioItem(name, classification, item_ids[name], self.player)
