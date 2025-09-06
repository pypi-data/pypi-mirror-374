import typing

import numpy as np
import pyqtgraph as pg
from PySide6.QtGui import QCloseEvent
from PySide6.QtGui import QFont

from .. import ClosedSignalInterface, ClassExecInterface
from .. import EventLoop
from .. import ui_extension

pg.setConfigOptions(antialias=True)


@ui_extension
class PlotWidget(pg.PlotWidget, ClosedSignalInterface, ClassExecInterface):
    def __init__(self, parent=None):
        super().__init__(parent=parent, background=(255, 255, 255))

        self.line_pen = pg.mkPen(color=(0, 0, 0), width=3)
        self.axis_pen = pg.mkPen(color=(0, 0, 0), width=1)
        self.labelStyle = {'color': '#000000', 'font-size': '14pt', 'font-family': "微软雅黑"}

        self.getPlotItem().showGrid(x=True, y=True, alpha=0.4)
        self.setMouseEnabled(x=False, y=False)

        font = QFont('Arial', 10)
        axes = ('top', 'bottom', 'left', 'right')
        for axis in axes:
            self.getPlotItem().showAxis(axis)
            self.getPlotItem().getAxis(axis).tickFont = font
            self.getPlotItem().getAxis(axis).setPen(self.axis_pen)

    def closeEvent(self, event: QCloseEvent):
        self.quite_closed.emit()
        event.accept()

    def exec(self):
        with EventLoop() as event:
            self.show()
            self.quite_closed.connect(event.quit)

    def plot(self, x=None, y=None, *args, **kwargs):
        """

        :param x: array_like
        :param y: array_like
        :return: None
        """
        self.getPlotItem().plot(x=x, y=y, pen=self.line_pen, *args, **kwargs)

    def append_plot(self, x=None, y=None, *args, **kwargs):
        """

        :param x: array_like
        :param y: array_like
        :return: None
        """
        if x is None or y is None:
            return
        if len(x) != len(y):
            raise Exception('X and Y arrays must be the same shape--got({}, ) and ({}, )'.format(len(x), len(y)))

        old_data = self.get_data()
        if old_data:
            x = np.append(old_data[0], x)
            y = np.append(old_data[1], y)
        # clear old data and repaint
        self.clear()
        self.plot(x=x, y=y, *args, **kwargs)

    def clear(self):
        self.getPlotItem().clear()

    def get_data(self) -> typing.Tuple[np.ndarray, np.ndarray]:
        """

        return last plot data
        """
        if self.getPlotItem().items:
            return self.getPlotItem().items[-1].getData()

    def set_x_label(self, text=None, units=None):
        # noinspection PyArgumentList
        self.getPlotItem().setLabel('bottom', text=text, units=units, **self.labelStyle)

    def set_y_label(self, text=None, units=None):
        # noinspection PyArgumentList
        self.getPlotItem().setLabel('left', text=text, units=units, **self.labelStyle)

    def set_labels(self, text=None, units=None):
        if text is None:
            return
        if len(text) != 2:
            raise ValueError("Label Text Length Must Equal to Two")
        if units is not None:
            if len(text) != len(units):
                raise ValueError("Label Text Length Must Equal to Label Units")
            self.set_x_label(text[0], units[0])
            self.set_y_label(text[1], units[1])
        else:
            self.set_x_label(text=text[0])
            self.set_y_label(text=text[1])
