import prett6
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QTabWidget

from .. import ExcitedSignalInterface, ContainerAbilityInterface
from .. import ui_extension


@ui_extension
class TabWidget(QTabWidget, ContainerAbilityInterface, ExcitedSignalInterface,
                prett6.WidgetIndexInterface):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.check_before_switch = None
        self.tabBar().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.tabBar() and event.type() == QEvent.Type.MouseButtonPress:
            mouse_event = event
            pos = mouse_event.position().toPoint()
            index = self.tabBar().tabAt(pos)
            if self.check_before_switch is not None and not self.check_before_switch(index):
                return True
        return super().eventFilter(obj, event)

    def install_check_before_switch(self, func):
        self.check_before_switch = func

    class TabWidgetItem:
        def __init__(self, parent: 'TabWidget'):
            self.parent = parent

        @property
        def count(self):
            return self.parent.count()

        def tab_text(self, idx):
            return self.parent.tabText(idx)

    class IndexItem(TabWidgetItem, prett6.IndexItem):
        def get_value(self):
            return self.parent.currentIndex()

        def set_value(self, value):
            value = value or 0
            self.parent.setCurrentIndex(value)

        def set_changed_connection(self):
            # noinspection PyUnresolvedReferences
            self.parent.currentChanged.connect(self.check_change)
