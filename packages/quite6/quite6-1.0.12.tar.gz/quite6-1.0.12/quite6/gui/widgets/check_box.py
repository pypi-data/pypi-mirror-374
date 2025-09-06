import prett6
from PySide6.QtWidgets import QCheckBox

from .. import ExcitedSignalInterface
from .. import ui_extension


@ui_extension
class CheckBox(QCheckBox, ExcitedSignalInterface, prett6.WidgetStringInterface, prett6.WidgetIndexInterface):

    def set_excited_signal_connection(self):
        # noinspection PyUnresolvedReferences
        self.clicked.connect(self.excited.emit)

    class CheckBoxItem:
        def __init__(self, parent: 'CheckBox'):
            self.parent = parent

    class StringItem(CheckBoxItem, prett6.WidgetStringItem):
        def get_value(self):
            return self.parent.text()

        def set_value(self, value=None):
            self.parent.setText(value or '')
            self.check_change()


    class IndexItem(CheckBoxItem, prett6.IndexItem):
        def get_value(self):
            return 1 if self.parent.isChecked() else 0

        def set_value(self, value):
            if value is None or value == 0:
                self.parent.setChecked(False)
            else:
                self.parent.setChecked(True)
