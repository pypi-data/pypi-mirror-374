"""
Various functions related to the 3DS Max interface.
"""
import dcckit.max.sdk
import ctypes
import Autodesk.Max
import pymxs


def disable_macro_recorder():
    """
    Disables the 3DS Max macro recorder
    """
    core_interface = dcckit.max.sdk.get_core_interface()
    core_interface.MacroRecorder.Disable()


def enable_macro_recorder():
    """
    Enables the 3DS Max macro recorder
    """
    core_interface = dcckit.max.sdk.get_core_interface()
    core_interface.MacroRecorder.Enable()

# -----------------------------------------------------------------------


def get_maxscript_listener_hwnd():
    """
    Gets the window handle for the maxscript listener

    Returns:
        int: The window handle for the maxscript listener
    """
    return int(str(Autodesk.Max.GlobalInterface.Instance.TheListenerWindow))


def is_listener_visible() -> bool:
    """
    Checks if the listener is visible.

    Returns:
        bool: True if the listener is visible, otherwise False
    """
    # TODO~ This does not work correctly
    user_32 = ctypes.windll.user32
    return user_32.IsWindowVisible(str(get_maxscript_listener_hwnd())) == 0


def show_listener():
    """
    Opens the maxscript listener
    """
    Autodesk.Max.GlobalInterface.Instance.ShowListener()


def hide_listener():
    """
    Closes the maxscript listener
    """
    pymxs.runtime.uiaccessor.closedialog(get_maxscript_listener_hwnd())


def toggle_listener_visibility():
    """
    Toggles the visibiilty of the listener
    """
    if is_listener_visible():
        hide_listener()
    else:
        show_listener()


def set_listener_visibility(visible: bool):
    """
    Sets the visibility of the listener.

    Args:
        visible (bool): The visibility state to set.
    """
    if visible == is_listener_visible():
        return
    toggle_listener_visibility()
