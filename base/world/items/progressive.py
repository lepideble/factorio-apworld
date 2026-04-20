from BaseClasses import ItemClassification

from .classes import FactorioItem


def make_progressive(items: list[FactorioItem], progressive_chains: dict[str, list[str]]) -> list[FactorioItem]:
    # Build reverse progressive lookup map
    progressive_map: dict[str, str] = {}
    for progressive_name, progressive_chain in progressive_chains.items():
        for item_name in progressive_chain:
            progressive_map[item_name] = progressive_name

    items_with_progressive = []

    items_by_progressive_name = { progressive_name: [] for progressive_name in progressive_chains.keys() }
    for item in items:
        if item.name in progressive_map:
            items_by_progressive_name[progressive_map[item.name]].append(item)
        else:
            items_with_progressive.append(item)

    for progressive_name, progressive_chain in progressive_chains.items():
        assert len(items_by_progressive_name[progressive_name]) == len(progressive_chain)

        items_by_progressive_name[progressive_name].sort(key=lambda item: progressive_chain.index(item.name))

        print(items_by_progressive_name[progressive_name])

        is_advancement = False
        is_useful = False

        progressive_items = []
        for item in reversed(items_by_progressive_name[progressive_name]):
            if item.advancement:
                is_advancement = True
            if item.useful:
                is_useful = True

            if is_advancement:
                classification = ItemClassification.progression
            elif is_useful:
                classification = ItemClassification.useful
            else:
                classification = ItemClassification.filler

            progressive_items.append(FactorioItem(progressive_name, classification, item.player))

        items_with_progressive.extend(reversed(progressive_items))

    return items_with_progressive
