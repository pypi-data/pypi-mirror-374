from PySide6.QtWidgets import QDockWidget

from .. import ContainerAbilityInterface
from .. import ui_extension


@ui_extension
class DockWidget(QDockWidget, ContainerAbilityInterface):
    pass
