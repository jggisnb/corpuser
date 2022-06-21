import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout, QWidget


class shapeLayout(QHBoxLayout):
    def __init__(self ,*args ,**kwargs):
        super(QHBoxLayout, self).__init__(*args ,**kwargs)
        self.items = []

    def addWidget(self, a0: QWidget, stretch: int = ..., alignment: typing.Union[QtCore.Qt.Alignment, QtCore.Qt.AlignmentFlag] = ...) -> None:
        super(QHBoxLayout, self).addWidget(a0)
        self.items.append(a0)

    def getLen(self):
        return len(self.items)

    def deleteWidget(self):
        if self.getLen() > 0:
            lastWidget = self.items[-1]
            lastWidget.deleteLater()
            self.items.pop(-1)
            del lastWidget
