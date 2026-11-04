import collections.abc
import importlib.resources
import json


data = json.loads(importlib.resources.files(__name__).joinpath('data.json').read_text())
types = json.loads(importlib.resources.files(__name__).joinpath('types.json').read_text())


class Prototype(dict):
    _defaults: dict

    def __init__(self, data):
        super().__init__(data)

        type_name = next(type_name for type_name, type_data in types.items() if 'type' in type_data and type_data['type'] == self['type'])
        ancestry = [type_name]
        while (type_name := types[type_name].get('parent')):
            ancestry.append(type_name)

        defaults = {}
        for ancestor in reversed(ancestry):
            defaults.update(types[ancestor].get('defaults', {}))

        self._defaults = defaults

    def __getattr__(self, name):
        return self.get(name, self._defaults[name])


def get_prototypes(type: str) -> collections.abc.Iterable[Prototype]:
    if (type_name := types[type].get('type')):
        for value in data.get(type_name, {}).values():
             if not value.get('hidden', False) and not value.get('parameter', False):
                yield Prototype(value)
    for child_type in types[type].get('children', []):
        yield from get_prototypes(child_type)


def get_prototype(type: str, name: str) -> Prototype|None:
    if (type_name := types[type].get('type')):
        if (prototype := data.get(type_name, {}).get(name)):
            return Prototype(prototype)
    for child_type in types[type].get('children', []):
        if (prototype := get_prototype(child_type, name)):
            return prototype
    return None
