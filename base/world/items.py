import re

from BaseClasses import Item, ItemClassification

from ..config import game_name
from ..data import technologies
from ..data_classes import Technology


# Compute upgrades
upgrades_levels = {}
upgrades_max_level = {}
upgrades_map = {}

for technology in technologies:
    if not technology.upgrade and technology.max_level is None:
        continue

    match = re.match(r'^(?P<name>.+)-(?P<level>\d+)$', technology.name)
    if match:
        name = match.group('name')
        level = int(match.group('level'))
    else:
        name = technology.name
        level = 1

    if name not in upgrades_levels:
        upgrades_levels[name] = []
        upgrades_max_level[name] = 0

    upgrades_levels[name].append(technology)

    if upgrades_max_level[name] is not None:
        if technology.max_level == 'infinite':
            upgrades_max_level[name] = None
        else:
            upgrades_max_level[name] = max(upgrades_max_level[name], level)

    upgrades_map[technology.name] = name


# Generate ids
item_ids = {}
next_id = 1
for technology in technologies:
    if technology.name in upgrades_map:
        if upgrades_map[technology.name] in item_ids:
            continue
        item_ids[upgrades_map[technology.name]] = next_id
    else:
        item_ids[technology.name] = next_id
    next_id += 1
del next_id


class FactorioItem(Item):
    game = game_name


def _create_item_for_technology(player: int, item_name: str, technology: Technology) -> FactorioItem:
    if len(technology.unlocked_recipes) > 0 or len(technology.unlocked_space_locations) > 0:
        classification = ItemClassification.progression
    elif len(technology.modifiers) > 0:
        classification = ItemClassification.useful
    else:
        classification = ItemClassification.filler

    return FactorioItem(item_name, classification, item_ids[item_name], player)


def create_item(player: int, item_name: str) -> FactorioItem:
    if item_name in upgrades_levels:
        technology = upgrades_levels[item_name][-1]
    else:
        technology = technologies[name]

    return _create_item_for_technology(player, item_name, technoloy)


def create_items(player: int) -> list[FactorioItem]:
    items = []

    for technology in technologies:
        if technology.name in upgrades_map:
            item_name = upgrades_map[technology.name]
        else:
            item_name = technology.name

        items.append(_create_item_for_technology(player, item_name, technology))

    return items
