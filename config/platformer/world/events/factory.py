from rule_builder.rules import Has, Rule

from ...data.classes import Surface
from ..rules import HasProduction
from .factory_base import get_events as base_get_events

def get_events(surface: Surface) -> dict[str, Rule]:
    # Fuel
    can_automate_chemical_fuel = (
        HasProduction('coal', surface, True) | HasProduction('carbon', surface, True)
            | HasProduction('solid-fuel', surface, True) | HasProduction('rocket-fuel', surface, True) | HasProduction('nuclear-fuel', surface, True)
            | HasProduction('yumako', surface, True) | HasProduction('jellynut', surface, True) | HasProduction('yumako-mash', surface, True) | HasProduction('jelly', surface, True)
    )

    # Power
    has_boiler_power = HasProduction('boiler', surface) & HasProduction('steam-engine', surface) & can_automate_chemical_fuel
    has_heating_power = HasProduction('heating-tower', surface) & HasProduction('heat-exchanger', surface) & HasProduction('steam-turbine', surface) & can_automate_chemical_fuel
    has_nuclear_power = HasProduction('nuclear-reactor', surface) & HasProduction('heat-exchanger', surface) & HasProduction('steam-turbine', surface) & HasProduction('uranium-fuel-cell', surface, True)
    has_fusion_power = HasProduction('fusion-reactor', surface) & HasProduction('fusion-generator', surface) & HasProduction('fusion-power-cell', surface, True)

    has_non_solar_power = has_boiler_power | has_heating_power | has_nuclear_power | has_fusion_power

    # Enemies
    has_gun_turret = HasProduction('gun-turret', surface) & HasProduction('firearm-magazine', surface, True)
    has_rocket_turret = HasProduction('rocket-turret', surface) & HasProduction('rocket', surface, True)
    has_railgun_turret = HasProduction('railgun-turret', surface) & HasProduction('railgun-ammo', surface, True)

    can_destroy_medium_asterorid = has_gun_turret & Has('physical-projectile-damage', 6)
    can_destroy_big_asterorid = has_rocket_turret & Has('stronger-explosives', 6) & can_destroy_medium_asterorid
    can_destroy_huge_asterorid = has_railgun_turret & can_destroy_big_asterorid

    # Thrusters
    has_truster_and_propellants = (
        HasProduction('thruster', surface)
            & HasProduction('thruster-fuel', surface, True) & HasProduction('thruster-oxidizer', surface, True)
            # Pipes are needed to transport propellants
            & HasProduction('pipe', surface) & HasProduction('pipe-to-ground', surface)
            # Pumps and storage tanks allow thruster throttling
            & HasProduction('pump', surface) & HasProduction('storage-tank', surface)
    )

    events = base_get_events(surface)

    events['Reach fulgora'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    events['Reach gleba'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    events['Reach vulcanus'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    events['Reach aquilo'] &= can_destroy_big_asterorid & has_truster_and_propellants
    events['Reach solar-system-edge'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power
    events['Reach shattered-planet'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power

    return events
