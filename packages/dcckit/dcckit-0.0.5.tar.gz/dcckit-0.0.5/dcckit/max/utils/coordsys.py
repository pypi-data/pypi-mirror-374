from pymxs import runtime as rt


class CoordSys(object):
    def __init__(self, target_coordsys):
        """
        Context manager used to temporarily change coordinate systems in 3ds Max.

        The same as using `in coordsys target` in Maxscript.

        Valid coordinate systems are:
        - local
        - world
        - parent
        - grid
        - screen

        ```
        with CoordSys("local") as cs:
            pass
        ```

        Args:
            target_coordsys (str): The target coordinate system to switch to.
        """
        self._target_coordsys = rt.name(target_coordsys)
        self._coordsys = getattr(rt, "%coordsys_context")
        self._previous_coordsys = None

    def __enter__(self):
        self._previous_coordsys = self._coordsys(self._target_coordsys, None)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._coordsys(self._previous_coordsys, None)
