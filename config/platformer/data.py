# Technologies that we don't want to be randomized
ignored_technologies = ['automation', 'automation-science-pack', 'electronics', 'engine', 'solar-energy', 'space-platform', 'steel-processing']

# Stuff that is only disabled by platformer but should be considered removed
removed_technologies = [
    'heavy-armor',
    'battery-equipment',
    'belt-immunity-equipment',
    'night-vision-equipment',
    'modular-armor',
    'solar-panel-equipment',
    'toolbelt',
    'mining-productivity-1',
    'mining-productivity-2',
    'mining-productivity-3',
    'flamethrower',
    'defender',
    'follower-robot-count-1',
    'follower-robot-count-2',
    'follower-robot-count-3',
    'follower-robot-count-4',
    'follower-robot-count-5',
    'refined-flammables-1',
    'refined-flammables-2',
    'refined-flammables-3',
    'refined-flammables-4',
    'refined-flammables-5',
    'refined-flammables-6',
    'refined-flammables-7',
    'energy-shield-equipment',
    'exoskeleton-equipment',
    'personal-roboport-equipment',
    'worker-robots-speed-1',
    'worker-robots-speed-2',
    'worker-robots-speed-3',
    'worker-robots-speed-4',
    'worker-robots-speed-5',
    'worker-robots-speed-6',
    'worker-robots-speed-7',
    'braking-force-1',
    'braking-force-2',
    'braking-force-3',
    'braking-force-4',
    'braking-force-5',
    'braking-force-6',
    'braking-force-7',
    'construction-robotics',
    'power-armor',
    'worker-robots-storage-1',
    'worker-robots-storage-2',
    'worker-robots-storage-3',
    'discharge-defense-equipment',
    'personal-laser-defense-equipment',
    'distractor',
    'battery-mk2-equipment',
    'battery-mk3-equipment',
    'fission-reactor-equipment',
    'electric-weapons-damage-1',
    'electric-weapons-damage-2',
    'electric-weapons-damage-3',
    'electric-weapons-damage-4',
    'destroyer',
    'power-armor-mk2',
    'logistic-system',
    'personal-roboport-mk2-equipment',
    'energy-shield-mk2-equipment',
    'cliff-explosives',
    'mech-armor',
    'tree-seeding',
    'toolbelt-equipment',
    'fish-breeding',
    'spidertron',
    'fusion-reactor-equipment',
    'foundation',
    'health',
    'artillery-shell-speed-1',
    'artillery-shell-damage-1',
    'artillery-shell-range-1',
    'artillery',
    'logistic-robotics',
    'rocket-silo',
]

def override_data(machines, recipes, recipes_unlocked_at_start, surfaces, surfaces_accessible_at_start, technologies, **args):
    # Remove mining
    for recipe in recipes:
        if recipe.name.startswith("mining-"):
           del recipes[recipe.name]

           recipes_unlocked_at_start.remove(recipe.name)

    # Keep only space platform surface
    for surface in surfaces:
        if not surface.name == 'space-platform':
            del surfaces[surface.name]

    surfaces_accessible_at_start.clear()
    surfaces_accessible_at_start.add('space-platform')

    # Removed machines
    del machines['stone-furnace']
    del machines['steel-furnace']

    # Ignored technologies
    for technology_name in ignored_technologies:
        technology = technologies[technology_name]

        recipes_unlocked_at_start.update(technology.unlocked_recipes)

        del technologies[technology_name]

    # Removed technologies
    for technology_name in removed_technologies:
        del technologies[technology_name]
