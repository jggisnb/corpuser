import os
import re

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRegExp
from PyQt5.QtGui import QPalette, QIcon, QColor, QTextCursor, QBrush, QTextCharFormat
from PyQt5.QtWidgets import QWidget, QTextBrowser, QSplitter, QHBoxLayout, QTextEdit, QLabel, QLineEdit, QComboBox, \
    QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QMessageBox
from control.myControl import myLineEdit
from helper.function import random_d, random_w_d, random_w_d_
from .. import baseSplitter
from ..base import view as baseView
from ..thread import uiThread_mode2, uiThread

class markTextEdit(QTextEdit):

    def __init__(self):
        super(markTextEdit, self).__init__()
        self.setStyleSheet("""
            font-size: 14px;
            font-weight:bold;
        """)
        pt = QPalette()
        pt.setBrush(QPalette.Text, Qt.white)
        pt.setBrush(QPalette.Base, QColor("#3c3f41"))
        pt.setBrush(QPalette.Highlight, QColor("#D7686D"))
        self.setPalette(pt)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._markModels = []
        self.__fmt_white = QTextCharFormat()
        self.__fmt_white.setForeground(QBrush(QColor("#ffffff")))
        self.__fmt_red = QTextCharFormat()
        self.__fmt_red.setForeground(QBrush(QColor("#D7686D")))

    def set_text_selected(self,regexs):
        self._markModels.clear()
        for regex in regexs:
            document = self.document()
            cursor = QTextCursor(document)
            hightLight = QTextCursor(document)
            cursor.beginEditBlock()
            while (not hightLight.isNull() and not hightLight.atEnd()):
                hightLight = document.find(QRegExp(regex),hightLight)
                hightLight.mergeCharFormat(self.__fmt_red)
                self.__mark(hightLight)
            cursor.endEditBlock()

    def restore_text(self,text):
        document = self.document()
        cursor = QTextCursor(document)
        hightLight = QTextCursor(document)
        cursor.beginEditBlock()
        hightLight = document.find(text, hightLight)
        hightLight.mergeCharFormat(self.__fmt_white)
        cursor.endEditBlock()

    def setText(self, text: str) -> None:
        self._markModels.clear()
        super(markTextEdit, self).setText(text)
        self.restore_text(text)


    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.parent().setEnabled(False)
        if e.button() == Qt.LeftButton:
            super(markTextEdit, self).mousePressEvent(e)
        else:
            self.cursorMove2end()
            if len(self._markModels):
                self._markModels[-1][2].mergeCharFormat(self.__fmt_white)
                self._markModels.pop(-1)
        self.parent().setEnabled(True)

    def marks(self):
        marks = []
        for mark in self._markModels:
            if len(marks) and mark[0] == marks[-1][-1]+1:
                marks[-1][-1] = mark[1]
                continue
            marks.append([mark[0],mark[1]])
        return marks

    def __mark(self,select_text):
        start = select_text.selectionStart()
        end = select_text.selectionEnd()
        if start != end:
            bemark = True
            end = end - 1
            for mark in self._markModels:
                i0 = mark[0]
                i1 = mark[1]
                if (start >= i0 and end <= i1) or (start >= i0 and start <= i1) or (end >= i0 and end <= i1) or (
                        start <= i0 and end >= i1):
                    bemark = False
                    break
            if bemark:
                select_text.mergeCharFormat(self.__fmt_red)  # 追加格式到原有文本
                self._markModels.append([start, end, select_text])
                self._markModels.sort()
            else:
                select_text.clearSelection()
                self.setTextCursor(select_text)  # 反向设定
                self.setFocus()

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            select_text = self.textCursor()  # 获取当前光标位置
            self.__mark(select_text)

        super(markTextEdit, self).mouseReleaseEvent(e)

    def cursorMove2end(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)


class view(baseView):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__(*args,**kwargs)
        self.__init_ui()

    def __init_ui(self):
        self.contentView = QWidget()
        self.contentView.setAutoFillBackground(True)

        layout0 = QHBoxLayout()
        self.input_edit = myLineEdit()
        self.input_edit.setPlaceholderText("将数据目录拖拽至此处。(必填)")
        self.input_edit.drop_sgl.connect(self.__read_input_files)

        self.file_ext_box = QComboBox()
        self.file_ext_box.addItems([".txt"])
        layout0.addWidget(QLabel("数据目录"))
        layout0.addWidget(self.input_edit)
        layout0.addWidget(self.file_ext_box)

        layout1 = QHBoxLayout()
        self.export_edit = myLineEdit()
        self.export_edit.setPlaceholderText("生成的语料导出目录。(必填)")
        layout1.addWidget(QLabel("导出目录"))
        layout1.addWidget(self.export_edit)

        self.textEdit = markTextEdit()

        self.listWgt = QListWidget()

        firstitem = QListWidgetItem(self.listWgt)
        size = self.listWgt.sizeHint()
        firstitem.setSizeHint(QSize(size.width(),28))
        self.listWgt.addItem(firstitem)
        titleLabel = QLabel("添加正则")
        titleView = QWidget()
        thLayout = QHBoxLayout()
        add_btn = QPushButton()
        add_btn.setIcon(QIcon(":/add.png"))
        add_btn.clicked.connect(self.__addcell)
        thLayout.addStretch(1)
        thLayout.addWidget(titleLabel)
        thLayout.addStretch(5)
        thLayout.addWidget(add_btn)
        thLayout.addStretch(1)
        thLayout.setContentsMargins(0,0,0,0)
        thLayout.setSpacing(0)

        titleView.setLayout(thLayout)
        titleView.setFixedHeight(28)
        self.listWgt.setSizeIncrement(size.width(),28)
        self.listWgt.setItemWidget(firstitem,titleView)

        layout2 = QVBoxLayout()

        splitter = baseSplitter.splitter(Qt.Horizontal)
        splitter.insertWidget(0, self.textEdit)
        splitter.insertWidget(1, self.listWgt)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(2, 1)

        self.next_btn = QPushButton(text="下一个(q)")
        self.next_btn.clicked.connect(self.__next_sentence)
        self.next_btn.setShortcut("q")
        self.last_btn = QPushButton(text="上一个(w)")
        self.last_btn.clicked.connect(self.__last_btn_sentence)
        self.recall_btn = QPushButton(text="撤回(e)")
        self.recall_btn.clicked.connect(self.__recall_sentence)
        layout4 = QHBoxLayout()
        label = QLabel("隐名替换(*×xX)")
        self.ruleBox = QComboBox()
        self.ruleBox.addItems([u"不开启",u"[\d]",u"[\w\d]",u"[\w\d_]"])
        layout4.addWidget(label)
        layout4.addWidget(self.ruleBox)

        layout3 = QHBoxLayout()
        layout3.addStretch(1)
        layout3.addWidget(self.next_btn)
        layout3.addStretch(1)
        layout3.addWidget(self.last_btn)
        layout3.addStretch(1)
        layout3.addWidget(self.recall_btn)
        layout3.addStretch(1)
        layout3.addLayout(layout4)
        layout3.addStretch(1)

        layout2.addLayout(layout0)
        layout2.addLayout(layout1)
        layout2.addWidget(splitter)
        layout2.addLayout(layout3)

        self.contentView.setLayout(layout2)

        layout5 = QVBoxLayout()
        self.countLabel = QLabel(f"导出数量:0")
        self.textBrowser = QTextBrowser()
        self.textBrowser.setAutoFillBackground(True)
        self.textBrowser.setStyleSheet("""
            background-color: #3c3f41;
        """)
        self.textBrowser.document().setMaximumBlockCount(500)
        layout5.addWidget(self.countLabel)
        layout5.addWidget(self.textBrowser)
        bottomView = QWidget()
        bottomView.setLayout(layout5)

        self.splitter = baseSplitter.splitter(Qt.Vertical)
        self.splitter.insertWidget(0, self.contentView)
        self.splitter.insertWidget(1, bottomView)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        layout = QHBoxLayout()
        layout.addWidget(self.splitter)

        self.setLayout(layout)

    def __inhibit_control(self):
        self.contentView.setEnabled(False)

    def __restore_control(self):
        self.contentView.setEnabled(True)

    #---------------QPushButton---------------#
    def __next_sentence(self):
        self.__inhibit_control()
        self.next_thread = uiThread()
        self.next_thread.task_no_args_sgl.connect(self.__next_sentece_sgl)
        self.next_thread.start()
        self.next_thread.finished.connect(self.onlogthread_finished)

    def __next_sentece_sgl(self):
        input_edit = self.input_edit.text()
        if not os.path.exists(input_edit) and not os.path.isdir(input_edit):
            return QMessageBox.critical(self, "错误", f"数据目录为空或者不存在:{input_edit}")

        export_edit = self.export_edit.text()
        if not os.path.exists(export_edit) and not os.path.isdir(export_edit):
            return QMessageBox.critical(self, "错误", f"导出目录不存在或不是一个文件夹:{export_edit}")

        export_edit = os.path.join(export_edit,f"export{self.__t1}.txt")

        if self._line_count > 0:
            rule = self.ruleBox.currentText()
            text = self._file_content[self._total_count-self._line_count]
            marks = self.textEdit.marks()
            mark_text = "$$$"
            browser_text = f"<p>"
            browser_wrap = []
            ischange = False
            for i,t in enumerate(text):
                if len(marks):
                    mark = marks[0]
                else:
                    mark = (-2,-1)
                if i >= mark[0] and i <= mark[1]:
                    ischange = True
                    mark_text += " B-NUM"
                    i3 = 0
                    if rule != u"不开启":
                        if rule == u"[\d]":
                            i3 = random_d()
                        elif rule == u"[\w\d]":
                            i3 = random_w_d()
                        else:
                            i3 = random_w_d_()
                    browser_wrap.append((1,t,i3))
                else:
                    mark_text += " O"
                    browser_wrap.append((0,t,0))
                    if len(marks) and ischange:
                        marks.pop(0)
                    ischange = False

            browser_texts = []
            first_in = True

            span1 = f"<span style='color:#ffffff;font-size:14px;'>"
            span2 = "<span style='color:#D7686D;font-size:14px;'>"
            span3 = "</span>"

            new_text = ""
            for i in browser_wrap:
                i2 = i[1]
                i3 = i[2]
                if i3 == 0:
                    new_text += i2
                else:
                    if re.match("[*×xX]", i2):
                        new_text += i3
                    else:
                        new_text += i2

            for i,item in enumerate(browser_wrap):
                t = new_text[i]
                if first_in and item[0] == 0:
                    browser_texts.append([0,span1,t])
                    first_in = False
                    continue
                elif first_in and item[0] == 1:
                    browser_texts.append([1,span2, t])
                    first_in = False
                    continue
                if browser_texts[-1][0] == item[0]:
                    browser_texts[-1][2] += t
                else:
                    browser_texts[-1].append(span3)
                    if item[0] == 0:
                        browser_texts.append([0, span1, t])
                    else:
                        browser_texts.append([1, span2, t])

            browser_texts[-1].append(span3)

            for bt in browser_texts:
                browser_text += "".join("".join(bt[1:]))
            browser_text += "</p>"
            self.textBrowser.append(browser_text)

            self._line_count -= 1
            self._export_contents.append(mark_text)

            export_text = new_text+mark_text
            with open(export_edit,"a",encoding="utf-8") as af:
                af.write(export_text+"\n")
            self.__count += 1
            self.__setLabelCount()
            if self._line_count > 0:
                self.textEdit.setText(self._file_content[self._total_count-self._line_count])
                self.textEdit.set_text_selected(self.get_regexs())
                return

        self._filename = self._filename_iter.readline().strip()

        if len(self._filename):
            rw = open(self._filename, "r", encoding="utf-8")
            self._file_content = rw.read().strip().split("\n")
            self._total_count = len(self._file_content)
            self._line_count = len(self._file_content)
            self.textEdit.setText(self._file_content[0])
            self.addLog(f"now read file:{self._filename}", 2)
        else:
            return QMessageBox.information(self, "info", f"数据已标完。")

    def __last_btn_sentence(self):
        self.__inhibit_control()

    def __recall_sentence(self):
        self.__inhibit_control()

    #---------------QListWidget---------------#
    class listcell(QWidget):
        delete_cell_sgl = pyqtSignal(QListWidgetItem)

        def __init__(self, item):
            super(QWidget, self).__init__()
            self.edit = QLineEdit()
            self.edit.setPlaceholderText("此处输入正则")
            thLayout = QHBoxLayout()
            sub_btn = QPushButton()
            sub_btn.setIcon(QIcon(":/sub.png"))
            sub_btn.clicked.connect(lambda: self.__deleteCell(item))
            thLayout.addWidget(self.edit)
            thLayout.addWidget(sub_btn)
            thLayout.setContentsMargins(0, 0, 0, 0)
            thLayout.setSpacing(0)
            self.setLayout(thLayout)
            self.setFixedHeight(28)

        def regex(self):
            return self.edit.text().strip()

        def __deleteCell(self, item):
            self.delete_cell_sgl.emit(item)

    def __addcell(self):
        item = QListWidgetItem(self.listWgt)
        size = self.listWgt.sizeHint()
        item.setSizeHint(QSize(size.width(), 28))
        self.listWgt.addItem(item)
        edit = QLineEdit()
        edit.setPlaceholderText(u"此处输入正则")
        view = self.listcell(item)
        view.delete_cell_sgl.connect(self.__deleteCell)
        self.listWgt.setSizeIncrement(size.width(), 28)
        self.listWgt.setItemWidget(item, view)

    def __deleteCell(self,item):
        count = self.listWgt.count()
        for i in range(count):
            im = self.listWgt.item(i)
            if item == im:
                self.listWgt.takeItem(i)
                del item
                break

    def get_regexs(self):
        count = self.listWgt.count()
        regexs = []
        for i in range(count):
            item = self.listWgt.item(i)
            cell = self.listWgt.itemWidget(item)
            if isinstance(cell,self.listcell):
                reg = cell.regex()
                if not reg in regexs:
                    regexs.append(reg)
        return regexs

    #---------------input_edit---------------#
    def __read_input_files(self,folder:str):
        self._read_input_files(folder)

    def _read_input_files(self,folder:str):
        if os.path.exists(folder) and os.path.isdir(folder):
            self.__inhibit_control()
            self.logthread = uiThread_mode2(self.__read_input_files_sgl,(folder,))
            self.logthread.start()
            self.logthread.finished.connect(self.onlogthread_finished)

    def onlogthread_finished(self):
        self.__restore_control()

    def setEditTextThread(self, control, text):
        self.setTextThread = uiThread((control, text,))
        self.setTextThread.task_sgl.connect(self.setEditTextSgl)
        self.setTextThread.start()

    def setEditTextSgl(self, args):
        control, text = args
        control.setText(text)

    def __read_input_files_sgl(self,folder):
        ext = self.file_ext_box.currentText()
        self.textBrowser.append(u"<p style='color:#6495ED;font-weight:bold;font-size:14px'>加载文件...</p>")
        count = 1
        import time
        self.__t1 = str(int(time.time()))
        if not os.path.exists("temp"):
            os.mkdir("temp")
        _filename_path = f"temp/fn{self.__t1}.txt"
        writer = open(_filename_path,"a",encoding="utf-8")
        for f in os.scandir(folder):
            path = f.path
            if os.path.isfile(path) and path.endswith(ext):
                writer.write(path+"\n")
                self.addLog(f"{count}.{path}", 1)
                count += 1
        writer.close()
        self._filename_iter = open(_filename_path,"r",encoding="utf-8")
        self._filename = self._filename_iter.readline().strip()
        rw = open(self._filename,"r",encoding="utf-8")
        self._file_content = rw.read().strip().split("\n")
        self._total_count = len(self._file_content)
        self._line_count = len(self._file_content)
        self.addLog(f"now read file:{self._filename}", 2)
        self.setEditTextThread(self.textEdit,self._file_content[0])
        self._export_contents = []
        self.__count = 0

    #---------------QLabel---------------#
    def __setLabelCount(self):
        self.countLabel.setText(f"导出数量:{self.__count}")

    def addLog(self,log,flag):
        if flag == 1:
            self.textBrowser.append(f"<p style='color:#65CB64;font-size:14px;'>{log}</p>")
        elif flag == 0:
            self.textBrowser.append(f"<p style='color:#D7686D;font-size:14px;'>{log}</p>")
        elif flag == 2:
            self.textBrowser.append(f"<p style='color:#ffffff;font-size:14px;'>{log}</p>")
        import time
        time.sleep(0.01)
