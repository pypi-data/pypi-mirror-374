import prett6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from .. import BaseInterface
from .. import ui_extension


@ui_extension
class Label(QLabel, BaseInterface, prett6.WidgetStringInterface):
    class StringItem(prett6.WidgetStringItem):
        def __init__(self, parent: 'Label'):
            self.parent = parent

        def get_value(self):
            return self.parent.text()

        def set_value(self, value):
            self.parent.setText(value or '')

    def set_clickable_text(self, show_text, call_data, call_func):
        self.setText("<a href=\"{}\">{}</a>".format(call_data, show_text))
        self.setTextFormat(Qt.TextFormat.RichText)
        self.linkActivated.connect(call_func)
