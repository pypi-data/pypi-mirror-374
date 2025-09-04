import pymxs


def version_year() -> int:
    """
    Gets the current version of 3DS Max

    Returns:
        int: The current max version year (Ie, 2021, 2022)
    """
    return pymxs.runtime.maxVersion()[7]
