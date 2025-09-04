import dcckit.max.sdk
from pymxs import runtime as rt


def get_or_pick_selection():
    """
    Gets the current node selection if something is selected
    else prompts the user to pick nodes

    Returns:
        list(pymxs.runtime.Node): The node selection
    """
    output = []
    for i in rt.selection:
        output.append(i)

    if (not output):
        target = rt.pickObject()
        if (target):
            output = [target]

    return output


def pick_node_from_viewport_position(position, inode=False):
    """
    Picks a node from a viewport position

    Args:
        position (tuple(int, int)): The viewport position
    Kwargs:
        inode (bool): Whether to return an inode or not
    Returns:
        pymxs.runtime.Node: The picked node
    """
    instance = dcckit.max.sdk.get_global_interface()
    pos_point2 = instance.Point2.Create(position[0], position[1])
    i_point2 = instance.IPoint2NS.Create(int(pos_point2.X), int(pos_point2.Y))

    interface = instance.UtilGetCOREInterface
    view_exp = interface.ActiveViewExp
    view_exp.ClearHitList()
    view_handle = view_exp.HWnd
    node = interface.PickNode(view_handle, i_point2, filt=None)

    if (inode and node):
        return rt.getNodeByHandle(node.Handle)

    return node
