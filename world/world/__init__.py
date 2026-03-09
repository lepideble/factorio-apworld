from BaseClasses import Region, Location, Item, ItemClassification
from worlds.AutoWorld import World

from ..config import game_name
from ..data import craftable_recipes, space_locations, surfaces, surfaces_accessible_at_start, technologies

from .items import item_ids
from .locations import location_ids, science_location_pools, FactorioLocation, FactorioScienceLocation
from .options import FactorioOptions

class FactorioItem(Item):
    game = game_name

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

            for recipe_name in craftable_recipes:
                region.add_event(f'Automate {recipe_name} on {surface.name}')
                region.add_event(f'Craft {recipe_name} on {surface.name}')

            if surface.is_space_platform:
                for space_location in space_locations:
                    region.add_event(f'Reach {space_location.name} with {surface.name}')

            self.multiworld.regions.append(region)

        # Create science locations
        science_location_pool = []

        for pack in self.options.max_science_pack.get_allowed_packs():
            science_location_pool.extend(science_location_pools[pack])

        self.science_locations = []
        for science_location_name in self.random.sample(science_location_pool, len(technologies)):
            self.science_locations.append(FactorioScienceLocation(self.player, science_location_name, None, menu_region))

        menu_region.locations.extend(self.science_locations)

        # Attribute counts to science locations
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

    def create_items(self) -> None:
        for technology in technologies:
            self.multiworld.itempool.append(self.create_item(technology.name))

    def set_rules(self) -> None:
        from .rules import get_rules

        for location_name, rule in get_rules(self.get_locations()).items():
            self.set_rule(self.get_location(location_name), rule)

    def create_item(self, name: str) -> FactorioItem:
        technology = technologies[name]

        if len(technology.unlocked_recipes) > 0 or len(technology.unlocked_space_locations) > 0:
            classification = ItemClassification.progression
        elif len(technology.modifiers) > 0:
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.filler

        return FactorioItem(name, classification, item_ids[name], self.player)
