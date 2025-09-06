from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow

from .. import ClassExecInterface
from .. import ClosedSignalInterface
from .. import ContainerAbilityInterface
from .. import EventLoop
from .. import ui_extension


@ui_extension
class MainWindow(QMainWindow, ClosedSignalInterface, ClassExecInterface, ContainerAbilityInterface):
    def closeEvent(self, event: QCloseEvent):
        if self.can_close:
            self.quite_closed.emit()
            event.accept()
        else:
            self.cannot_closed.emit()
            event.ignore()

    def exec(self):
        with EventLoop() as event:
            self.show()
            self.quite_closed.connect(event.quit)
