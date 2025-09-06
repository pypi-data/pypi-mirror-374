import prett6
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit

from .. import BaseInterface
from .. import ui_extension


@ui_extension
class DateEdit(QDateEdit, BaseInterface, prett6.WidgetStringInterface):
    class StringItem(prett6.WidgetStringItem):
        def __init__(self, parent: 'DateEdit'):
            self.parent = parent

        def get_value(self):
            return self.parent.text()

        def set_value(self, value):
            value = value or ''
            if value != self.get_value():
                date = value.split('-')
                if len(date) != 3:
                    raise ValueError('Date format is invalid')
                self.parent.setDate(QDate(int(date[0]), int(date[1]), int(date[2])))

        def set_changed_connection(self):
            # noinspection PyUnresolvedReferences
            self.parent.dateChanged.connect(self.string.check_change)
