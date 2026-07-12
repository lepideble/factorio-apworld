from BaseClasses import ItemClassification

from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map
from ..options import FactorioOptions
from .classes import classification, FactorioItem, FactorioQualityItem, FactorioRecipeItem, FactorioSpaceLocationItem, FactorioTechnologyItem
from .classification import is_advancement, is_useful
from .pool import quality_pool, recipe_pool, space_location_pool
from .progressive import make_progressive


def item_classification(name: str, index: int = 0, split_technologies: bool | None = None) -> ItemClassification:
    return classification(is_advancement(name, index, split_technologies), is_useful(name, index, split_technologies))


def create_item(options: FactorioOptions, progressive_chains: dict[str, list[str]], player: int, name: str) -> FactorioItem:
    if (progressive_chain := progressive_chains.get(name)):
        return FactorioItem(name, item_classification(progressive_chain[0], 0, options.split_technologies), player)
    else:
        return FactorioItem(name, item_classification(name, 0, options.split_technologies), player)


def create_items(options: FactorioOptions, progressive_chains: dict[str, list[str]], player: int) -> list[FactorioItem]:
    items = []

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if options.split_technologies and len(technology.modifiers) == 0:
            continue

        items.append(FactorioTechnologyItem(
            technology.name,
            item_classification(technology.name, 0, options.split_technologies),
            player,
        ))

    for item_name, levels in upgrades_levels.items():
        for index in range(0, options.upgrades_count[item_name]):
            items.append(FactorioTechnologyItem(
                item_name,
                item_classification(item_name, index, options.split_technologies),
                player,
            ))

    if options.split_technologies:
        for quality_name, quality_count in quality_pool.items():
            for index in range(quality_count):
                items.append(FactorioQualityItem(
                    quality_name,
                    item_classification(f'quality: {quality_name}', index),
                    player,
                ))

        for recipe_name, recipe_count in recipe_pool.items():
            for index in range(recipe_count):
                items.append(FactorioRecipeItem(
                    recipe_name,
                    item_classification(f'recipe: {recipe_name}', index),
                    player,
                ))

        for space_location_name, space_location_count in space_location_pool.items():
            for index in range(space_location_count):
                items.append(FactorioSpaceLocationItem(
                    space_location_name,
                    item_classification(f'space location: {space_location_name}', index),
                    player,
                ))

    assert len(items) == get_item_count(options), 'Unexpected item count'

    return make_progressive(items, progressive_chains)


def get_item_count(options: FactorioOptions) -> int:
    count = 0

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if options.split_technologies and len(technology.modifiers) == 0:
            continue

        count += 1

    for item_name in upgrades_levels.keys():
        count += options.upgrades_count[item_name]

    if options.split_technologies:
        count += quality_pool.total()
        count += recipe_pool.total()
        count += space_location_pool.total()

    return count
