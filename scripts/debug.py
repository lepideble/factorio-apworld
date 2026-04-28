import argparse
import sys
import os.path

def print_machines():
    from factorio_platformer.data.raw import machines

    for machine in machines:
        print(f'Machine: {machine.name}')
        print(f'  categories: {', '.join(machine.categories)}')


def print_recipes():
    from factorio_platformer.data.raw import recipes

    for recipe in recipes:
        print(f'Recipe: {recipe.name}')
        print(f'  category: {recipe.category}')
        print(f'  ingredients: {recipe.ingredients}')
        print(f'  products: {recipe.products}')


def print_science_packs():
    from factorio_platformer.data.raw import science_packs

    for science_pack in science_packs:
        print(f'Science pack: {science_pack}')


def print_surfaces():
    from factorio_platformer.data.raw import surfaces

    for surface in surfaces:
        print(f'Surface: {surface.name}')
        print('  properties:')
        for name, value in surface.properties.items():
            print(f'    {name}: {value}')


def print_technologies():
    from factorio_platformer.data.raw import technologies

    for technology in technologies:
        print(f'Technology: {technology.name}')
        print(f'  upgrade: {technology.upgrade}')
        if technology.max_level is not None:
            print(f'  upgrade: {technology.max_level}')
        if len(technology.unlocked_recipes) > 0:
            print(f'  unlocked_recipes: {', '.join(technology.unlocked_recipes)}')
        if len(technology.unlocked_space_locations) > 0:
            print(f'  unlocked_space_locations: {', '.join(technology.unlocked_space_locations)}')
        if len(technology.modifiers) > 0:
            print(f'  modifiers: {technology.modifiers}')


def create_options(options_dict):
    from factorio_platformer.world.options import FactorioOptions
    options = {}
    for key, option in FactorioOptions.type_hints.items():
        options[key] = option.from_any(options_dict.get(key, option.default))

    return FactorioOptions(**options)

def create_world(options_dict):
    from BaseClasses import MultiWorld
    from factorio_platformer.world import FactorioWorld

    multiworld = MultiWorld(1)
    world = FactorioWorld(multiworld, 1)
    multiworld.worlds[1] = world
    world.options = create_options(options_dict)

    world.create_regions()
    world.create_items()

    return multiworld


def print_items(options_dict):
    from factorio_platformer.config import progressive_items_with_split_technologies, progressive_items_without_split_technologies
    from factorio_platformer.world.items.factory import create_items
    from factorio_platformer.world.items.progressive import make_progressive

    options = create_options(options_dict)

    progressive_items = {}
    if options.progressive:
        if options.split_technologies:
            progressive_items = progressive_items_with_split_technologies
        else:
            progressive_items = progressive_items_without_split_technologies

    for item in make_progressive(create_items(options, 0), progressive_items):
        print(f'{item.name}:')
        print(f'  id: {item.code}')
        print(f'  classification: {item.classification.name}')


def print_locations():
    multiworld = create_world()

    for location in multiworld.get_locations():
        print(f'{location.name}')


def main(what, options):
    options_dict = {}
    for option in options:
        [key, value] = option.split('=', 1)
        options_dict[key] = value

    # Data
    if what == 'machines':
        print_machines()
    if what == 'recipes':
        print_recipes()
    if what == 'science-packs':
        print_science_packs()
    if what == 'surfaces':
        print_surfaces()
    if what == 'technologies':
        print_technologies()

    # World
    if what == 'items':
        print_items(options_dict)
    if what == 'locations':
        print_locations(options_dict)

parser = argparse.ArgumentParser()
parser.add_argument('what')
parser.add_argument('-o', '--option', action='append', default=[], dest='options')

# Debug
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build'))

    main(**vars(parser.parse_args()))
