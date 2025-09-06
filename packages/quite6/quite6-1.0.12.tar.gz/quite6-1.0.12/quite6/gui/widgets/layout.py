from PySide6.QtWidgets import QLayout

from .. import ContainerAbilityInterface
from .. import ui_extension


@ui_extension
class Layout(QLayout, ContainerAbilityInterface):
    pass
