from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map


def is_progression(name: str, level: int | None = None) -> bool:
    if name in upgrades_levels:
        assert level is not None and level > 0, f'Invalid level: {level}'

        if level > len(upgrades_levels[name]):
            return False

        return upgrades_levels[name][level-1].has_unlock
    else:
        assert name not in upgrades_map, f'Invalid name: {name}'
        assert level is None, f'Invalid level: {level}'

        return technologies[name].has_unlock


def is_usefull(name: str, level: int | None = None) -> bool:
    if name in upgrades_levels:
        assert level is not None and level > 0, f'Invalid level: {level}'

        if level > len(upgrades_levels[name]):
            return upgrades_levels[name][-1].has_modifier

        return upgrades_levels[name][level-1].has_modifier
    else:
        assert name not in upgrades_map, f'Invalid name: {name}'
        assert level is None, f'Invalid level: {level}'

        return technologies[name].has_modifier
