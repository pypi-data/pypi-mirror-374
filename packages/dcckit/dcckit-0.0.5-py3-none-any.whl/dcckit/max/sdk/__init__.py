"""
Various SDK related wrapper functions, for accessing the 3ds Max SDK
via Python (using PythonNet)
"""
import clr
clr.AddReference("Autodesk.Max")

from Autodesk.Max import GlobalInterface  # noqa


def get_core_interface() -> "COREInterface":
    """
    Gets the CORE interface from the SDK/C#

    Returns:
        COREInterface: The COREInterface as retrieved from the c# libs
    """
    return get_global_interface().UtilGetCOREInterface


def get_global_interface() -> "GlobalInterface":
    """
    Gets the global interface from the SDK/C#

    Returns:
        GlobalInterface: The GlobalInterface as retrieved from the c# libs
    """
    return GlobalInterface.Instance


def get_active_view_exp() -> "ViewExp":
    """
    Gets the active viewport

    Returns:
        ViewExp: The active viewport
    """
    return get_core_interface().ActiveViewExp


def get_time() -> int:
    """
    Gets the current Max time

    Returns:
        int: Current Time
    """
    return get_core_interface().Time
