from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle

from ..data import science_packs

class MaxSciencePack(Choice):
    """Maximum level of science pack required to complete the game.
    This also affects the relative cost of silo and satellite recipes if they are randomized.
    That is the only thing in which the Utility Science Pack and Space Science Pack settings differ."""
    display_name = "Maximum Required Science Pack"
    default = len(science_packs) - 1

    def get_allowed_packs(self):
        return {option.replace("_", "-") for option, value in self.options.items() if value <= self.value}

MaxSciencePack.options = {name: index for index, name in enumerate(science_packs)}
MaxSciencePack.name_lookup = {option_id: name for name, option_id in MaxSciencePack.options.items()}


class MinTechCost(Range):
    """The cheapest a Technology can be in Science Packs."""
    display_name = "Minimum Science Pack Cost"
    range_start = 1
    range_end = 10000
    default = 5


class MaxTechCost(Range):
    """The most expensive a Technology can be in Science Packs."""
    display_name = "Maximum Science Pack Cost"
    range_start = 1
    range_end = 10000
    default = 500


class TechCostDistribution(Choice):
    """Random distribution of costs of the Science Packs.
    Even: any number between min and max is equally likely.
    Low: low costs, near the minimum, are more likely.
    Middle: medium costs, near the average, are more likely.
    High: high costs, near the maximum, are more likely."""
    display_name = "Tech Cost Distribution"
    option_even = 0
    option_low = 1
    option_middle = 2
    option_high = 3


class TechCostMix(Range):
    """Percent chance that a preceding Science Pack is also required.
    Chance is rolled per preceding pack."""
    display_name = "Science Pack Cost Mix"
    range_end = 100
    default = 70


class RampingTechCosts(Toggle):
    """Forces the amount of Science Packs required to ramp up with the highest involved Pack. Average is preserved.
    For example:
    off: Automation (red)/Logistics (green) sciences can range from 1 to 1000 Science Packs,
    on: Automation (red) ranges to ~500 packs and Logistics (green) from ~500 to 1000 Science Packs"""
    display_name = "Ramping Tech Costs"


@dataclass
class FactorioOptions(PerGameCommonOptions):
    max_science_pack: MaxSciencePack
    min_tech_cost: MinTechCost
    max_tech_cost: MaxTechCost
    tech_cost_distribution: TechCostDistribution
    tech_cost_mix: TechCostMix
    ramping_tech_costs: RampingTechCosts
