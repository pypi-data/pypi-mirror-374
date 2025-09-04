from pymxs import runtime as rt


def is_scaled(max_node: rt.Node) -> bool:
    """
    Checks if a node has had its scale property overriden
    
    I.e. is not identity / [1.0, 1.0, 1.0]

    Args:
        max_node (Node): The Max node to check
    Returns:
        bool: True if the node has been scaled - else False
    """
    output = False
    node_scale = max_node.scale
    checks = (node_scale.x, node_scale.y, node_scale.z)
    for i in checks:
        if not rt.close_enough(i, 1.0, 10):
            # Note: The `close_enough` maxscript method has bad documentation
            #       not entirely sure what the tolerance range is measured in
            #       the documentation just says "A god value of <int> in most cases is 10"
            #       Keeping this call for legacy reasons
            output = True
            break
    return output


def get_descendants(target_node: rt.Node, current_objects=None) -> list:
    """
    Gets all descendants of a given node

    Args:
        target_node (Node): The target node to check
        current_objects (List[Node]): The object array to append to
    Returns:
        List[Node]: All descendants
    """
    if current_objects is None:
        current_objects = []

    for child in target_node.children:
        if child not in current_objects:
            current_objects.append(child)
        get_descendants(child, current_objects)

    return current_objects


def get_all_children(node):
    """
    Gets all children of a node recursively

    Args:
        node (rt.Node): The node to get the children of
    Returns:
        list: All children of the node
    """
    output = []
    for child in node.children:
        output.append(child)
        output += get_all_children(child)
    return output


def delete_hierarchy(node):
    """
    Deletes a node hierarchy

    Args:
        node (rt.Node): The node to delete
    """
    nodes = get_all_children(node) + [node]
    rt.delete(nodes)


def find_node_for_object(base_object):
    """
    Given an MXS Object, this will attempt to find the corresponding Node

    This is useful when you've been working with a reference to an object
    which has an associated node, but aren't given access to the actual node.

    E.g. `rt.getClassInstances` returns objects, even when the object is a node like type.

    Args:
        base_object (rt.MAXWrapper): The object to get the node from
    Returns:
        rt.Node: The node object if found, otherwise None
    """
    for obj in rt.objects:
        if obj.baseObject == base_object:
            return obj
    return None


def is_instance(max_node: rt.Node, max_type: rt.MAXClass) -> bool:
    """
    Checks if the input node is an instance of a core maxscript type
    Has additional checks for plugin types
    as there is no direct way to check if a class is an instance of another

    Args:
        max_node (Node): The max node to check
        max_type (MAXClass): The max class to check
    Returns:
        bool: True if it is an instance - else False
    """
    if max_node:
        if rt.classOf(max_node) == max_type:
            return True

        try:
            # check for a delegate property which inherits the class
            # the delegate is an interface to the base class instance
            if rt.classOf(max_node.delegate) == max_type:
                return True
        except Exception:
            pass

    return False