import functools
import importlib.util


HOSTS_AND_THEIR_IMPORTS = {
    "max": "pymxs",
    "unreal": "unreal",
    "houdini": "hou",
    "painter": "substance_painter",
    "designer": "sd"
}


@functools.lru_cache()
def get_current_host_name() -> str:
    """
    Gets the name of the current host application.

    E.g. "max" for 3ds Max, "unreal" for Unreal Engine, etc.

    Returns:
        str: The name of the current host application.
            Or "python" if no host application is found.
    """
    # loop over the keys in HOSTS_AND_THEIR_IMPORTS
    # and check if the import exists
    for host_name, import_name in HOSTS_AND_THEIR_IMPORTS.items():
        if importlib.util.find_spec(import_name) is not None:
            return host_name
    return "python"


def hostmethod(func):
    """
    Custom decorator used to implement overrides in different host applications.

    E.g.
    ```
    @dcckit.hosts.hostmethod
    def some_function():
        pass

    @some_function.override
    def some_function():
        pass
    ```
    """
    def wrapper(*args, **kwargs):
        if (func.__override__):
            return func.__override__(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def _override(host_name):
        def _override_decorator(override_func):
            if (host_name == get_current_host_name()):
                def __override_wrapper(*args, **kwargs):
                    return override_func(*args, **kwargs)
                setattr(func, "__override__", override_func)
                setattr(__override_wrapper, "override", _override)
                return __override_wrapper
            else:
                return wrapper
        return _override_decorator

    setattr(wrapper, "override", _override)
    setattr(func, "__override__", None)
    return wrapper
