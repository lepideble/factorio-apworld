from .classification_base import is_advancement as base_is_advancement, is_useful


def is_advancement(name: str, index: int = 0, split_technologies = None) -> bool:
    if name == 'physical-projectile-damage' and index < 6:
        return True

    if name == 'stronger-explosives' and index < 6:
        return True

    return base_is_advancement(name, index, split_technologies)
