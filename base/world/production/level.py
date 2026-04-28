import enum

class ProductionLevel(enum.Enum):
    '''Possible production levels:

    Available: you have a few of this items but can't craft more 
    Craftable: you can craft this item but can't fully automate it (for example hand crafting)
    Automated: production of this item is fully automated
    '''

    AVAILABLE = enum.auto()
    CRAFTABLE = enum.auto()
    AUTOMATED = enum.auto()
