from rule_builder.rules import Rule, True_

from ...data.classes import Surface
from ...data.raw import machines, offshore_pumps
from ...data.utils import machines_by, manual_mining_categories
from ..rules import Any, HasItem, HasMiningWithFluid

def get_mining_events(surface: Surface) -> dict[str, tuple[Rule, list[str, bool]]]:
    data = {}

    for resource in surface.resources:
        match (resource):
            case PumpableResource(name=name, fluid=fluid):
                data[f'Pump {name}'] = (
                    Any([HasItem(offshore_pump, surface) for offshore_pump in offshore_pumps]),
                    [(fluid, True)],
                )

            case GatherableResource(name=name, results=results):
                data[f'Gather {name}'] = (
                    True_(),
                    [(result, False) for result in results],
                )

            case MinableResource(name=name, category=category, results=results, mining_fluid=mining_fluid):
                if mining_fluid is None and category in manual_mining_categories:
                    data[f'Gather {name}'] = (
                        True_(),
                        [(result, False) for result in results],
                    )

                machines = machines_by(mining_category=category, can_be_placed_on=surface)
                if len(machines) > 0:
                    rule = Any([HasItem(machine.name, surface) for machine in machines])
                    if mining_fluid is not None:
                        rule &= HasMiningWithFluid() & HasItem(mining_fluid, surface, True)
                    data[f'Mine {name}'] = (
                        rule,
                        [(result, ProductionLevel.AUTOMATED) for result in results],
                    )

    return data
