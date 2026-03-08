from ..world.rules import CanCraft, HasRecipe


def override_rules(world):
    # Starting asteroid collector
    world.set_rule(world.get_location('Craft crudeic-asteroid-chunk on space-platform'), HasRecipe('crudeic-asteroid-chunk'))
    world.set_rule(world.get_location('Craft metallic-asteroid-chunk on space-platform'), HasRecipe('metallic-asteroid-chunk'))
    world.set_rule(world.get_location('Craft oxide-asteroid-chunk on space-platform'), HasRecipe('oxide-asteroid-chunk'))

    # Starting crusher
    world.set_rule(world.get_location('Craft crudeic-asteroid-crushing on space-platform'), HasRecipe('crudeic-asteroid-crushing') & CanCraft('crudeic-asteroid-chunk', 'space-platform'))
    world.set_rule(world.get_location('Craft metallic-asteroid-crushing on space-platform'), HasRecipe('metallic-asteroid-crushing') & CanCraft('metallic-asteroid-chunk', 'space-platform'))
    world.set_rule(world.get_location('Craft oxide-asteroid-crushing on space-platform'), HasRecipe('oxide-asteroid-crushing') & CanCraft('oxide-asteroid-chunk', 'space-platform'))

    # Starting furnace
    world.set_rule(world.get_location('Craft copper-plate on space-platform'), HasRecipe('copper-plate') & CanCraft('copper-ore', 'space-platform'))
    world.set_rule(world.get_location('Craft iron-plate on space-platform'), HasRecipe('iron-plate') & CanCraft('iron-ore', 'space-platform'))
    world.set_rule(world.get_location('Craft lithium-plate on space-platform'), HasRecipe('lithium-plate') & CanCraft('lithium', 'space-platform'))
    world.set_rule(world.get_location('Craft steel-plate on space-platform'), HasRecipe('steel-plate') & CanCraft('iron-plate', 'space-platform'))
    world.set_rule(world.get_location('Craft stone-brick on space-platform'), HasRecipe('stone-brick') & CanCraft('stone', 'space-platform'))

    # Starting assembling machine
    world.set_rule(world.get_location('Craft engine-unit on space-platform'), HasRecipe('engine-unit') & CanCraft('iron-gear-wheel', 'space-platform') & CanCraft('pipe', 'space-platform') & CanCraft('steel-plate', 'space-platform'))
