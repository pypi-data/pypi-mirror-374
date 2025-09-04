import glob
import json
import os

from dcckit.unreal import plugin, engine


class UProject(object):
    def __init__(self, uproject_path: str):
        """
        Class used for interfacing with an Unreal UProject file

        Args:
            uproject_path (str): The path to the UProject file
        """
        self.__path = uproject_path

    @property
    def path(self) -> str:
        """
        Get the path to the UProject file

        Returns:
            str: The path to the UProject file
        """
        return self.__path

    @property
    def name(self) -> str:
        """
        Get the name of the project

        Returns:
            str: The name of the project
        """
        return os.path.splitext(os.path.basename(self.path))[0]

    @property
    def root(self) -> str:
        """
        Get the root path of the project

        Returns:
            str: The root path of the project
        """
        return os.path.dirname(self.path)

    # -----------------------------------------------------------------------

    @property
    def plugins(self) -> list:
        """
        Get a list of plugins in the project

        Returns:
            list: A list of UPlugin objects
        """
        plugins = []
        for uplugin_path in glob.glob(os.path.join(self.root, "Plugins\\**\\*.uplugin"), recursive=True):
            plugins.append(plugin.UPlugin(uplugin_path))
        return plugins

    # -----------------------------------------------------------------------

    def get_engine_association_name(self):
        """
        Gets the name of the engine associated with this project (if set)

        Returns:
            str: The name of the engine associated with this project - or "" if not set
        """
        with open(self.path, "r") as f:
            data = json.load(f)
        if "EngineAssociation" in data:
            return data["EngineAssociation"]
        return ""

    def get_engine(self) -> engine.UEngine:
        """
        Get the engine associated with this project (if set)

        Returns:
            UEngine: The engine associated with this project - or None if not set
        """
        installed_engine_versions = engine.get_installed_engine_versions()
        engine_association_name = self.get_engine_association_name()

        if (engine_association_name not in installed_engine_versions):
            return None

        engine_root = installed_engine_versions[engine_association_name]
        return engine.UEngine(engine_root)

    # TODO! map and unmap paths to project
