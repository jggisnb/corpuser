from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QSplitter, QHBoxLayout, QTextBrowser, QWidget
from ..base import view as baseView

class model_pkg_base_view(baseView):
    def __init__(self, *args, **kwargs):
        super(model_pkg_base_view, self).__init__(*args, **kwargs)
        self.__base_ui()

    def setup_ui(self):
        self.scrollArea.setWidget(self.contentView)

    def __base_ui(self):
        self.scrollArea = QScrollArea()

        self.contentView = QWidget()
        self.contentView.setMinimumWidth(980)

        self.textBrowser = QTextBrowser()
        self.textBrowser.setAutoFillBackground(True)
        self.textBrowser.setStyleSheet("""
            background-color: #3c3f41;
        """)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.insertWidget(0, self.scrollArea)
        self.splitter.insertWidget(1, self.textBrowser)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(2, 2)
        layout = QHBoxLayout()
        layout.addWidget(self.splitter)

        self.setLayout(layout)

    def addLog(self,log,flag):
        if flag == 1:
            self.textBrowser.append(f"<p style='color:#65CB64;font-size:14px;'>{log}</p>")
        else:
            self.textBrowser.append(f"<p style='color:#D7686D;font-size:14px;'>{log}</p>")