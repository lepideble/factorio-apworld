import dataclasses
import pprint

import data.classes
import data.raw


def is_default(value, field):
    if value == field.default:
        return True
    if isinstance(value, list) and len(value) == 0 and field.default_factory == list:
        return True
    if isinstance(value, set) and len(value) == 0 and field.default_factory == set:
        return True
    return False


def format_value(value):
    if dataclasses.is_dataclass(value):
        args = []
        for field in reversed(dataclasses.fields(value)):
            field_value = getattr(value, field.name)
            if len(args) == 0 and is_default(field_value, field):
                continue
            args.insert(0, field_value)
        return f'{value.__class__.__name__}({', '.join(map(format_value, args))})'

    if isinstance(value, list):
        return f'[{', '.join(map(format_value, value))}]'

    if isinstance(value, set):
        if len(value) == 0:
            return 'set()'
        else:
            return '{' + ', '.join(map(format_value, sorted(value))) + '}'

    return pprint.PrettyPrinter(width=1000000).pformat(value)


def print_data(name):
    value = getattr(data.raw, name)

    print('')
    if isinstance(value, data.classes.Table):
        print(f'{name} = Table()')
        for item in value:
            print(f'{name}.add({format_value(item)})')
    else:
        print(f'{name} = {format_value(value)}')


print('from .classes import GatherableResource, Machine, MinableResource, PumpableResource, Recipe, SpaceLocation, Surface, SurfaceCondition, Table, Technology')
print_data('surfaces')
print_data('surfaces_accessible_at_start')
print_data('space_locations')
print_data('machines')
print_data('machines_for_manual_craft')
print_data('recipes')
print_data('recipes_unlocked_at_start')
print_data('science_packs')
print_data('technologies')
print_data('items')
