import itertools
import re

from BaseClasses import Item, ItemClassification

from ..config import game_name, progressive_technologies
from ..data import science_packs, technologies
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

ids = itertools.count(start=1)

item_ids['progressive science-pack'] = next(ids)

for technology in technologies:
    if technology.name in science_packs:
        continue

    if technology.name in upgrades_map:
        if upgrades_map[technology.name] in item_ids:
            continue
        item_ids[upgrades_map[technology.name]] = next(ids)
    else:
        item_ids[technology.name] = next(ids)

for progressive_name in progressive_technologies:
    item_ids[progressive_name] = next(ids)

del ids


class FactorioItem(Item):
    game = game_name

    def __init__(self, name: str, classification: ItemClassification, player: int):
        super().__init__(name, classification, item_ids[name], player)


def create_item(player: int, progressive_levels: dict[str, list[str]], item_name: str) -> FactorioItem:
    if item_name in upgrades_levels:
        technology = upgrades_levels[item_name][-1]
    elif item_name in progressive_levels:
        technology = progressive_levels[item_name][-1]
    else:
        technology = technologies[name]

    if len(technology.unlocked_recipes) > 0 or len(technology.unlocked_space_locations) > 0:
        classification = ItemClassification.progression
    elif len(technology.modifiers) > 0:
        classification = ItemClassification.useful
    else:
        classification = ItemClassification.filler

    return FactorioItem(item_name, classification, player)


def create_items(player: int, progressive_levels: dict[str, list[str]]) -> list[FactorioItem]:
    # Build reverse progressive lookup map
    progressive_map: dict[str, str] = {}
    for name, levels in progressive_levels.items():
        for level in levels:
            progressive_map[level] = name


    items = []

    for technology in technologies:
        if technology.name in upgrades_map:
            item_name = upgrades_map[technology.name]
            index = upgrades_levels[item_name].index(technology)
            levels = upgrades_levels[item_name][index:]
        elif technology.name in progressive_map:
            item_name = progressive_map[technology.name]
            index = progressive_levels[item_name].index(technology.name)
            levels = [technologies[name] for name in progressive_levels[item_name][index:]]
        else:
            item_name = technology.name
            levels = [technology]

        has_unlock = False
        has_modifier = False

        for level in levels:
            if len(level.unlocked_recipes) > 0 or len(level.unlocked_space_locations) > 0:
                has_unlock = True
            if len(level.modifiers) > 0:
                has_modifier = True

        if has_unlock:
            classification = ItemClassification.progression
        elif has_modifier:
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.filler

        items.append(FactorioItem(item_name, classification, player))

    return items
