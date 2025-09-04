"""
Module containing various 3DS Max Plugin related logic
"""
import dcckit.max.sdk
import typing


def dll_dir():
    """
    Gets the DllDir instance

    Returns:
        DllDir: The DllDir interface
    """
    return dcckit.max.sdk.get_global_interface().DllDir.Instance


def load_dll(file_path: str, force_load_deferrable: bool = True):
    """
    Loads a Dll from its file path

    Args:
        file_path (str): The path to the Dll to load
    Kwargs:
        force_load_deferrable (bool): Should deferrable plugins be force loaded?
    Returns:
        Plugin: The Plugin if loaded - else None
    """
    output = None

    num_loaded_prev = dll_dir().Count
    success = dll_dir().LoadADll(file_path, force_load_deferrable)
    num_loaded_current = dll_dir().Count

    if success and num_loaded_current > num_loaded_prev:
        plugin = dll_dir().GetDllDescription(num_loaded_current - 1)

        if plugin:
            output = plugin

            # Make sure we load all clases for the plugin
            for i in range(plugin.NumberOfClasses):
                class_desc = plugin[i]
                if class_desc:
                    dll_dir().ClassDir.AddClass(class_desc, num_loaded_current, i, True)

    if not output:
        pass

    return output


def plugin_types() -> typing.Tuple[str]:
    """
    Note: Where can we find the order these should be loaded in?

    There might be more info somewhere here:
    https://help.autodesk.com/view/3DSMAX/2016/ENU/?guid=__files_GUID_7F6A1A08_E8C7_42C9_A773_3FF1920ABCF0_htm\n

    Returns:
        typing.Tuple[str]: All known plugin dll extension types (Ie, "dlu", "dlm")
    """
    return (
        "dlc",
        "dle",
        "dlf",
        "dlh",
        "dli",
        "dlm",
        "dln",
        "dlo",
        "dlr",
        "dls",
        "dlt",
        "dlu",
        "dlv",
        "dlx",
        "flt",
        "gup"
    )
