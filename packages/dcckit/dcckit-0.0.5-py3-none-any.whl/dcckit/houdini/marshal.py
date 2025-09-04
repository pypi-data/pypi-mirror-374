import numpy as np
import hou

import dcckit.math


def lerp_vector3(a, b, x):
    """
    Interpolates between two hou.Vector3 vectors

    Args:
        a (hou.Vector3): The start vector
        b (hou.Vector3): The end vector
        x (float): The interpolation alpha
    Returns:
        hou.Vector3: The interpolated vector
    """
    return hou.Vector3(
        dcckit.math.lerp(a.x(), b.x(), x),
        dcckit.math.lerp(a.y(), b.y(), x),
        dcckit.math.lerp(a.z(), b.z(), x)
    )


def remap_vector3(value, start1, stop1, start2, stop2):
    """
    Remaps a hou.Vector3 value from one range to another

    Args:
        value (hou.Vector3): The value to remap
        start1 (hou.Vector3): The start of the input range
        stop1 (hou.Vector3): The end of the input range
        start2 (hou.Vector3): The start of the output range
        stop2 (hou.Vector3): The end of the output range
    Returns:
        hou.Vector3: The remapped value
    """
    return hou.Vector3(
        np.interp(value.x(), [start1.x(), stop1.x()], [start2.x(), stop2.x()]),
        np.interp(value.y(), [start1.y(), stop1.y()], [start2.y(), stop2.y()]),
        np.interp(value.z(), [start1.z(), stop1.z()], [start2.z(), stop2.z()])
    )


def average_vector3(values: hou.Vector3) -> hou.Vector3:
    """
    Gets the average of a list of hou.Vector3 vectors

    Args:
        values (List[hou.Vector3]): The list of vectors
    Returns:
        hou.Vector3: The average vector
    """
    output = hou.Vector3(0.0, 0.0, 0.0)
    for i in values:
        output += i
    return output / len(values)
