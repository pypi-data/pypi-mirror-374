import Autodesk.Max
import numpy as np
from dcckit.max.sdk import inode
from pymxs import runtime as rt


def get_verts(node):
    """
    Gets the vertices for the input object as a numpy array

    Args:
        node (rt.Node): The node to get the vertices from
    Returns:
        numpy.ndarray: The vertices for the input object
    """
    try:
        sdk_node = inode.find_with_handle(node.inode.handle)
        world_state = sdk_node.EvalWorldState(0, False)
        obj = world_state.Obj.__implementation__
        output = None

        if isinstance(obj, Autodesk.Max.Wrappers.PolyObject):
            mesh = obj.Mesh

            num_verts = mesh.VNum
            output = np.zeros((num_verts, 3), dtype=np.float32)

            for i in range(mesh.VNum):
                pos = mesh.V(i).P
                x, y, z = pos.X, pos.Y, pos.Z
                output[i] = np.array([x, y, z], dtype=np.float32)

        elif isinstance(obj, Autodesk.Max.Wrappers.TriObject):
            mesh = obj.Mesh_

            num_verts = mesh.NumVerts
            output = np.zeros((num_verts, 3), dtype=np.float32)

            def get_vert(i):
                pos = mesh.GetVert(i)
                x, y, z = pos.X, pos.Y, pos.Z
                return np.array([x, y, z], dtype=np.float32)

            num_verts = mesh.NumVerts
            output = np.zeros((num_verts, 3), dtype=np.float32)

            for i in range(mesh.NumVerts):
                pos = mesh.GetVert(i)
                x, y, z = pos.X, pos.Y, pos.Z
                output[i] = np.array([x, y, z], dtype=np.float32)

        return output

    except Exception as e:
        raise e
        # Not a geometry type
        # Note: It's quicker here to just try and catch the exception
        # than to run any validation checks
        return None


def get_tri_count(*args):
    """
    Gets the number of tris for the input objects

    Note: The number of internal tris (not polys)

    Args:
        *args: The nodes to get the tri count from
    """
    output = 0

    sdk_nodes = [inode.find_with_handle(node.inode.handle) for node in args]

    for sdk_node in sdk_nodes:
        try:
            world_state = sdk_node.EvalWorldState(0, False)
            obj = world_state.Obj.__implementation__

            if isinstance(obj, Autodesk.Max.Wrappers.PolyObject):
                mesh = obj.Mesh
                output += mesh.TriNum

            elif isinstance(obj, Autodesk.Max.Wrappers.TriObject):
                mesh = obj.Mesh_
                output += mesh.NumFaces
        except Exception:
            pass

    return output


def get_vertex_positions(max_node: rt.EditablePoly) -> np.ndarray:
    """
    Creates a vertex buffer of the positions of a geometry object

    Args:
        max_node (MXSNode): The node to get the vertex positions from
    Returns:
        numpy.array: The vertex positions as a numpy array
            E.g. np.array([[x1, y1, z1], [x2, y2, z2], ...])
    """
    if rt.classOf(max_node) != rt.editable_poly:
        raise AttributeError(f"Expected a geometry type, got {max_node} of type {rt.classOf(max_node)}")

    num_verts = rt.polyOp.getNumVerts(max_node)
    mxs_verts = rt.polyOp.getVerts(max_node, [i + 1 for i in range(num_verts)])

    output = np.zeros((num_verts, 3), dtype=np.float32)
    for index, vert in enumerate(mxs_verts):
        vert = vert
        output[index][0] = vert[0]
        output[index][1] = vert[1]
        output[index][2] = vert[2]
    return output


def get_triangle_indices(max_node):
    """
    Gets the triangle indices for a max poly object (aka index buffer)

    Args:
        max_node (MXSNode): The node to get the triangle indices from
    Returns:
        numpy.array: The triangle indices as a numpy array
            E.g. np.array([[v1, v2, v3], [v4, v5, v6], ...])    
    """
    if rt.classOf(max_node) != rt.editable_poly:
        raise AttributeError(
            f"Expected a poly object, got {max_node} of type {rt.classOf(max_node)}"
        )

    mxs_face_tris = rt.getAllFaceTris(max_node)
    num_tris = max_node.mesh.numFaces

    index = 0
    output = np.zeros((num_tris, 3), dtype=np.uint32)
    for face_tris in mxs_face_tris:
        for tri in face_tris:
            output[index][0] = tri[0]
            output[index][1] = tri[1]
            output[index][2] = tri[2]
            index += 1
    output -= 1  # MAXScript is 1-indexed, convert to 0-indexed
    return output
