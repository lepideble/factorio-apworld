import itertools

from ...config import progressive_items_with_split_technologies, progressive_items_without_split_technologies
from ...data.raw import technologies
from ...data.utils import upgrades_map
from .pool import quality_pool, recipe_pool, space_location_pool


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

for quality_name in sorted(quality_pool.keys()):
    item_ids[f'quality: {quality_name}'] = next(ids)

for recipe_name in sorted(recipe_pool.keys()):
    item_ids[f'recipe: {recipe_name}'] = next(ids)

for space_location_name in sorted(space_location_pool.keys()):
    item_ids[f'space location: {space_location_name}'] = next(ids)

progressive_pool = {'progressive science-pack'}
progressive_pool.update(progressive_items_with_split_technologies.keys())
progressive_pool.update(progressive_items_without_split_technologies.keys())
for progressive_name in sorted(progressive_pool):
    item_ids[progressive_name] = next(ids)

del ids
