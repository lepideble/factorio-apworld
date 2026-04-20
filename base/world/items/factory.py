from BaseClasses import ItemClassification

from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map
from ...utils import range_inclusive
from ..options import FactorioOptions
from .classes import FactorioItem, FactorioRecipeItem, FactorioTechnologyItem
from .classification import is_progression, is_usefull
from .pool import recipe_pool


def create_item(options: FactorioOptions, player: int, name: str) -> FactorioItem:
    if name in upgrades_levels:
        level = len(upgrades_levels[name])
    else:
        level = None

    if is_progression(name, level, options.split_technologies):
        classification = ItemClassification.progression
    elif is_usefull(name, level, options.split_technologies):
        classification = ItemClassification.useful
    else:
        classification = ItemClassification.filler

    return FactorioItem(name, classification, player)


def create_items(options: FactorioOptions, player: int) -> list[FactorioItem]:
    items = []

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if options.split_technologies:
            if len(technology.unlocked_space_locations) == 0 and len(technology.modifiers) == 0:
                continue

        if is_progression(technology.name, None, options.split_technologies):
            classification = ItemClassification.progression
        elif is_usefull(technology.name, None, options.split_technologies):
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.filler

        items.append(FactorioTechnologyItem(technology.name, classification, player))

    for item_name, levels in upgrades_levels.items():
        count = options.upgrades_count[item_name]

        for level in range_inclusive(1, count):
            if any((is_progression(item_name, level_to_check, options.split_technologies) for level_to_check in range_inclusive(level, count))):
                classification = ItemClassification.progression
            elif any((is_usefull(item_name, level_to_check, options.split_technologies) for level_to_check in range_inclusive(level, count))):
                classification = ItemClassification.useful
            else:
                classification = ItemClassification.filler

            items.append(FactorioTechnologyItem(item_name, classification, player))

    if options.split_technologies:
        for recipe_name, recipe_count in recipe_pool.items():
            for index in range(recipe_count):
                items.append(FactorioRecipeItem(
                    recipe_name,
                    ItemClassification.progression if index == 0 else ItemClassification.useful,
                    player,
                ))

    assert len(items) == get_item_count(options), 'Unexpected item count'

    return items


def get_item_count(options: FactorioOptions) -> int:
    count = 0

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if options.split_technologies:
            if len(technology.unlocked_space_locations) == 0 and len(technology.modifiers) == 0:
                continue

        count += 1

    for item_name in upgrades_levels.keys():
        count += options.upgrades_count[item_name]

    if options.split_technologies:
        count += recipe_pool.total()

    return count
