import os
import pymxs
import dcckit.host


@dcckit.host.hostmethod
def path() -> str:
    """
    Gets the path to the scene which is currently opened in a given host.

    Returns:
        str: The path to the current scene - or ""
    """
    raise NotImplementedError


@path.override("max")
def path():
    from pymxs import runtime as rt
    fp = rt.maxFilePath
    fp = fp.replace("/", "\\")
    if not fp.endswith("\\"):
        fp += "\\"
    
    return fp + rt.maxFileName


# -----------------------------------------------------------------------

def name(remove_extension: bool = False) -> str:
    """
    Gets the name of the currently opened scene in a given host.

    Kwargs:
        remove_extension (bool): If True, the file extension will be removed.
    Returns:
        str: The name of the current scene - or ""
    """
    fp = path()
    if not fp:
        return ""
    
    output = os.path.basename(fp)

    if remove_extension:
        output = os.path.splitext(output)[0]

    return output
