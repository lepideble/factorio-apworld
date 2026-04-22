from BaseClasses import Item, ItemClassification

from ...config import game_name
from .ids import item_ids


class FactorioItem(Item):
    game = game_name

    def __init__(self, name: str, classification: ItemClassification, player: int):
        super().__init__(name, classification, item_ids[name], player)


class FactorioQualityItem(FactorioItem):
    def __init__(self, quality_name: str, classification: ItemClassification, player: int):
        super().__init__(f'quality: {quality_name}', classification, player)


class FactorioRecipeItem(FactorioItem):
    def __init__(self, recipe_name: str, classification: ItemClassification, player: int):
        super().__init__(f'recipe: {recipe_name}', classification, player)


class FactorioSpaceLocationItem(FactorioItem):
    def __init__(self, space_location_name: str, classification: ItemClassification, player: int):
        super().__init__(f'space location: {space_location_name}', classification, player)


class FactorioTechnologyItem(FactorioItem):
    def __init__(self, technology_name: str, classification: ItemClassification, player: int):
        super().__init__(technology_name, classification, player)
