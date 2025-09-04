import contextlib
from pymxs import runtime as rt


@contextlib.contextmanager
def visibility(visible: bool):
    """
    Temporarily change the visibility of the atsOps dialog.

    ```
    with visibility(False):
        ...
    ```

    Args:
        visible (bool): The temporary visibility state to set for the atsOps dialog.
    """
    visibility_before = rt.atsOps.visible
    if visible != visibility_before:
        rt.atsOps.visible = visible
        rt.atsOps.refresh()
    yield

    if visibility_before != visible:
        rt.atsOps.visible = visibility_before
        rt.atsOps.refresh()
