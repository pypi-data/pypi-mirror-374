import prett6
from PySide6.QtWidgets import QLineEdit

from .. import FocusInSignalInterface, FocusOutSignalInterface, ExcitedSignalInterface
from .. import ui_extension


@ui_extension
class LineEdit(QLineEdit,
               prett6.WidgetStringInterface,
               FocusInSignalInterface,
               FocusOutSignalInterface,
               ExcitedSignalInterface):

    def set_excited_signal_connection(self):
        # noinspection PyUnresolvedReferences
        self.returnPressed.connect(self.excited.emit)

    class StringItem(prett6.WidgetStringItem):
        def __init__(self, parent: 'LineEdit'):
            self.parent = parent

        def get_value(self):
            return self.parent.text()

        def set_value(self, value):
            value = value or ''
            if value != self.get_value():
                self.parent.setText(value)

        def set_changed_connection(self):
            # noinspection PyUnresolvedReferences
            self.parent.textChanged.connect(self.string.check_change)

    def focusInEvent(self, e):
        super().focusInEvent(e)
        self.focus_in.emit(self.string.value)

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        self.focus_out.emit(self.string.value)
