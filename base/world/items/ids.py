import itertools

from ...config import progressive_technologies
from ...data.raw import technologies
from ...data.utils import upgrades_map


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
