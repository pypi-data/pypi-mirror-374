import Autodesk.Max
from pymxs import runtime as rt

import dcckit.max.sdk.inode as inode


def get_used_material_ids(*args) -> list:
    """
    Gets all used material IDs for the input nodes
    Note: Only geometry based nodes are processed!

    Args:
        args ([MXSNode]): The MXSNodes to check - can be a single input
            or multiple inputs (flattened)
    Returns:
        [int]: All used material IDs (sorted)
    """
    output = set()

    for i in args:
        if rt.superClassOf(i) == rt.geometryClass:
            try:
                sdk_node = inode.find_with_handle(i.inode.handle)
                world_state = sdk_node.EvalWorldState(0, True)
                obj = world_state.Obj

                if isinstance(obj, Autodesk.Max.Wrappers.PolyObject):
                    mesh = obj.Mesh
                    for i in range(mesh.FNum):
                        mnface = mesh.F(i)
                        # SDK Material IDs are Zero based. MaxScript/User is 1 based
                        output.add(mnface.get_Material__MNFace() + 1)
                elif isinstance(obj, Autodesk.Max.Wrappers.TriObject):
                    mesh = obj.Mesh_
                    for i in range(mesh.NumFaces):
                        output.add(mesh.GetFaceMtlIndex(i) + 1)

            except Exception:
                # For non geometry based nodes
                pass

    return sorted(output)
