"""
Export based wrapper functions
"""
import os
from pymxs import runtime as rt


def export_nodes(
    nodes: [rt.Node],
    file_path: str,
    export_animation: bool = False,
    convert_unit: str = "cm",
    smoothing_groups: bool = True,
    smooth_mesh_export: bool = True,
    show_warnings: bool = False,
    tangent_space_export: bool = True
):
    """
    Quickly exports a series of nodes as an FBX to the given path

    Args:
        nodes ([pymxs.runtime.Node]): The Max nodes to export
        file_path (str): The path to export the FBX to
    Kwargs:
        export_animation (bool): Should animation be exported?
        convert_unit (str): The unit to convert to - defaults to "cm"
        smoothing_groups (bool): Should the geometry be exported with smoothing groups?
        smooth_mesh_export (bool): Should smooth mesh export be set?
        show_warnings (bool): Should warnings be shown?
        tangent_space_export (bool): Should tangent space export be used?
    Returns:
        bool: True if the geometry was exported - else False
    """
    success = False

    selection_cache = [x for x in rt.selection]

    with rt.undo(False):
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        try:
            merged_geometry = rt.editable_mesh()
            rt.convertToPoly(merged_geometry)

            for o in nodes:
                copy = rt.copy(o)
                rt.convertToPoly(copy)
                rt.polyOp.attach(merged_geometry, copy)

            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            rt.select(merged_geometry)

            params_without_args = ("ResetExport",)
            params_with_args = {
                "Animation": export_animation,
                "ConvertUnit": convert_unit,
                "SmoothingGroups": smoothing_groups,
                "SmoothMeshExport": smooth_mesh_export,
                "ShowWarnings": show_warnings,
                "TangentSpaceExport": tangent_space_export
            }
            for param in params_without_args:
                rt.FBXExporterSetParam(param)
            for param, value in params_with_args.items():
                rt.FBXExporterSetParam(param, value)

            rt.exportFile(
                file_path,
                rt.name("noPrompt"),
                selectedOnly=True,
                using="FBXEXP"
            )

            success = True

        except Exception as e:
            if show_warnings:
                print(str(e))
            success = False

        finally:
            rt.delete(merged_geometry)

    rt.select(selection_cache)

    return success
