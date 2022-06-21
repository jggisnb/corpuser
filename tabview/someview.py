from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QFrame


class frameview(QWidget):
    def __init__(self,*args,**kwargs):
        super(QWidget, self).__init__()
        self.__frame = QFrame(self)
        self.__frame.setFrameShape(QFrame.Box)
        self.__frame.setFrameShadow(QFrame.Raised)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.__frame.resize(a0.size())