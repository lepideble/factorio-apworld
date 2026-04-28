from .pool import craftsanity_item_pool, science_location_pools


location_ids = {}

next_id = 1
for pool in science_location_pools.values():
    location_ids.update({name: id for id, name in enumerate(pool, start=next_id)})
    next_id += len(pool)
for item_name in craftsanity_item_pool:
    location_ids[f'Craft {item_name}'] = next_id
    next_id += 1
del next_id
