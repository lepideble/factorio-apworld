import collections.abc
import importlib.resources
import json


data = json.loads(importlib.resources.files(__name__).joinpath('data.json').read_text())
types = json.loads(importlib.resources.files(__name__).joinpath('types.json').read_text())


def get_prototypes(type: str) -> collections.abc.Iterable[dict]:
    if (type_name := types[type].get('type')):
        for value in data.get(type_name, {}).values():
             if not value.get('hidden', False) and not value.get('parameter', False):
                yield value
    for child_type in types[type].get('children', []):
        yield from get_prototypes(child_type)


def get_prototype(type: str, name: str) -> dict|None:
    if (type_name := types[type].get('type')):
        if (prototype := data.get(type_name, {}).get(name)):
            return prototype
    for child_type in types[type].get('children', []):
        if (prototype := get_prototype(child_type, name)):
            return prototype
    return None
