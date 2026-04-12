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
    {
        'type': 'reach-space-location',
        'name': 'reach-aquilo',
        'space_location': 'aquilo',
    },
]

progressive_technologies = {
    'progressive automation': ['automation', 'automation-2', 'automation-3'],
    'progressive circuit': ['electronics', 'advanced-circuit', 'processing-unit', 'quantum-processor'],
    'progressive circuit-network': ['circuit-network', 'advanced-combinators'],
    'progressive logistics': ['logistics', 'logistics-2', 'logistics-3', 'turbo-transport-belt'],
    'progressive military': ['military', 'military-2', 'military-3', 'military-4'],
    'progressive quality': ['epic-quality', 'legendary-quality'],
    'progressive wall': ['stone-wall', 'gate'],
}

# Item that should be included in craftsanity
def craftsanity_filter(item_name: str):
    return not item_name.endswith('-barrel')
