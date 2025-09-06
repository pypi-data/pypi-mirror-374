import prett6
from PySide6.QtWidgets import QRadioButton

from .. import ExcitedSignalInterface
from .. import ui_extension


@ui_extension
class RatioButton(QRadioButton, ExcitedSignalInterface, prett6.WidgetStringInterface):
    def set_excited_signal_connection(self):
        # noinspection PyUnresolvedReferences
        self.clicked.connect(self.excited.emit)

    class StringItem(prett6.WidgetStringItem):
        def __init__(self, parent: 'RatioButton'):
            self.parent = parent

        def get_value(self):
            return self.parent.text()

        def set_value(self, value):
            self.parent.setText(value or '')
            self.check_change()
