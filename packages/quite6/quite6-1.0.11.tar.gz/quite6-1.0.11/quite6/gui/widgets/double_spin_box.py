import prett6
from PySide6.QtWidgets import QDoubleSpinBox

from .. import BaseInterface
from .. import ui_extension


@ui_extension
class DoubleSpinBox(QDoubleSpinBox, BaseInterface, prett6.WidgetStringInterface):
    class StringItem(prett6.WidgetStringItem):
        def __init__(self, parent: 'DoubleSpinBox'):
            self.parent = parent

        def get_value(self):
            return str(self.parent.value())

        def set_value(self, value):
            if self.get_value() != value:
                self.parent.setValue(float(value or 0))

        def set_changed_connection(self):
            # noinspection PyUnresolvedReferences
            self.parent.valueChanged[float].connect(self.check_change)
