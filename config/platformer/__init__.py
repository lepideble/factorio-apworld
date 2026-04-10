game_name = 'Factorio: Platformer'


# Mod dependencies
dependencies = [
    'platformer',
]


# Possible victory conditions
victory_conditions = [
    {
        'type': 'reach-space-location',
        'name': 'reach-solar-system-edge',
        'space_location': 'solar-system-edge',
    },
]


# Item that should be included in craftsanity
def craftsanity_filter(item_name: str):
    return not item_name.endswith('-barrel')
