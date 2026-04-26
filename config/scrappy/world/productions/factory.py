from rule_builder.rules import Rule, True_

from ...data.classes import Surface
from ..rules import CanAutomate, CanCraft, UnlockedRecipe
from .factory_base import get_productions as base_get_productions


scrap_items = {'circuit-scrap', 'copper-scrap', 'iron-scrap', 'mech-scrap', 'plastic-bits', 'steel-scrap'}


def add_condition(productions, name, rule):
    productions[name] = (productions[name][0] & rule, productions[name][1])


def get_productions(surface: Surface) -> dict[str, tuple[Rule, dict[str, bool]]]:
    productions = base_get_productions(surface)

    # Scraps items should never be considered automated
    productions = {
        name: (
            rule,
            {
                item: automated and item not in scrap_items
                for (item, automated) in production.items()
            },
        )
        for name, (rule, production) in productions.items()
    }

    del productions['Automate advanced-circuit-from-scrap crafting']
    del productions['Automate copper-plate-from-scrap crafting']
    del productions['Automate electric-engine-unit-from-scrap crafting']
    del productions['Automate electronic-circuit-from-scrap crafting']
    del productions['Automate engine-unit-from-scrap crafting']
    del productions['Automate iron-plate-from-scrap crafting']
    del productions['Automate plastic-bar-from-bits crafting']
    del productions['Automate processing-unit-from-scrap crafting']
    del productions['Automate sort-mech-scrap crafting']
    del productions['Automate steel-plate-from-scrap crafting']

    # Anything with multiple fluid output needs a storage tank to mesure levels
    has_storage_tank = CanCraft('storage-tank', surface)

    add_condition(productions, 'Automate advanced-oil-processing crafting', has_storage_tank)
    add_condition(productions, 'Automate basic-oil-processing crafting', has_storage_tank)
    add_condition(productions, 'Automate butane-pollution crafting', has_storage_tank)
    add_condition(productions, 'Automate coal-liquefaction crafting', has_storage_tank)
    add_condition(productions, 'Automate tar-liquefaction crafting', has_storage_tank)

    # Anything using fish can't be automated
    del productions['Automate spidertron crafting']

    # Anything using wood can't be automated
    del productions['Automate combat-shotgun crafting']
    del productions['Automate shotgun crafting']
    del productions['Automate small-electric-pole crafting']
    del productions['Automate wooden-chest crafting']

    # Combustion results
    productions['Burn uranium-fuel-cell'] = (
        CanCraft('nuclear-reactor', surface) & CanAutomate('uranium-fuel-cell', surface),
        {'depleted-uranium-fuel-cell': True},
    )

    # Steam
    productions['Heat water'] = (
        CanCraft('boiler', surface) & CanAutomate('coal', surface) & CanAutomate('water', surface),
        {'steam': True},
    )

    return productions
