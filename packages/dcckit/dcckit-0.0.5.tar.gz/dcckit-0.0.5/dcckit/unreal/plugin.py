import os


class UPlugin(object):
    def __init__(self, uplugin_path: str):
        """
        Class used for interfacing with an Unreal UPlugin file

        Args:
            uplugin_path (str): The path to the UPlugin file
        """
        self.__path = uplugin_path

    @property
    def path(self) -> str:
        """
        Get the path to the UPlugin file

        Returns:
            str: The path to the UPlugin file
        """
        return self.__path

    @property
    def root(self):
        """
        Get the root path of the plugin

        Returns:
            str: The root path of the plugin
        """
        return os.path.dirname(self.path)

    @property
    def name(self):
        """
        Get the name of the plugin

        Returns:
            str: The name of the plugin
        """
        return os.path.splitext(os.path.basename(self.path))[0]
