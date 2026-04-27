game_name = 'Scrappy Factorio'


# Mod dependencies
dependencies = [
    'elevated-rails',
    'quality',
    'scrap-industry',
    'scrap-chemistry',
]


# Possible victory conditions
victory_conditions = [
    {
        'type': 'launch-rocket',
        'name': 'launch-rocket',
    },
]

# Early technologies
def items_required_for_research(options) -> set[str]:
    if options.split_technologies:
        return {
            # Lab
            'recipe: copper-cable',
            'recipe: electronic-circuit',
            'recipe: lab',
            # Power
            'recipe: boiler',
            'recipe: offshore-pump',
            'recipe: pipe',
            'recipe: small-electric-pole',
            'recipe: steam-engine',
            # Science pack
            'recipe: automation-science-pack',
        }
    else:
        return {
            'electronics',
            'steam-power',
            'automation-science-pack',
        }

def items_required_for_automation(options) -> set[str]:
    if options.split_technologies:
        return {
            # Automation
            'recipe: assembling-machine-1',
            'recipe: long-handed-inserter',
            # Logistics
            'recipe: splitter',
            'recipe: underground-belt',
            # Remaining stuff from technologies required for research
            'recipe: inserter',
            'recipe: pipe-to-ground',
        }
    else:
        return {
            'automation',
            'logistics',
        }

progressive_items_with_split_technologies = {
    'progressive assembling machine': ['recipe: assembling-machine-1', 'recipe: assembling-machine-2', 'recipe: assembling-machine-3'],
    'progressive circuit': ['recipe: electronic-circuit', 'recipe: advanced-circuit', 'recipe: processing-unit'],
    'progressive combinator': ['recipe: constant-combinator', 'recipe: arithmetic-combinator', 'recipe: decider-combinator', 'recipe: selector-combinator'],
    'progressive concrete': ['recipe: concrete', 'recipe: refined-concrete'],
    'progressive inserter': ['recipe: inserter', 'recipe: long-handed-inserter', 'recipe: fast-inserter', 'recipe: bulk-inserter'],
    'progressive oil processing': ['recipe: basic-oil-processing', 'recipe: advanced-oil-processing'],
    'progressive pipe': ['recipe: pipe', 'recipe: pipe-to-ground'],
    'progressive quality': ['quality: uncommon', 'quality: rare', 'quality: epic', 'quality: legendary'],
    'progressive rail': ['recipe: rail', 'recipe: rail-ramp', 'recipe: rail-support'],
    'progressive rail automation': ['recipe: train-stop', 'recipe: rail-signal', 'recipe: rail-chain-signal'],
    'progressive science-pack': ['recipe: automation-science-pack', 'recipe: logistic-science-pack', 'recipe: chemical-science-pack', 'recipe: military-science-pack', 'recipe: production-science-pack', 'recipe: utility-science-pack', 'recipe: satellite'],
    'progressive splitter': ['recipe: splitter', 'recipe: fast-splitter', 'recipe: express-splitter'],
    'progressive train': ['recipe: locomotive', 'recipe: cargo-wagon', 'recipe: fluid-wagon'],
    'progressive transport belt': ['recipe: fast-transport-belt', 'recipe: express-transport-belt'],
    'progressive underground belt': ['recipe: underground-belt', 'recipe: fast-underground-belt', 'recipe: express-underground-belt'],
    'progressive wall': ['recipe: stone-wall', 'recipe: gate'],
    # Modules
    'progressive efficiency module': ['recipe: efficiency-module', 'recipe: efficiency-module-2', 'recipe: efficiency-module-3'],
    'progressive productivity module': ['recipe: productivity-module', 'recipe: productivity-module-2', 'recipe: productivity-module-3'],
    'progressive quality module': ['recipe: quality-module', 'recipe: quality-module-2', 'recipe: quality-module-3'],
    'progressive speed module': ['recipe: speed-module', 'recipe: speed-module-2', 'recipe: speed-module-3'],
}

progressive_items_without_split_technologies = {
    'progressive automation': ['automation', 'automation-2', 'automation-3'],
    'progressive circuit': ['electronics', 'advanced-circuit', 'processing-unit'],
    'progressive circuit network': ['circuit-network', 'advanced-combinators'],
    'progressive inserter': ['fast-inserter', 'bulk-inserter'],
    'progressive logistics': ['logistics', 'logistics-2', 'logistics-3'],
    'progressive oil processing': ['oil-processing', 'advanced-oil-processing'],
    'progressive railway': ['railway', 'elevated-rail'],
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
    return not item_name.endswith('-barrel') and not item_name.endswith('-scrap') and not item_name.endswith('-bits')
