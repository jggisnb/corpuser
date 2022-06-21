import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox

from control.myControl import myLineEdit, extendedComboBox
from ..base import pkg_base_view
from ..thread import uiThread_mode2

class view(pkg_base_view):
    def __init__(self):
        super(view, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout()

        layout0 = QHBoxLayout()
        label = QLabel(u"语料目录")
        self.input_edit = myLineEdit()
        self.input_edit.setPlaceholderText(u"将语料目录拖拽至此处。(必填)")
        self.input_edit.drop_emit.connect(self.__read_input_files)
        self.file_ext_box = QComboBox()
        self.file_ext_box.addItems([".txt"])

        layout0.addWidget(label)
        layout0.addWidget(self.input_edit)
        layout0.addWidget(self.file_ext_box)

        self.reg_box = extendedComboBox()
        self.reg_box.addItems(["\\n","([\s\S]+?)[$]{3}(.+?)\\n"])

        layout1 = QHBoxLayout()
        start_btn = QPushButton(u"开始")
        layout1.addStretch(1)
        layout1.addWidget(self.reg_box)
        layout1.addWidget(start_btn)
        layout1.addStretch(1)

        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addWidget(QLabel())
        layout.addLayout(layout0)
        layout.addLayout(layout1)

        self.contentView.setLayout(layout)
        self.setup_ui()
        self.textBrowser.setMinimumHeight(500)
        self.textBrowser.document().setMaximumBlockCount(500)

    # ---------------input_edit---------------#
    def __read_input_files(self, folder: str):
        self._read_input_files(folder)

    def _read_input_files(self,folder:str):
        if os.path.exists(folder) and os.path.isdir(folder):
            self.__inhibit_control()
            self.logthread = uiThread_mode2(self.__read_input_files_sgl,(folder,))
            self.logthread.start()
            self.logthread.finished.connect(self.onlogthread_finished)

    def __read_input_files_sgl(self, folder):
        ext = self.file_ext_box.currentText()
        self.textBrowser.append(u"<p style='color:#6495ED;font-weight:bold;font-size:14px'>加载文件...</p>")
        count = 1
        import time
        self.__t1 = str(int(time.time()))
        if not os.path.exists("temp"):
            os.mkdir("temp")
        _filename_path = f"temp/fn{self.__t1}.txt"
        writer = open(_filename_path, "a", encoding="utf-8")
        for f in os.scandir(folder):
            path = f.path
            if os.path.isfile(path) and path.endswith(ext):
                writer.write(path + "\n")
                self.addLog(f"{count}.{path}", 1)
                count += 1
        writer.close()
        self._filename_iter = open(_filename_path, "r", encoding="utf-8")
        self._filename = self._filename_iter.readline().strip()
        self.addLog(f"now read file:{self._filename}", 2)

    def onlogthread_finished(self):
        self.__restore_control()

    def __inhibit_control(self):
        self.contentView.setEnabled(False)

    def __restore_control(self):
        self.contentView.setEnabled(True)

    def addLog(self,log,flag):
        if flag == 1:
            self.textBrowser.append(f"<p style='color:#65CB64;font-size:14px;'>{log}</p>")
        elif flag == 0:
            self.textBrowser.append(f"<p style='color:#D7686D;font-size:14px;'>{log}</p>")
        import time
        time.sleep(0.01)
