from __future__ import annotations

import itertools
import typing

from BaseClasses import Item, ItemClassification

from ..config import game_name, progressive_technologies
from ..data.raw import science_packs, technologies
from ..data.utils import upgrades_levels, upgrades_map

if typing.TYPE_CHECKING:
    from .options import FactorioOptions


# Generate ids
item_ids = {}

ids = itertools.count(start=1)

for technology in technologies:
    if technology.name in upgrades_map:
        if upgrades_map[technology.name] in item_ids:
            continue
        item_ids[upgrades_map[technology.name]] = next(ids)
    else:
        item_ids[technology.name] = next(ids)

item_ids['progressive science-pack'] = next(ids)
for progressive_name in progressive_technologies:
    item_ids[progressive_name] = next(ids)

del ids


class FactorioItem(Item):
    game = game_name

    def __init__(self, name: str, classification: ItemClassification, player: int):
        super().__init__(name, classification, item_ids[name], player)


def create_item(progressive_levels: dict[str, list[str]], player: int, item_name: str) -> FactorioItem:
    if item_name in upgrades_levels:
        technology = upgrades_levels[item_name][-1]
    elif item_name in progressive_levels:
        technology = progressive_levels[item_name][-1]
    else:
        technology = technologies[name]

    if technology.has_unlock:
        classification = ItemClassification.progression
    elif technology.has_modifier:
        classification = ItemClassification.useful
    else:
        classification = ItemClassification.filler

    return FactorioItem(item_name, classification, player)


def create_items(options: FactorioOptions, progressive_levels: dict[str, list[str]], player: int) -> list[FactorioItem]:
    # Build reverse progressive lookup map
    progressive_map: dict[str, str] = {}
    for name, levels in progressive_levels.items():
        for level in levels:
            progressive_map[level] = name

    items = []

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if technology.name in progressive_map:
            item_name = progressive_map[technology.name]
            index = progressive_levels[item_name].index(technology.name)
            technologies_to_check = [technologies[name] for name in progressive_levels[item_name][index:]]
        else:
            item_name = technology.name
            technologies_to_check = [technology]

        if any(map(lambda level: level.has_unlock, technologies_to_check)):
            classification = ItemClassification.progression
        elif any(map(lambda level: level.has_modifier, technologies_to_check)):
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.filler

        items.append(FactorioItem(item_name, classification, player))

    for item_name, levels in upgrades_levels.items():
        count = options.upgrades_count[item_name]

        for level in range(0, count):
            if level >= len(levels):
                if levels[-1].has_modifier:
                    classification = ItemClassification.useful
                else:
                    classification = ItemClassification.filler
            else:
                technologies_to_check = levels[level:]

                if any(map(lambda level: level.has_unlock, levels)):
                    classification = ItemClassification.progression
                elif any(map(lambda level: level.has_modifier, levels)):
                    classification = ItemClassification.useful
                else:
                    classification = ItemClassification.filler

            items.append(FactorioItem(item_name, classification, player))

    return items
