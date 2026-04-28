from rule_builder.rules import Rule, True_

from ...data.classes import Surface
from ...data.raw import machines, offshore_pumps
from ...data.utils import machines_by_mining_category
from ..rules.classes import Any
from .rules import HasItem
from .level import ProductionLevel

def get_mining_events(surface: Surface) -> dict[str, tuple[Rule, list[str, ProductionLevel]]]:
    data = {}

    for resource in surface.resources:
        match (resource):
            case PumpableResource(name=name, fluid=fluid):
                data[f'Pump {name}'] = (Any([HasItem(offshore_pump, ProductionLevel.CRAFTABLE, surface) for offshore_pump in offshore_pumps]), [(fluid, ProductionLevel.AUTOMATED)])

            case GatherableResource(name=name, results=results):
                data[f'Gather {name}'] = (True_(), [(result, ProductionLevel.CRAFTABLE) for result in results])

            case MinableResource(name=name, category=category, results=results, mining_fluid=mining_fluid):
                if mining_fluid is None and category in machines['character'].mining_categories:
                    data[f'Gather {name}'] = (True_(), [(result, ProductionLevel.CRAFTABLE) for result in results])

                rule = Any([HasItem(machine.name, ProductionLevel.CRAFTABLE, surface) for machine in machines_by_mining_category(category) if machine.can_be_placed_on(surface)])
                if mining_fluid is not None:
                    rule &=  # TODO unlocked mining with fluid
                    rule &= HasItem(mining_fluid, ProductionLevel.AUTOMATED, surface)
                data[f'Mine {name}'] = (rule, [(result, ProductionLevel.AUTOMATED) for result in results])

    return data
