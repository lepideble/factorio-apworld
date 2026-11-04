from collections import defaultdict

from .classes import GatherableResource, Machine, MinableResource, PumpableResource, Recipe, SpaceLocation, Surface, SurfaceCondition, Table, Technology
from .prototypes import get_prototype, get_prototypes


# Utility parsing functions
def parse_product_protoype_array(product_prototypes: list) -> dict[str, int|float]:
    result = {}

    for product_prototype in product_prototypes:
        if 'amount' in product_prototype:
            amount = product_prototype['amount']
        else:
            amount = (product_prototype['amount_min'] + product_prototype['amount_max']) / 2

        amount *= product_prototype.get('probability', 1)

        amount += product_prototype.get('extra_count_fraction', 0)

        result[product_prototype['name']] = amount

    return result

def parse_surface_condition_array(surface_conditions: list) -> list[SurfaceCondition]:
    return [SurfaceCondition(surface_condition['property'], surface_condition.get('min'), surface_condition.get('max')) for surface_condition in surface_conditions]


# Surfaces
surfaces = Table()
surfaces_accessible_at_start = {'nauvis'}

for prototype in get_prototypes('SurfacePrototype'):
    surfaces.add(Surface(prototype['name'], prototype['surface_properties']))

for prototype in get_prototypes('PlanetPrototype'):
    resources = []

    autoplace_controls = prototype['map_gen_settings']['autoplace_controls']
    autoplace_settings = prototype['map_gen_settings']['autoplace_settings']

    for tile_data in get_prototypes('TilePrototype'):
        autoplace = autoplace_settings['tile']['settings'].get(tile_data['name'], autoplace_controls.get(tile_data.get('autoplace', {}).get('control')))

        if autoplace is None:
            continue

        tile_name = tile_data['name']
        tile_fluid = tile_data.get('fluid')

        if tile_fluid is not None:
            resources.append(PumpableResource(tile_name, tile_fluid))

    for entity_data in get_prototypes('EntityPrototype'):
        autoplace = autoplace_settings['entity']['settings'].get(entity_data['name'], autoplace_controls.get(entity_data.get('autoplace', {}).get('control')))

        if autoplace is None:
            continue

        if 'minable' not in entity_data:
            continue

        entity_name = entity_data['name']
        minable_data = entity_data['minable']

        if 'results' in minable_data:
            results = parse_product_protoype_array(minable_data['results'])
        else:
            results = {minable_data['result']: minable_data.get('count', 1)}

        if entity_data['type'] == 'resource':
            resources.append(MinableResource(entity_name, entity_data.category, results, minable_data.get('required_fluid')))
        else:
            resources.append(GatherableResource(entity_name, results))

    surfaces.add(Surface(prototype['name'], prototype['surface_properties'], resources))


# Space locations
_asteroid_to_chunks = defaultdict(list)
_asteroid_to_asteroid = defaultdict(list)

for prototype in get_prototypes('AsteroidPrototype'):
    for dying_trigger_effect in prototype.get('dying_trigger_effect', []):
        if dying_trigger_effect['type'] == 'create-asteroid-chunk':
            _asteroid_to_chunks[prototype['name']].append(dying_trigger_effect['asteroid_name'])

        if dying_trigger_effect['type'] == 'create-entity':
            _asteroid_to_asteroid[prototype['name']].append(dying_trigger_effect['entity_name'])

def _recursive_asteroid_to_chunks(asteroid_name: str):
    asteroid_chunks = set(_asteroid_to_chunks.get(asteroid_name, []))

    for asteroid_name in _asteroid_to_asteroid.get(asteroid_name, []):
        asteroid_chunks.update(_recursive_asteroid_to_chunks(asteroid_name))

    return asteroid_chunks

space_locations = Table()

for prototype in get_prototypes('SpaceLocationPrototype'):
    asteroid_chunks = set()

    for asteroid_spawn_definition in prototype.get('asteroid_spawn_definitions', []):
        if asteroid_spawn_definition.get('type', 'entity') == 'asteroid-chunk':
            asteroid_chunks.add(asteroid_spawn_definition['asteroid'])
        else:
            asteroid_chunks.update(_recursive_asteroid_to_chunks(asteroid_spawn_definition['asteroid']))

    asteroid_chunks_results = set()
    for asteroid_chunk in asteroid_chunks:
        asteroid_chunk_data = get_prototype('AsteroidChunkPrototype', asteroid_chunk)
        if 'minable' in asteroid_chunk_data:
            asteroid_chunks_results.add(asteroid_chunk_data['minable']['result'])

    space_locations.add(SpaceLocation(
        name=prototype['name'],
        asteroid_chunks=asteroid_chunks_results,
        unlocked_at_start=prototype['name'] == 'nauvis',
        accessible_at_start=prototype['name'] == 'nauvis',
    ))

for prototype in get_prototypes('SpaceConnectionPrototype'):
    space_locations[prototype['from']].connections.add(prototype['to'])
    space_locations[prototype['to']].connections.add(prototype['from'])


# Machines
machines = Table()

for prototype in get_prototypes('CharacterPrototype'):
    machines.add(Machine(
        prototype['name'],
        [],
        set(prototype['crafting_categories']),
        set(prototype['mining_categories']),
    ))

for prototype in get_prototypes('CraftingMachinePrototype'):
    machines.add(Machine(
        prototype['name'],
        parse_surface_condition_array(prototype.get('surface_conditions', [])),
        set(prototype['crafting_categories']),
    ))

for prototype in get_prototypes('LabPrototype'):
    machines.add(Machine(
        prototype['name'],
        parse_surface_condition_array(prototype.get('surface_conditions', [])),
        allowed_science_packs=set(prototype['inputs']),
    ))

for prototype in get_prototypes('MiningDrillPrototype'):
    machines.add(Machine(
        prototype['name'],
        parse_surface_condition_array(prototype.get('surface_conditions', [])),
        set(),
        set(prototype['resource_categories']),
    ))

for prototype in get_prototypes('OffshorePumpPrototype'):
    machines.add(Machine(
        prototype['name'],
        parse_surface_condition_array(prototype.get('surface_conditions', [])),
        is_offshore_pump=True,
    ))

for prototype in get_prototypes('AsteroidCollectorPrototype'):
    machines.add(Machine(
        prototype['name'],
        parse_surface_condition_array(prototype.get('surface_conditions', [])),
        is_asteroid_collector=True,
    ))

machines_for_manual_craft = {'character'}


# Recipes
recipes = Table()
recipes_unlocked_at_start: dict[str] = set()

for prototype in get_prototypes('RecipePrototype'):
    recipe = Recipe(
        prototype['name'],
        set(prototype.get('categories', ['crafting'])),
        {ingredient['name']: ingredient['amount'] for ingredient in prototype.get('ingredients', [])},
        parse_product_protoype_array(prototype.get('results', [])),
        prototype.energy_required,
    )

    recipes.add(recipe)
    if prototype.enabled:
        recipes_unlocked_at_start.add(prototype['name'])


# Science packs
# this is a list because keeping the order in which they are defined is important
science_packs = list()

for prototype in get_prototypes('LabPrototype'):
    for science_pack in prototype['inputs']:
        if not science_pack in science_packs:
            science_packs.append(science_pack)


# Technologies
technologies = Table()

for prototype in get_prototypes('TechnologyPrototype'):
    technology = Technology(prototype['name'])

    for effect in prototype.get('effects', []):
        match effect['type']:
            case 'unlock-quality':
                technology.unlocked_qualities.add(effect['quality'])
            case 'unlock-recipe':
                technology.unlocked_recipes.add(effect['recipe'])
            case 'unlock-space-location':
                technology.unlocked_space_locations.add(effect['space_location'])
            case _:
                technology.modifiers.append(effect['type'])

    technology.upgrade = prototype.upgrade
    technology.max_level = prototype.get('max_level')

    if (unit := prototype.get('unit')) is not None:
        technology.unit_count = unit.get('count')

    technologies.add(technology)


# Items
items = set()

for prototype in get_prototypes('ItemPrototype'):
    if 'only-in-cursor' in prototype.get('flags', []):
        continue
    items.add(prototype['name'])
