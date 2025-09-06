from PySide6.QtCore import Qt

from . import WidgetUiController
from ..gui import Shortcut


class DialogUiController(WidgetUiController):
    def __init__(self, parent=None, ui_file=None):
        super().__init__(parent, ui_file)

        Shortcut('ctrl+w', self.w).excited.connect(self.w.close)

    def exec(self):
        return self.w.exec()

    def setWindowMinimizeButtonHint(self):
        self.w.setWindowFlags(Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)

    @classmethod
    def class_exec(cls, *args, **kwargs):
        return cls(*args, **kwargs).exec()
