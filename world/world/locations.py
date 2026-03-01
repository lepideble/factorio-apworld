from ..data import science_packs

science_location_pools: dict[str, list[str]] = {}

for i, pack in enumerate(science_packs, start=1):
    max_needed: int = 999
    prefix: str = f"AP-{i}-"
    science_location_pools[pack] = [prefix + str(x).upper().zfill(3) for x in range(1, max_needed + 1)]

location_ids = {}

next_id = 1
for pool in science_location_pools.values():
    location_ids.update({name: id for id, name in enumerate(pool, start=next_id)})
    next_id += len(pool)
del next_id
