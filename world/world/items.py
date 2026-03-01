from ..data import technologies

item_ids = {}

next_id = 1
for technology in technologies:
    item_ids[technology.name] = next_id
    next_id += 1
del next_id
