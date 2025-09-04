import functools
import glob
import os
import winreg

from dcckit.unreal import plugin


def get_installed_engine_versions():
    """
    Get a list of installed unreal engine versions and their paths

    E.g. {"4.2": "C:\\Program Files\\Epic Games\\UE_4.2"}

    Returns:
        dict: A dictionary of version: path
    """
    ue_versions = {}
    reg_path = r"SOFTWARE\EpicGames\Unreal Engine"

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
            num_subkeys, num_values, last_modified = winreg.QueryInfoKey(key)
            for i in range(num_subkeys):
                version = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, version) as subkey:
                    path, _ = winreg.QueryValueEx(subkey, 'InstalledDirectory')
                    ue_versions[version] = path
    except Exception:
        # Usually means a registry key doesn't exist or was set incorrectly!
        pass

    return ue_versions


def find_engine_root(engine_association):
    """
    Finds the root directory for an engine from the name as stored in the registry
    :param <str:guid_string> The guid to search for
    :return <str:dir> The path to the engine root directory - None if not found
    """
    all_installed_engines = get_installed_engine_versions()
    if engine_association in all_installed_engines:
        return all_installed_engines[engine_association]
    return None


class UEngine(object):
    def __init__(self, uengine_root: str):
        """
        Class used for interacting with an Unreal UEngine

        Args:
            uengine_root (str): The path to the UEngine root directory
        """
        self.__root = uengine_root

    @property
    def root(self) -> str:
        """
        Get the root path of the UEngine

        Returns:
            str: The root path of the UEngine
        """
        return self.__root

    @property
    @functools.lru_cache()
    def plugins(self) -> list:
        """
        Get a list of plugins in the engine

        Returns:
            list: A list of UPlugin objects
        """
        plugins = []
        for uplugin_path in glob.glob(os.path.join(self.root, "Plugins\\**\\*.uplugin"), recursive=True):
            plugins.append(plugin.UPlugin(uplugin_path))
        return plugins
