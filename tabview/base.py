from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget


class view(QWidget):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__()
        if "index" in kwargs.keys():
            self.index = kwargs["index"]
        self.setAutoFillBackground(True)


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QHBoxLayout, QTextBrowser, QWidget

from . import baseSplitter

class pkg_base_view(view):
    def __init__(self, *args, **kwargs):
        super(pkg_base_view, self).__init__(*args, **kwargs)
        self.__base_ui()

    def setup_ui(self):
        self.scrollArea.setWidget(self.contentView)

    def __base_ui(self):
        self.scrollArea = QScrollArea()

        self.contentView = QWidget()
        self.contentView.setMinimumWidth(1200)

        self.textBrowser = QTextBrowser()
        self.textBrowser.setAutoFillBackground(True)
        self.textBrowser.setStyleSheet("""
            background-color: #3c3f41;
        """)

        self.splitter = baseSplitter.splitter(Qt.Vertical)
        self.splitter.insertWidget(0, self.scrollArea)
        self.splitter.insertWidget(1, self.textBrowser)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(2, 2)
        layout = QHBoxLayout()
        layout.addWidget(self.splitter)

        self.setLayout(layout)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(view, self).resizeEvent(a0)
        self.scrollArea.resize(self.textBrowser.width(), self.scrollArea.height())
        self.contentView.resize(self.textBrowser.width()-53, self.contentView.height())


