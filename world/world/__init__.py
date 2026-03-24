from BaseClasses import Region, Location, Item, ItemClassification
from worlds.AutoWorld import World

from ..config import game_name
from ..data import craftable_recipes, space_locations, surfaces, surfaces_accessible_at_start, technologies

from .items import item_ids
from .locations import get_locations, location_ids
from .options import FactorioOptions

class FactorioItem(Item):
    game = game_name

class FactorioWorld(World):
    game = game_name

    item_name_to_id = item_ids
    location_name_to_id = location_ids

    options_dataclass = FactorioOptions
    options: FactorioOptions

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

        for location in get_locations(self.options, self.random):
            location.player = self.player
            location.parent_region = menu_region

            menu_region.locations.append(location)

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
