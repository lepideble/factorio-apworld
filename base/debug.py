def print_machines():
    from .data.raw import machines

    for machine in machines:
        print(f'Machine: {machine.name}')
        print(f'  categories: {', '.join(machine.categories)}')


def print_recipes():
    from .data.raw import recipes

    for recipe in recipes:
        print(f'Recipe: {recipe.name}')
        print(f'  category: {recipe.category}')
        print(f'  ingredients: {recipe.ingredients}')
        print(f'  products: {recipe.products}')


def print_science_packs():
    from .data.raw import science_packs

    for science_pack in science_packs:
        print(f'Science pack: {science_pack}')


def print_surfaces():
    from .data.raw import surfaces

    for surface in surfaces:
        print(f'Surface: {surface.name}')
        print('  properties:')
        for name, value in surface.properties.items():
            print(f'    {name}: {value}')


def print_technologies():
    from .data.raw import technologies

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


def create_world():
    from BaseClasses import MultiWorld
    from .world import FactorioWorld
    from .world.options import FactorioOptions, Goal, MaxSciencePack, MaxTechCost, MinTechCost, RampingTechCosts, TechCostDistribution, TechCostMix

    multiworld = MultiWorld(1)
    world = FactorioWorld(multiworld, 1)
    multiworld.worlds[1] = world
    world.options = FactorioOptions(
        progression_balancing=0,
        accessibility=0,
        local_items=0,
        non_local_items=0,
        start_inventory=0,
        start_hints=0,
        start_location_hints=0,
        exclude_locations=0,
        priority_locations=0,
        item_links=0,
        plando_items=0,
        max_science_pack=MaxSciencePack.from_any(MaxSciencePack.default),
        min_tech_cost=MinTechCost.from_any(MinTechCost.default),
        max_tech_cost=MaxTechCost.from_any(MaxTechCost.default),
        tech_cost_distribution=TechCostDistribution.from_any(TechCostDistribution.default),
        tech_cost_mix=TechCostMix.from_any(TechCostMix.default),
        ramping_tech_costs=RampingTechCosts.from_any(RampingTechCosts.default),
        goal=Goal.from_any(Goal.default),
    )

    world.create_regions()
    world.create_items()

    return multiworld


def print_items():
    multiworld = create_world()

    for item in multiworld.get_items():
        print(f'{item.name}:')
        print(f'  id: {item.code}')
        print(f'  classification: {repr(item.classification)}')


def print_locations():
    multiworld = create_world()

    for location in multiworld.get_locations():
        print(f'{location.name}')


def main(argv):
    # Data
    if '--all' in argv or '--machines' in argv:
        print_machines()
    if '--all' in argv or '--recipes' in argv:
        print_recipes()
    if '--all' in argv or '--science-packs' in argv:
        print_science_packs()
    if '--all' in argv or '--surfaces' in argv:
        print_surfaces()
    if '--all' in argv or '--technologies' in argv:
        print_technologies()

    # World
    if '--all' in argv or '--items' in argv:
        print_items()
    if '--all' in argv or '--locations' in argv:
        print_locations()


# Debug
if __name__ == '__main__':
    import sys

    main(sys.argv)
