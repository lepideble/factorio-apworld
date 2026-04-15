from collections.abc import Iterable

from rule_builder.rules import Rule

from ..locations import FactorioLocation, FactorioCraftLocation, FactorioScienceLocation
from .classes import All, CanAutomate, CanCraft


def get_locations_rules(locations: Iterable[FactorioLocation]) -> dict[str, Rule]:
    rules = {}

    for location in locations:
        if isinstance(location, FactorioCraftLocation):
            rules[location.name] = CanCraft(location.item_name)

        if isinstance(location, FactorioScienceLocation):
            # Early science locations can be recognised by the fact that they already have an item
            if location.item is not None:
                rules[location.name] = All([CanCraft(science_pack) for science_pack in location.ingredients.keys()])
            else:
                rules[location.name] = All([CanAutomate(science_pack) for science_pack in location.ingredients.keys()])

    return rules
