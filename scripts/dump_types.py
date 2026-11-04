import json
import urllib.request

def dump_types():
    data = json.loads(urllib.request.urlopen('https://lua-api.factorio.com/2.1.24/prototype-api.json').read())

    types = {}
    for prototype in data['prototypes']:
        types[prototype['name']] = {}

        type = prototype.get('typename')
        if type:
            types[prototype['name']]['type'] = type

        parent = prototype.get('parent')
        if parent:
            types[prototype['name']]['parent'] = parent

        children = [child['name'] for child in data['prototypes'] if child.get('parent') == prototype['name']]
        if len(children) > 0:
            types[prototype['name']]['children'] = children

        defaults = {}
        for property in prototype['properties']:
            if 'default' in property and isinstance(property['default'], dict) and property['default']['complex_type'] == 'literal':
                defaults[property['name']] = property['default']['value']
        if len(defaults) > 0:
            types[prototype['name']]['defaults'] = defaults

    print(json.dumps(types, indent = 4))

if __name__ == '__main__':
    dump_types()
