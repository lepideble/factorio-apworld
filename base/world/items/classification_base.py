from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map


def is_advancement(name: str, index: int = 0, split_technologies: bool | None = None) -> bool:
    """
    Is the given item advancement.
    index represent the item index (equivalent to how many of that item is already in the pool)
    """

    assert index >= 0, 'Invalid index'

    if name in upgrades_levels:
        if index < len(upgrades_levels[name]):
            return any((
                upgrades_levels[name][index_to_check].has_unlock
                for index_to_check in range(index, len(upgrades_levels[name]))
            ))
        else:
            return False
    elif name.startswith('recipe: '):
        return index == 0
    else:
        if len(technologies[name].unlocked_space_locations) > 0:
            return True

        if not split_technologies and len(technologies[name].unlocked_recipes) > 0:
            return True

        return False


def is_useful(name: str, index: int = 0, split_technologies: bool | None = None) -> bool:
    """
    Is the given item useful.
    index represent the item index (equivalent to how many of that item is already in the pool)
    """

    assert index >= 0, 'Invalid index'

    if name in upgrades_levels:
        if index < len(upgrades_levels[name]):
            return any((
                upgrades_levels[name][index_to_check].has_modifier
                for index_to_check in range(index, len(upgrades_levels[name]))
            ))
        else:
            return upgrades_levels[name][-1].has_modifier
    elif name.startswith('recipe: '):
        return True
    else:
        return technologies[name].has_modifier
