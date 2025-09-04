import os


def get_max_install_directory(max_version: int) -> str:
    """
    Gets the install directory for a given version of 3ds Max.

    Args:
        max_version (int): The version of 3ds Max.
    Returns:
        str: The install directory for the given version of 3ds Max.
    """
    return f"C:\\Program Files\\Autodesk\\3ds Max {max_version}"


def get_max_exe_path(max_version: int = None, batch: bool = False) -> str:
    """
    Returns the path to the 3ds Max executable.

    Kwargs:
        max_version (int): The version of 3ds Max.
            - `None` will result in us using the most up-to-date version which is installed.
        batch (bool): Whether to return the path to the `3dsmaxbatch.exe`.
    Returns:
        str: The path to the 3ds Max executable.
    """
    if max_version is None:
        for i in range(2030, 2022, -1):
            path = get_max_exe_path(max_version=i, batch=batch)
            if os.path.isfile(path):
                return path
        return ""

    exe_name = "3dsmax.exe" if not batch else "3dsmaxbatch.exe"
    return os.path.join(get_max_install_directory(max_version), exe_name)
