from PySide6.QtWidgets import QInputDialog, QMessageBox

from .. import Widget


class WidgetController:
    def __init__(self, parent=None, constructor=None):
        assert constructor is not None

        if isinstance(parent, WidgetController):
            parent = parent.w

        self.w = self.__trick__(constructor, parent)

    def question(self, text, title='选择'):
        # noinspection PyCallByClass
        return QMessageBox.question(self.w, title, text,
                                    QMessageBox.StandardButton.Yes,
                                    QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

    def warning(self, text, title='警告'):
        # noinspection PyCallByClass
        QMessageBox.warning(self.w, title, text)

    def information(self, text, title='提示'):
        # noinspection PyCallByClass
        QMessageBox.information(self.w, title, text)

    def about(self, text, title='关于'):
        # noinspection PyCallByClass
        QMessageBox.about(self.w, title, text)

    def message(self, ok=True, ok_msg='成功', bad_msg='失败'):
        if ok:
            self.information(ok_msg)
        else:
            self.warning(bad_msg)

    def input(self, title, label):
        dialog = QInputDialog()
        (text, bool_) = dialog.getText(self.w, title, label)
        return text, bool_

    @staticmethod
    def __trick__(constructor, parent) -> Widget:
        return constructor(parent)

    # actions
    def close(self):
        self.w.close()

    def show(self):
        self.w.show()

    def hide(self):
        self.w.hide()
