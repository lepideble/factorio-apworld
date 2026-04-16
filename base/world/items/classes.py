from BaseClasses import Item, ItemClassification

from ...config import game_name
from .ids import item_ids


class FactorioItem(Item):
    game = game_name

    def __init__(self, name: str, classification: ItemClassification, player: int):
        super().__init__(name, classification, item_ids[name], player)
