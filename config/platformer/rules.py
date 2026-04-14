from collections.abc import Iterable

from rule_builder.rules import Rule

from ..data.raw import recipes, space_locations
from ..world.locations import FactorioLocation
from ..world.rules_classes import CanAutomate, CanCraft


# Fuel
can_automate_chemical_fuel = (
    CanAutomate('coal') | CanAutomate('carbon')
        | CanAutomate('solid-fuel') | CanAutomate('rocket-fuel') | CanAutomate('nuclear-fuel')
        | CanAutomate('yumako') | CanAutomate('jellynut') | CanAutomate('yumako-mash') | CanAutomate('jelly')
)


# Power
has_boiler_power = CanCraft('boiler') & CanCraft('steam-engine') & can_automate_chemical_fuel
has_heating_power = CanCraft('heating-tower') & CanCraft('heat-exchanger') & CanCraft('steam-turbine') & can_automate_chemical_fuel
has_nuclear_power = CanCraft('nuclear-reactor') & CanCraft('heat-exchanger') & CanCraft('steam-turbine') & CanAutomate('uranium-fuel-cell')
has_fusion_power = CanCraft('fusion-reactor') & CanCraft('fusion-generator') & CanAutomate('fusion-power-cell')

has_non_solar_power = has_boiler_power | has_heating_power | has_nuclear_power | has_fusion_power


def override_rules(locations: Iterable[FactorioLocation], rules: dict[str, Rule]):
    # Advanced oil processing need to have storage tanks to mesure output levels
    rules['Automate advanced-oil-processing on space-platform'] &= CanCraft('storage-tank')
    rules['Automate heavy-oil-cracking on space-platform'] &= CanCraft('storage-tank')
    rules['Automate light-oil-cracking on space-platform'] &= CanCraft('storage-tank')

    # Space location rules
    can_destroy_medium_asterorid = CanCraft('gun-turret') & CanAutomate('firearm-magazine')
    can_destroy_big_asterorid = CanCraft('rocket-turret') & CanAutomate('rocket') & can_destroy_medium_asterorid
    can_destroy_huge_asterorid = CanCraft('railgun-turret') & CanAutomate('railgun-ammo') & can_destroy_big_asterorid

    has_truster_and_propellants = (
        CanCraft('thruster')
            & CanAutomate('thruster-fuel') & CanAutomate('thruster-oxidizer')
            # Pipes are needed to transport propellants
            & CanCraft('pipe') & CanCraft('pipe-to-ground')
            # Pumps and storage tanks allow thruster throttling
            & CanCraft('pump') & CanCraft('storage-tank')
    )

    rules['Reach fulgora with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach gleba with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach vulcanus with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach aquilo with space-platform'] &= can_destroy_big_asterorid & has_truster_and_propellants
    rules['Reach solar-system-edge with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power
    rules['Reach shattered-planet with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power
