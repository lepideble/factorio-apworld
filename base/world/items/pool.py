import collections
import itertools

from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map
from .classification import is_advancement


# Minimum, maximum and default count that can be added to the pool for each upgrade
upgrades_min_count: dict[str, int] = {}
upgrades_max_count: dict[str, int | None] = {}
upgrades_default_count: dict[str, int] = {}

for name, levels in upgrades_levels.items():
    for index in itertools.count():
        if not is_advancement(name, index):
            upgrades_min_count[name] = index
            break

    match levels[-1].max_level:
        case None:
            upgrades_max_count[name] = len(levels)
        case 'infinite':
            upgrades_max_count[name] = None
        case max_level:
            upgrades_max_count[name] = max_level

    if levels[-1].max_level is None:
        upgrades_default_count[name] = len(levels)
    else:
        upgrades_default_count[name] = len(levels) - 1


# Split technologies item pools
quality_pool = collections.Counter()
recipe_pool = collections.Counter()

for technology in technologies:
    # Ignore upgrades because it would make things messy
    if technology.name in upgrades_map:
        continue

    for quality_name in technology.unlocked_qualities:
        quality_pool[quality_name] += 1

    for recipe_name in technology.unlocked_recipes:
        recipe_pool[recipe_name] += 1
