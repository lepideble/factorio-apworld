from .classification_base import is_advancement as base_is_advancement, is_useful


def is_advancement(name: str, level: int | None = None, split_technologies = None) -> bool:
    if name == 'physical-projectile-damage' and level <= 6:
        return True

    if name == 'stronger-explosives' and level <= 6:
        return True

    return base_is_advancement(name, level, split_technologies)
