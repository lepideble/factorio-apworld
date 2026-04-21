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

# Early technologies
def items_required_for_research(options) -> set[str]:
    if options.split_technologies:
        return {'recipe: automation-science-pack', 'recipe: copper-cable', 'recipe: electronic-circuit', 'recipe: lab'}
    else:
        return {'automation-science-pack', 'electronics'}

def items_required_for_automation(options) -> set[str]:
    if options.split_technologies:
        return {
            'recipe: assembling-machine-1', 'recipe: engine-unit', 'recipe: inserter', 'recipe: long-handed-inserter',
            'recipe: pipe', 'recipe: solar-panel', 'recipe: splitter', 'recipe: steel-plate', 'recipe: underground-belt',
        }
    else:
        return {'automation', 'engine', 'logistics', 'solar-energy', 'steel-processing'}

progressive_items_with_split_technologies = {
    'progressive assembling machine': ['recipe: assembling-machine-1', 'recipe: assembling-machine-2', 'recipe: assembling-machine-3'],
    'progressive circuit': ['recipe: electronic-circuit', 'recipe: advanced-circuit', 'recipe: processing-unit', 'recipe: quantum-processor'],
    'progressive combinator': ['recipe: constant-combinator', 'recipe: arithmetic-combinator', 'recipe: decider-combinator', 'recipe: selector-combinator'],
    'progressive concrete': ['recipe: concrete', 'recipe: refined-concrete'],
    'progressive inserter': ['recipe: inserter', 'recipe: long-handed-inserter', 'recipe: fast-inserter', 'recipe: bulk-inserter', 'recipe: stack-inserter'],
    'progressive oil processing': ['recipe: basic-oil-processing', 'recipe: advanced-oil-processing'],
    'progressive pipe': ['recipe: pipe', 'recipe: pipe-to-ground'],
    'progressive pipe casting': ['recipe: casting-pipe', 'recipe: casting-pipe-to-ground'],
    'progressive quality': ['quality-module', 'epic-quality', 'legendary-quality'],
    'progressive rail': ['recipe: rail', 'recipe: rail-ramp', 'recipe: rail-support'],
    'progressive rail automation': ['recipe: train-stop', 'recipe: rail-signal', 'recipe: rail-chain-signal'],
    'progressive splitter': ['recipe: splitter', 'recipe: fast-splitter', 'recipe: express-splitter', 'recipe: turbo-splitter'],
    'progressive train': ['recipe: locomotive', 'recipe: cargo-wagon', 'recipe: fluid-wagon'],
    'progressive transport belt': ['recipe: fast-transport-belt', 'recipe: express-transport-belt', 'recipe: turbo-transport-belt'],
    'progressive underground belt': ['recipe: underground-belt', 'recipe: fast-underground-belt', 'recipe: express-underground-belt', 'recipe: turbo-underground-belt'],
    'progressive wall': ['recipe: stone-wall', 'recipe: gate'],
    # Bacteria
    'progressive copper bacteria': ['recipe: copper-bacteria', 'recipe: copper-bacteria-cultivation'],
    'progressive iron bacteria': ['recipe: iron-bacteria', 'recipe: iron-bacteria-cultivation'],
    # Modules
    'progressive efficiency module': ['recipe: efficiency-module', 'recipe: efficiency-module-2', 'recipe: efficiency-module-3'],
    'progressive productivity module': ['recipe: productivity-module', 'recipe: productivity-module-2', 'recipe: productivity-module-3'],
    'progressive quality module': ['recipe: quality-module', 'recipe: quality-module-2', 'recipe: quality-module-3'],
    'progressive speed module': ['recipe: speed-module', 'recipe: speed-module-2', 'recipe: speed-module-3'],
    # Propellants
    'progressive thruster fuel': ['recipe: thruster-fuel', 'recipe: advanced-thruster-fuel'],
    'progressive thruster oxidizer': ['recipe: thruster-oxidizer', 'recipe: advanced-thruster-oxidizer'],
}

progressive_items_without_split_technologies = {
    'progressive automation': ['automation', 'automation-2', 'automation-3'],
    'progressive circuit': ['electronics', 'advanced-circuit', 'processing-unit', 'quantum-processor'],
    'progressive circuit network': ['circuit-network', 'advanced-combinators'],
    'progressive inserter': ['fast-inserter', 'bulk-inserter', 'stack-inserter'],
    'progressive logistics': ['logistics', 'logistics-2', 'logistics-3', 'turbo-transport-belt'],
    'progressive oil processing': ['oil-processing', 'advanced-oil-processing'],
    'progressive railway': ['railway', 'elevated-rail', 'rail-support-foundations'],
    'progressive quality': ['epic-quality', 'legendary-quality'],
    'progressive wall': ['stone-wall', 'gate'],
    # Modules
    'progressive efficiency module': ['efficiency-module', 'efficiency-module-2', 'efficiency-module-3'],
    'progressive productivity module': ['productivity-module', 'productivity-module-2', 'productivity-module-3'],
    'progressive quality module': ['quality-module', 'quality-module-2', 'quality-module-3'],
    'progressive speed module': ['speed-module', 'speed-module-2', 'speed-module-3'],
}

# Item that should be included in craftsanity
def craftsanity_filter(item_name: str):
    return not item_name.endswith('-barrel') and not item_name.endswith('-asteroid-chunk')
