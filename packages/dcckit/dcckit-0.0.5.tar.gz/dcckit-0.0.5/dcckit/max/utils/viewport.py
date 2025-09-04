import dcckit.max.sdk
import pymxs
import typing
from pymxs import runtime as rt


def hit_test_face(inode, position):
    """
    Takes an input node and viewport position and returns the face ID that is hit

    Args:
        inode (rt.INode): The inode to work on
        position (tuple(int, int)): Screen position to test at
    Returns:
        int: ID of the face hit, None if nothing was hit
    """
    instance = dcckit.max.sdk.get_global_interface()
    interface = dcckit.max.sdk.get_core_interface()

    pos = instance.IPoint2NS.Create(int(position[0]), int(position[1]))

    # graphics window
    view_exp = dcckit.max.sdk.get_active_view_exp()
    graphics_window = view_exp.Gw

    hit_region = instance.HitRegion.Create()
    instance.MakeHitRegion(hit_region, 0x0001, 1, 4, pos)  # 0x0001 = POINT_RGN
    graphics_window.SetHitRegion(hit_region)

    tx = inode.GetObjectTM(interface.Time, valid=None)
    graphics_window.Transform = tx
    graphics_window.ClearHitCode()

    # see https://help.autodesk.com/view/MAXDEV/2022/ENU/?guid=Max_Developer_Help_cpp_ref_class_hit_list_wrapper_html
    object_wrapper = instance.ObjectWrapper.Create()
    object_wrapper.Init(
        0,
        inode.EvalWorldState(dcckit.max.sdk.get_time(), evalHidden=True),
        copy=False,
        enable=0x7,  # default
        nativeType=2  # polyObject
    )

    # see https://help.autodesk.com/view/3DSMAX/2016/ENU/?guid=__cpp_ref_class_hit_list_wrapper_html
    hit_list_wrapper = instance.HitListWrapper.Create()
    hit_list_wrapper.Init(2)
    result = object_wrapper.SubObjectHitTest(
        2,  # SEL_FACE
        graphics_window,
        graphics_window.Material,
        hit_region,
        1 << 25,  # SUBHIT_MNFACES
        hit_list_wrapper,
        numMat=1,
        mat=None
    )

    if (result):
        # get the closest one
        hit_list_wrapper.GoToFirst
        closest = hit_list_wrapper.Index
        min_dist = hit_list_wrapper.Dist

        while (1):
            if (min_dist > hit_list_wrapper.Dist):
                min_dist = hit_list_wrapper.Dist
                closest = hit_list_wrapper.Index
            if (not hit_list_wrapper.GoToNext):
                break
        return closest + 1
    return None


def toggle_uv_view_mode(mode: typing.Union[int, None]):
    """
    Toggles the UV view mode of the viewport

    Args:
        mode (int or None): The mode to set the viewport to.
            Note: This should be an index (of the UV channel), or None to disable.

    Valid modes are:
        None: Disable UV view mode
        0: Vertex Colour
        -1: Vertex Illumination
        -2: Vertex Alpha
        3..N: Map channel X
    """

    with pymxs.undo(False):
        rt.suspendEditing()
        rt.disableSceneRedraw()

        selection = [x for x in rt.selection]
        geometry = [x for x in rt.geometry]

        if len(geometry):
            for geo in geometry:
                if not geo:
                    continue

                if mode is not None:
                    geo.displayByLayer = False
                    geo.vertexColorType = 5
                    geo.vertexColorMapChannel = mode
                    geo.showVertexColors = True
                    geo.vertexColorsShaded = False
                else:
                    geo.showVertexColors = False
                    geo.vertexColorsShader = True

        rt.select(selection)
        rt.enableSceneRedraw()
        rt.completeRedraw()
        rt.resumeEditing()


def focus(nodes=None):
    """
    Focuses the viewport around the selected object/s
    """
    if nodes:
        prev_selection = [x for x in rt.selection]
        rt.selection = nodes
        rt.actionMan.executeAction(0, "310")  # Tools: Zoom Extents to Selected
        rt.selection = prev_selection
    else:
        rt.actionMan.executeAction(0, "310")
