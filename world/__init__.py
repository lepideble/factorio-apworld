from worlds.LauncherComponents import Component, components, Type, launch as launch_component

from .world import FactorioWorld
from .config import game_name


def launch_client(*args: str):
    from .client import launch
    launch_component(launch, name=f'{game_name} Client', args=args)


components.append(Component(f'{game_name} Client', func=launch_client, component_type=Type.CLIENT))
