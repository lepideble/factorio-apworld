from rule_builder.rules import Has, Rule, True_

from ...data.classes import Surface
from ...data.raw import space_locations
from ...data.utils import manual_asteroid_collection
from ..rules import Any, HasItem

def get_asteroids_events(surface: Surface) -> dict[str, tuple[Rule, list[str, bool]]]:
    events = {}

    if surface.is_space_platform:
        available_asteroid_chunks = set()
        for space_location in space_locations:
            available_asteroid_chunks.update(space_location.asteroid_chunks)

        for asteroid_chunk in available_asteroid_chunks:
            reached_location_rule = Any([
                True_() if space_location.accessible_at_start else Has(f'Reach {space_location.name} with {surface.name}')
                for space_location in space_locations
                if asteroid_chunk in space_location.asteroid_chunks
            ])

            if manual_asteroid_collection:
                events[f'Collect {asteroid_chunk}'] = (
                    reached_location_rule,
                    [(asteroid_chunk, False)],
                )

            machines = # TODO
            if len(machines) > 0:
                events[f'Automate {asteroid_chunk} collection'] = (
                    Any([HasItem(machine.name, surface) for machine in machines]) & reached_location_rule,
                    [(asteroid_chunk, True)],
                )

    return events
