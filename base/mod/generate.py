import collections.abc
import importlib.resources
import json
import os
import zipfile

from jinja2 import Environment, FunctionLoader

from worlds.Files import APPlayerContainer

from ..config import dependencies


resources_lib = importlib.resources.files(__name__).joinpath('lib')
resources_template = importlib.resources.files(__name__).joinpath('template')


def _recursive_list_files(traversable) -> collections.abc.Iterator[str]:
    for file in traversable.iterdir():
        if file.is_dir():
            for name in _recursive_list_files(file):
                yield file.name + '/' + name
        else:
            yield file.name

template_files = list(_recursive_list_files(resources_template))


base_info = {
    "title": "Archipelago",
    "author": "Berserker",
    "homepage": "https://archipelago.gg",
    "description": "Integration client for the Archipelago Randomizer",
    "factorio_version": "2.0",
    "dependencies": dependencies,
}


class FactorioModFile(APPlayerContainer):
    game = "Factorio"
    compression_method = zipfile.ZIP_DEFLATED  # Factorio can't load LZMA archives
    writing_tasks: list
    patch_file_ending = ".zip"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.writing_tasks = []

    def write_contents(self, opened_zipfile: zipfile.ZipFile):
        # directory containing Factorio mod has to come first, or Factorio won't recognize this file as a mod.
        mod_dir = self.path[:-4]  # cut off .zip
        for root, dirs, files in os.walk(mod_dir):
            for file in files:
                filename = os.path.join(root, file)
                opened_zipfile.write(filename,
                                     os.path.relpath(filename,
                                                     os.path.join(mod_dir, '..')))
        for task in self.writing_tasks:
            target, content = task()
            opened_zipfile.writestr(target, content)
        # now we can add extras.
        super(FactorioModFile, self).write_contents(opened_zipfile)


def load_template(name: str):
    for path in [resources_lib, resources_template]:
        file = path.joinpath(name)
        if file.is_file():
            return file.read_text(), name, lambda: False

    return None


template_env = Environment(loader=FunctionLoader(load_template))


def generate_mod(mod_name: str, mod_version: str, mod_data: dict, world, output_directory: str) -> None:
    versioned_mod_name = f'{mod_name}_{mod_version}'

    zf_path = os.path.join(output_directory, f'{versioned_mod_name}.zip')
    mod = FactorioModFile(zf_path, player=world.player, player_name=world.player_name)

    for file in template_files:
        if file.endswith('.j2'):
            mod.writing_tasks.append(lambda path=file: (versioned_mod_name + '/' + path.removesuffix('.j2'), template_env.get_template(path).render(**mod_data)))
        else:
            mod.writing_tasks.append(lambda path=file: (versioned_mod_name + '/' + path, resources_template.joinpath(path).read_bytes()))

    mod.writing_tasks.append(lambda: (versioned_mod_name + '/LICENSE', importlib.resources.files(__name__).parent.joinpath('LICENSE').read_bytes()))

    info = base_info.copy()
    info['name'] = mod_name
    info['version'] = mod_version
    mod.writing_tasks.append(lambda: (versioned_mod_name + "/info.json",
                                      json.dumps(info, indent=4)))

    mod.write()
