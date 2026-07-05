from rule_builder.rules import Rule

from ...data.classes import Surface


def create_production_events(world, surface: Surface, events: dict[str, tuple[Rule, dict[str, bool]]]) -> None:
    region = world.get_region(surface.name)

    for name, (rule, production) in events.items():
        for (index, (item_name, automated)) in enumerate(production.items(), start=1):
            region.add_event(
                location_name=f'{name} output {index} on {surface.name}',
                item_name=get_production_item_name(surface.name, item_name, automated),
                rule=rule,
                show_in_spoiler=False,
            )


def get_production_item_name(surface_name: str, item_name: str, automated: bool):
    return f'Production of {item_name}{' automated' if automated else ''} on {surface_name}'
