import json
import os
import pkgutil
import zipfile

from jinja2 import Environment, FunctionLoader

from worlds.Files import APPlayerContainer
from Utils import get_text_after

from ..config import dependencies


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
    return pkgutil.get_data(__name__, f'mod_template/{name}').decode(), name, lambda: False


template_env = Environment(loader=FunctionLoader(load_template))


def generate_mod(mod_name: str, mod_version: str, mod_data: dict, world, output_directory: str) -> None:
    versioned_mod_name = f'{mod_name}_{mod_version}'

    zf_path = os.path.join(output_directory, f'{versioned_mod_name}.zip')
    mod = FactorioModFile(zf_path, player=world.player, player_name=world.player_name)

    if world.zip_path:
        with zipfile.ZipFile(world.zip_path) as zf:
            for file in zf.infolist():
                if not file.is_dir() and "/mod/mod/" in file.filename:
                    path_part = get_text_after(file.filename, "/mod/mod/")
                    mod.writing_tasks.append(lambda arcpath=versioned_mod_name+"/"+path_part, content=zf.read(file):
                                             (arcpath, content))
    else:
        basepath = os.path.join(os.path.dirname(__file__), "mod")
        for dirpath, dirnames, filenames in os.walk(basepath):
            base_arc_path = (versioned_mod_name+"/"+os.path.relpath(dirpath, basepath)).rstrip("/.\\")
            for filename in filenames:
                mod.writing_tasks.append(lambda arcpath=base_arc_path+"/"+filename,
                                                file_path=os.path.join(dirpath, filename):
                                         (arcpath, open(file_path, "rb").read()))

    mod.writing_tasks.append(lambda: (versioned_mod_name + "/data.lua",
                                      template_env.get_template("data.lua").render(**mod_data)))
    mod.writing_tasks.append(lambda: (versioned_mod_name + "/data-final-fixes.lua",
                                      template_env.get_template("data-final-fixes.lua").render(**mod_data)))
    mod.writing_tasks.append(lambda: (versioned_mod_name + "/control.lua",
                                      template_env.get_template("control.lua").render(**mod_data)))
    mod.writing_tasks.append(lambda: (versioned_mod_name + "/settings.lua",
                                      template_env.get_template("settings.lua").render(**mod_data)))
    mod.writing_tasks.append(lambda: (versioned_mod_name + "/locale/en/locale.cfg",
                                      template_env.get_template(r"locale/en/locale.cfg").render(**mod_data)))

    info = base_info.copy()
    info['name'] = mod_name
    info['version'] = mod_version
    mod.writing_tasks.append(lambda: (versioned_mod_name + "/info.json",
                                      json.dumps(info, indent=4)))

    mod.write()
