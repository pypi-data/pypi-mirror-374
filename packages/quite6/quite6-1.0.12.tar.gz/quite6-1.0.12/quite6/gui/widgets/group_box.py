from PySide6.QtWidgets import QGroupBox

from .. import ContainerAbilityInterface
from .. import ui_extension


@ui_extension
class GroupBox(QGroupBox, ContainerAbilityInterface):
    pass
