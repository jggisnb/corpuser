from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QFrame


class clicked_frame(QFrame):
    clicked_emit = pyqtSignal()
    color = "#d7686d"
    def __init__(self,*args,**kwargs):
        super(clicked_frame, self).__init__(*args,**kwargs)
        self.setAutoFillBackground(True)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        super(clicked_frame, self).mousePressEvent(a0)
        if a0.button() == Qt.LeftButton:
            self._pressed = True
            self.setStyleSheet(f'background-color: #40{self.color[1:]}')

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        super(clicked_frame, self).mouseReleaseEvent(a0)
        if a0.button() == Qt.LeftButton and hasattr(self,"_pressed") and self._pressed:
            self._pressed = False
            self.clicked_emit.emit()
        self.setStyleSheet(f'background-color: #ff{self.color[1:]}')


class frameview(QWidget):
    def __init__(self,*args,**kwargs):
        super(QWidget, self).__init__()
        self.__frame = QFrame(self)
        self.__frame.setFrameShape(QFrame.Box)
        self.__frame.setFrameShadow(QFrame.Raised)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.__frame.resize(a0.size())