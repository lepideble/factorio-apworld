from BaseClasses import Region, Location, Item, ItemClassification
from rule_builder.rules import Has
from worlds.AutoWorld import World

from ..config import game_name
from ..data import science_packs, space_locations, surfaces, surfaces_accessible_at_start, technologies, technologies_required_for_automation, technologies_required_for_research
from ..data_utils import craftable_recipes

from .items import create_item, create_items, item_ids, FactorioItem
from .locations import FactorioCraftLocation, FactorioScienceLocation, get_locations, location_ids
from .options import FactorioOptions

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
                region.add_event(f'Automate {recipe_name} on {surface.name}', show_in_spoiler=False)
                region.add_event(f'Craft {recipe_name} on {surface.name}', show_in_spoiler=False)

            if surface.is_space_platform:
                for space_location in space_locations:
                    if not space_location.accessible_at_start:
                        region.add_event(f'Reach {space_location.name} with {surface.name}', show_in_spoiler=False)

            self.multiworld.regions.append(region)

        for location in get_locations(self.options, self.random):
            location.player = self.player
            location.parent_region = menu_region

            menu_region.locations.append(location)

    def create_items(self) -> None:
        for item in create_items(self.player):
            if item.name in technologies_required_for_automation:
                # Early science locations are always placed at the start
                for location in self.get_locations():
                    if isinstance(location, FactorioScienceLocation) and location.item is None:
                        location.count = min(location.count, 10)
                        location.place_locked_item(item)

                        break
            elif item.name in technologies_required_for_research:
                # Early craft locations are always placed at the start
                for location in self.get_locations():
                    if isinstance(location, FactorioCraftLocation) and location.item is None:
                        location.place_locked_item(item)

                        break
            else:
                self.multiworld.itempool.append(item)

    def set_rules(self) -> None:
        from .rules import get_rules

        for location_name, rule in get_rules(self.get_locations()).items():
            self.set_rule(self.get_location(location_name), rule)

        match (self.options.goal.get_victory_condition()):
            case {'type': 'reach-space-location', 'space_location': space_location}:
                self.set_completion_rule(Has(f'Reach {space_location} with space-platform'))
            case _:
                raise Error('Invalid victory condition')

    def create_item(self, name: str) -> FactorioItem:
        return create_item(self.player, name)

    def generate_basic(self) -> None:
        world_generation = self.options.world_generation.value
        if world_generation['basic'].get('seed', None) is None:
            world_generation['basic']['seed'] = self.random.randint(0, 2 ** 32 - 1) # 32 bit uint

    def generate_output(self, output_directory: str) -> None:
        from ..mod.data import get_mod_data, get_mod_name, get_mod_version
        from ..mod.generate import generate_mod

        generate_mod(get_mod_name(self), get_mod_version(self), get_mod_data(self), self, output_directory)
