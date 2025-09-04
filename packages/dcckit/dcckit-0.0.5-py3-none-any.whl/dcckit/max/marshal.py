import pymxs


def python_to_maxscript_array(python_array):
    """
    Converts a python based array to a maxscript one

    Args:
        python_array (list): The python array to convert
    Returns:
        pymxs.array: The maxscript array
    """
    output = pymxs.runtime.array()
    for i in python_array:
        pymxs.runtime.append(output, i)
    return output
