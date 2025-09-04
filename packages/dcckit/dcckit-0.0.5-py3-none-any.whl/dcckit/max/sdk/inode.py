import dcckit.max.sdk


def find_with_handle(handle):
    """
    Finds and returns an INode by its handle

    Note: This is an SDK based INode, not the MXSWrapper.

    Args:
        handle (int): The handle of the node
    Returns:
        INode: Node with the given handle, or None if not found
    """
    try:
        output = dcckit.max.sdk.get_core_interface().GetINodeByHandle(handle)
        return output

    except Exception:
        # Don't raise as the SDK could have weird issues we're not aware of!
        pass

    return None


def get_root():
    """
    Gets the root INode for the current scene

    Returns:
        INode: The root INode for the current scene
    """
    try:
        output = dcckit.max.sdk.get_core_interface().RootNode
        return output

    except Exception:
        pass

    return None


def get_children(inode, recursive=False):
    """
    Gets the child nodes for the input INode

    Args:
        inode (INode): The node to get the children for
    Kwargs:
        recursive (bool): Whether to get the children recursively
    """
    outputs = []
    for i in range(inode.NumberOfChildren):
        child = inode.GetChildNode(i)
        outputs.append(child)

        if recursive:
            outputs.extend(get_children(child, True))

    return outputs


def from_max_nodes(max_nodes: list) -> list:
    """
    Gets a list of SDK INode objects from input Maxscript Nodes
    This can be slightly faster than calling `get_inode_by_handle`
    when working with a lot of MXS nodes

    Args:
        max_nodes (List[Node]): The Maxscript Nodes to get the INodes for
    Returns:
        List[INode]: The output INodes - ordered in the same order as the input nodes
    """
    output = []
    handle_and_node = {}
    for i in get_children(get_root(), recursive=True):
        handle_and_node[i.Handle] = i
    for i in max_nodes:
        output.append(handle_and_node[i.inode.handle])
    return output
