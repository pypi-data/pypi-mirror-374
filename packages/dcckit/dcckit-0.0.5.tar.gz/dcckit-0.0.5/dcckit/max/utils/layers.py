import pymxs
from pymxs import runtime as rt


def find(name: str) -> "rt.Layer":
    """
    Gets a layer with the given name

    Args:
        name (str): The name of the layer
    Returns:
        Layer: The layer object
    """
    return rt.layerManager.getLayerFromName(name)


def create(name: str) -> "rt.Layer":
    """
    Creates a new layer with the given name

    Args:
        name (str): The name of the layer
    Returns:
        Layer: The layer object
    """
    return rt.layerManager.newLayerFromName(name)


def find_or_create(name: str) -> "rt.Layer":
    """
    Gets a layer with the given name or creates it if it does not exist

    Args:
        name (str): The name of the layer
    Returns:
        Layer: The layer object
    """
    if existing := find(name):
        return existing
    return create(name)


def remove_empty_layers() -> int:
    """
    Removes all empty layers from the scene

    Returns:
        int: The number of layers removed
    """
    output = 0
    layers = [rt.layerManager.getLayer(i) for i in range(rt.layerManager.count)]
    for layer in reversed(layers):
        if layer.getNumNodes() == 0:
            output += 1
            rt.layerManager.deleteLayerByName(layer.name)
    return output


def get_nodes(layer: "rt.Layer", recursive=False) -> list:
    """
    Gets all the nodes in the given layer

    Args:
        layer (Layer): The layer object
    Kwargs:
        recursive (bool): Whether to get the nodes recursively
    Returns:
        list: The list of nodes
    """
    _nodes = rt.array()
    # The `layer.nodes` function takes an input array and fills it with the nodes
    # by default in mxs
    #
    # but the Python wrapper tries to be smart and adds this to the return value
    result = layer.nodes(pymxs.byref(_nodes))
    nodes = result[1]

    if recursive:
        for node in list(nodes):
            for child in node.children:
                nodes.append(child)

    return nodes


def clear(layer: "rt.Layer", delete_layer=False):
    """
    Clears all nodes from the given layer

    Args:
        layer (Layer): The layer object
    Kwargs:
        delete_layer (bool): Whether to delete the layer after clearing it
    """
    to_delete = []
    for node in get_nodes(layer):
        to_delete.append(node)
    rt.delete(to_delete)

    if delete_layer:
        rt.layerManager.deleteLayerByName(layer.name)
        