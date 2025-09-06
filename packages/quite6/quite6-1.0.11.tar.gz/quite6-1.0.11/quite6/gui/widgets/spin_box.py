import prett6
from PySide6.QtWidgets import QSpinBox

from .. import BaseInterface
from .. import ui_extension


@ui_extension
class SpinBox(QSpinBox, BaseInterface, prett6.WidgetStringInterface):
    class StringItem(prett6.WidgetStringItem):
        def __init__(self, parent: 'SpinBox'):
            self.parent = parent

        def get_value(self):
            return str(self.parent.value())

        def set_value(self, value):
            if self.get_value() != value:
                self.parent.setValue(int(value or 0))

        def set_changed_connection(self):
            # noinspection PyUnresolvedReferences
            self.parent.valueChanged[int].connect(self.check_change)
