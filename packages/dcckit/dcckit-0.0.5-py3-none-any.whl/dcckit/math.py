import numpy as np


def lerp(a, b, x):
    """
    Performs linear interpolation between two values.

    Args:
        a (float): The start value.
        b (float): The end value.
        x (float): The interpolation factor (0.0 to 1.0).

    Returns:
        float: The interpolated value.
    """
    return a + (b - a) * x
