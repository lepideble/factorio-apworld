from collections.abc import Iterable

from rule_builder.rules import Rule

from ..data.raw import recipes, space_locations
from ..world.locations import FactorioLocation
from ..world.rules_classes import CanAutomate, CanCraft


def override_rules(locations: Iterable[FactorioLocation], rules: dict[str, Rule]):
    # Advanced oil processing need to have storage tanks to mesure output levels
    rules['Automate advanced-oil-processing on space-platform'] &= CanCraft('storage-tank', 'space-platform')
    rules['Automate heavy-oil-cracking on space-platform'] &= CanCraft('storage-tank', 'space-platform')
    rules['Automate light-oil-cracking on space-platform'] &= CanCraft('storage-tank', 'space-platform')

    # Space location rules
    can_destroy_medium_asterorid = CanCraft('gun-turret', 'space-platform') & CanAutomate('firearm-magazine', 'space-platform')
    can_destroy_big_asterorid = CanCraft('rocket-turret', 'space-platform') & CanAutomate('rocket', 'space-platform') & can_destroy_medium_asterorid
    can_destroy_huge_asterorid = CanCraft('railgun-turret', 'space-platform') & CanAutomate('railgun-ammo', 'space-platform') & can_destroy_big_asterorid

    has_truster_and_propellants = (
        CanCraft('thruster', 'space-platform')
            & CanAutomate('thruster-fuel', 'space-platform') & CanAutomate('thruster-oxidizer', 'space-platform')
            # Pipes are needed to transport propellants
            & CanCraft('pipe', 'space-platform') & CanCraft('pipe-to-ground', 'space-platform')
            # Pumps and storage tanks allow thruster throttling
            & CanCraft('pump', 'space-platform') & CanCraft('storage-tank', 'space-platform')
    )

    rules['Reach fulgora with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach gleba with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach vulcanus with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach aquilo with space-platform'] &= can_destroy_big_asterorid & has_truster_and_propellants
    rules['Reach solar-system-edge with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants
    rules['Reach shattered-planet with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants
