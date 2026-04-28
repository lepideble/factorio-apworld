from random import Random
from collections import Iterable

from BaseClasses import Location, Region
from rule_builder.rules import Rule

from ...config import items_required_for_automation, items_required_for_research
from ...data.raw import science_packs
from ...data.utils import craftable_items_at_start
from ..options import FactorioOptions
from ..rules import All, Any, HasItem
from .classes import FactorioCraftLocation, FactorioLocation, FactorioScienceLocation
from .pool import craftsanity_item_pool, science_location_pools


def get_locations(options: FactorioOptions, random: Random, locations_to_create: int) -> list[FactorioLocation]:
    early_craftsanity_count = len(items_required_for_research(options))
    early_science_location_count = len(items_required_for_automation(options))
    craftsanity_count = min(options.craftsanity.value - early_craftsanity_count, locations_to_create - early_craftsanity_count - early_science_location_count)
    science_location_count = locations_to_create - early_craftsanity_count - early_science_location_count - craftsanity_count

    # Ensure enough early craftsanity location exists
    early_craftsanity_items = random.sample([item_name for item_name in craftsanity_item_pool if item_name in craftable_items_at_start], early_craftsanity_count)

    craftsanity_locations = [FactorioCraftLocation(0, item_name) for item_name in early_craftsanity_items]

    # Create remaining craftsanity locations
    craftsanity_items = random.sample([item_name for item_name in craftsanity_item_pool if item_name not in early_craftsanity_items], craftsanity_count)

    for item_name in craftsanity_items:
        craftsanity_locations.append(FactorioCraftLocation(0, item_name))

    # Ensure enough early science locations exists
    early_science_locations_names = random.sample(science_location_pools[science_packs[0]], early_science_location_count)

    science_locations = [FactorioScienceLocation(0, science_location_name) for science_location_name in early_science_locations_names]

    # Create remaining science locations
    science_location_pool = []

    for pack in options.max_science_pack.get_allowed_packs():
        for science_location_name in science_location_pools[pack]:
            if science_location_name not in early_science_locations_names:
                science_location_pool.append(science_location_name)

    for science_location_name in random.sample(science_location_pool, science_location_count):
        science_locations.append(FactorioScienceLocation(0, science_location_name))

    # Attribute ingredients to science locations
    for science_location in science_locations:
        science_location.ingredients = {science_packs[science_location.complexity]: 1}
        for complexity in range(science_location.complexity):
            if (options.tech_cost_mix > random.randint(0, 99)):
                science_location.ingredients[science_packs[complexity]] = 1

    # Attribute counts to science locations
    cost_distribution = options.tech_cost_distribution
    min_cost = options.min_tech_cost.value
    max_cost = options.max_tech_cost.value

    match cost_distribution:
        case cost_distribution.option_even:
            science_location_costs = (random.randint(min_cost, max_cost) for _ in science_locations)
        case cost_distribution.option_low:
            science_location_costs = (random.triangular(min_cost, max_cost, min_cost) for _ in science_locations)
        case cost_distribution.option_middle:
            science_location_costs = (random.triangular(min_cost, max_cost, (min_cost + max_cost) // 2) for _ in science_locations)
        case cost_distribution.option_high:
            science_location_costs = (random.triangular(min_cost, max_cost, max_cost) for _ in science_locations)

    science_location_costs = sorted(science_location_costs)

    if options.ramping_tech_costs:
        sorter = lambda location: (location.complexity, location.cost)
    else:
        sorter = lambda location: location.cost

    for i, location in enumerate(sorted(science_locations, key=sorter)):
        location.count = science_location_costs[i]

    science_locations.sort(key=lambda location: (location.complexity, location.cost))

    return craftsanity_locations + science_locations


def get_locations_rules(locations: Iterable[FactorioLocation]) -> dict[str, Rule]:
    rules = {}

    for location in locations:
        if isinstance(location, FactorioCraftLocation):
            rules[location.name] = Any([HasItem(surface, location.item_name) for surface in surfaces])

        if isinstance(location, FactorioScienceLocation):
            rules[location.name] = Any([
                All([
                    # Early science locations can be recognised by the fact that they already have an item
                    HasItem(surface, science_pack, location.item is None),
                    for science_pack in location.ingredients
                ])
                for surface in surfaces
            ])

    return rules
