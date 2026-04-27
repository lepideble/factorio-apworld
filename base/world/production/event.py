from BaseClasses import Item, ItemClassification, Location, Region

from ...config import game_name
from ...data.classes import Surface


class FactorioProductionEventItem(Item):
    game = game_name
    production: list[str, bool]
    surface: Surface

    def __init__(self, player: int, name: str, production: list[str, bool], surface: Surface):
        super().__init__(player, name, ItemClassification.progression, None)
        self.production = production
        self.surface = surface

    def get_production_item_names(self):
        for item_name, item_production_level in self.production:
            for production_level in ProductionLevel:
                if production_level.value <= item_production_level.value
                    yield f'{self.surface.name}/{item_name}/{production_level.name}'


class FactorioProductionEventLocation(Location):
    game = game_name

    def __init__(self, player: int, name: str, parent: Region | None = None):
        super().__init__(player, name, None, parent)
        self.show_in_spoiler = False


def create_production_event(world, surface, events) -> None:
    region = world.get_region(surface.name)

    for name, (rule, production) in events:
        event_item = FactorioProductionEventItem(region.player, f'{name} on {surface.name}', production, surface)
        event_location = FactorioProductionEventLocation(region.player, f'{name} on {surface.name}', region)

        rworld.set_rule(event_location, rule)

        event_location.place_locked_item(event_item)

        region.locations.append(event_location)


def get_production_item_name(surface_name: str, item_name: str, automated: bool):
    return f'{surface_name}/{item_name}{'/automated' if automated else ''}'


def collect_production_event(state, item: FactorioProductionEventItem) -> bool:
    for item_name, automated in item.production:
        state.add_item(get_production_item_name(item.surface.name, item_name, automated))
    return True


def remove_production_event(state, item: FactorioProductionEventItem) -> bool:
    for item_name, automated in item.production:
        state.remove_item(get_production_item_name(item.surface.name, item_name, automated))
    return True
