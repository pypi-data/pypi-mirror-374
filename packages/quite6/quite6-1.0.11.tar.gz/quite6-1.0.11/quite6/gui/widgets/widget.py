from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QCloseEvent

from .. import Painter
from .. import ui_extension
from .. import EventLoop
from .. import ClosedSignalInterface, ClassExecInterface, ContainerAbilityInterface


@ui_extension
class Widget(QWidget, ClosedSignalInterface, ClassExecInterface, ContainerAbilityInterface):
    def __init__(self, parent=None, *args):
        # noinspection PyUnresolvedReferences
        super().__init__(parent.w if getattr(parent, 'w', None) is not None else parent, *args)

    def closeEvent(self, event: QCloseEvent):
        self.quite_closed.emit()
        event.accept()

    def exec(self):
        with EventLoop() as event:
            self.show()
            self.quite_closed.connect(event.quit)

    @property
    def background_color(self):
        return self._create(lambda: None)

    @background_color.setter
    def background_color(self, value):
        self.assign(value)
        self.update()

    @property
    def size(self) -> tuple[int, int]:
        return self.width(), self.height()

    def paintEvent(self, *args, **kwargs):
        painter = Painter(self)

        if self.background_color is not None:
            painter.fillRect(self.rect(), self.background_color)
        self.paint(painter)

    def paint(self, painter: Painter):
        pass
