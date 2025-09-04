from dcckit.host import hostmethod


_QAPP = None


@hostmethod
def get_application():
    """
    Gets the QApplication instance for the current host application.

    Note: Creates a new instance if it does not exist.
        E.g. Unreal and Blender do not natively use Qt.

    Returns:
        QApplication: The QApplication instance.
    """
    raise NotImplementedError


def _create_qapp_in_non_qt_native_host():
    """
    Creates a QApplication instance in a host that does not natively use Qt.
    This is used for hosts like Blender and Unreal Engine.
    """
    from qtpy import QtWidgets
    global _QAPP
    if _QAPP is None:
        _QAPP = QtWidgets.QApplication([])


@get_application.override("blender")
def get_application():
    _create_qapp_in_non_qt_native_host()
    return _QAPP


@get_application.override("unreal")
def get_application():
    _create_qapp_in_non_qt_native_host()
    return _QAPP

# -----------------------------------------------------------------------

@hostmethod
def get_main_window():
    """
    Returns the main window for the current host application
    """
    raise NotImplementedError


@get_main_window.override("houdini")
def get_main_window():
    import hou
    return hou.ui.mainQtWindow()


@get_main_window.override("painter")
def get_main_window():
    import substance_painter.ui
    return substance_painter.ui.get_main_window()


@get_main_window.override("designer")
def get_main_window():
    import sd
    app = sd.getContext().getSDApplication()
    uiMgr = app.getQtForPythonUIMgr()
    return uiMgr.getMainWindow()

# -----------------------------------------------------------------------


@hostmethod
def register_widget(widget):
    """
    Registers a widget with the current host application

    Some widgets require additional registration in order to
    correctly parent to the main window

    E.g. Unreal does not use Qt so requires extra steps to bind to the slate UI

    Args:
        widget (QWidget): The widget to register
    """
    return


@register_widget.override("unreal")
def register_widget(widget):
    import unreal
    unreal.parent_external_window_to_slate(
        widget.winId(),
        unreal.SlateParentWindowSearchMethod.ACTIVE_WINDOW
    )

# -----------------------------------------------------------------------


@hostmethod
def create_dock_widget(child_widget, identifier="", title="Dock"):
    """
    Creates a dock widget in the current host.

    Different hosts can have different implementations for dock widgets

    Args:
        child_widget (QWidget): The widget to place inside the dock widget
    Kwargs:
        identifier (str): The unique identifier for the dock widget
        title (str): The title of the dock widget
    """
    raise NotImplementedError


@create_dock_widget.override("designer")
def create_dock_widget(child_widget, identifier="", title="Dock"):
    import sd
    from qtpy import QtWidgets
    ui_mgr = sd.getContext().getSDApplication().getQtForPythonUIMgr()
    output = ui_mgr.newDockWidget(identifier, title)
    main_layout = QtWidgets.QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    output.setLayout(main_layout)
    main_layout.addWidget(child_widget)
    return output

@create_dock_widget.override("painter")
def create_dock_widget(child_widget, identifier="", title="Dock"):
    import substance_painter.ui
    output = substance_painter.ui.add_dock_widget(child_widget)
    output.setWindowTitle(title)
    return output
