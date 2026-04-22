from BaseClasses import ItemClassification

from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map
from ..options import FactorioOptions
from .classes import FactorioItem, FactorioQualityItem, FactorioRecipeItem, FactorioTechnologyItem
from .classification import is_advancement, is_useful
from .pool import quality_pool, recipe_pool


def get_classification(advancement: bool, useful: bool) -> ItemClassification:
    if advancement:
        return ItemClassification.progression
    elif useful:
        return ItemClassification.useful
    else:
        return ItemClassification.filler


def create_item(options: FactorioOptions, player: int, name: str) -> FactorioItem:
    return FactorioItem(
        name,
        get_classification(
            is_advancement(name, 0, options.split_technologies),
            is_useful(name, 0, options.split_technologies),
        ),
        player
    )


def create_items(options: FactorioOptions, player: int) -> list[FactorioItem]:
    items = []

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if options.split_technologies:
            if len(technology.unlocked_space_locations) == 0 and len(technology.modifiers) == 0:
                continue

        items.append(FactorioTechnologyItem(
            technology.name,
            get_classification(
                is_advancement(technology.name, 0, options.split_technologies),
                is_useful(technology.name, 0, options.split_technologies),
            ),
            player,
        ))

    for item_name, levels in upgrades_levels.items():
        for index in range(0, options.upgrades_count[item_name]):
            items.append(FactorioTechnologyItem(
                item_name,
                get_classification(
                    is_advancement(item_name, index, options.split_technologies),
                    is_useful(item_name, index, options.split_technologies),
                ),
                player,
            ))

    if options.split_technologies:
        for quality_name, quality_count in quality_pool.items():
            for index in range(quality_count):
                items.append(FactorioQualityItem(
                    quality_name,
                    get_classification(
                        is_advancement(f'quality: {quality_name}', index),
                        is_useful(f'quality: {quality_name}', index),
                    ),
                    player,
                ))

        for recipe_name, recipe_count in recipe_pool.items():
            for index in range(recipe_count):
                items.append(FactorioRecipeItem(
                    recipe_name,
                    get_classification(
                        is_advancement(f'recipe: {recipe_name}', index),
                        is_useful(f'recipe: {recipe_name}', index),
                    ),
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
        count += quality_pool.total()
        count += recipe_pool.total()

    return count
