import os
import re
import sys
from typing import List

from bs4 import BeautifulSoup

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRegExp
from PyQt5.QtGui import QPalette, QIcon, QColor, QTextCursor, QBrush, QTextCharFormat, QRegExpValidator
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QLabel, QLineEdit, QComboBox, \
    QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QMenu, QAction, QFrame, QColorDialog, QDialog
from control.myControl import myLineEdit
from helper import function
from helper.function import random_d, random_w_d, random_w_d_
from .. import baseSplitter
from ..base import pkg_base_view
from ..layout import shapeLayout
from ..thread import uiThread_mode2, uiThread

class markTextEdit(QTextEdit):
    insert_part_emit = pyqtSignal()
    def __init__(self,parent):
        self.parentView = parent

        self.__shutcut_map = {}
        for i in range(0,12):
            self.__shutcut_map[f"f{i+1}"] = 16777264 + i

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

        self.__menu = QMenu()
        action = QAction("插入身份证",self)
        action.triggered.connect(self.insertCreditCard)
        action1 = QAction("插入手机号码",self)
        action1.triggered.connect(self.insertPhoneNumber)
        action2 = QAction("插入微信号",self)
        action2.triggered.connect(self.insertWeChat)
        self.__menu.addAction(action)
        self.__menu.addAction(action1)
        self.__menu.addAction(action2)

        self.__key_press = False
        self.__beMove = False
        self.__beMark = False

    def insertCreditCard(self):
        self.insertPlainText(function.getCreditCard())
        self.insert_part_emit.emit()

    def insertPhoneNumber(self):
        self.insertPlainText(function.getPhomeNumber())
        self.insert_part_emit.emit()

    def insertWeChat(self):
        self.insertPlainText(function.getWeChat())
        self.insert_part_emit.emit()

    def check_legitimacy(self):
        checked,_ = self.parentView.check_legitimacy(False)
        if checked:
            return self.parentView.markinfo
        else:
            return False

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if Qt.Key_F1 <= e.key() <= Qt.Key_F12:
            self.__key_press = e.key()
        else:
            super(markTextEdit, self).keyPressEvent(e)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent) -> None:
        if self.__key_press:
            select_text = self.textCursor()
            start = select_text.selectionStart()
            end = select_text.selectionEnd()
            if start != end:
                markinfo = self.check_legitimacy()
                self.__mark_with_info(markinfo,select_text)
                self.__key_press = False
                return
        self.__key_press = False
        return super(markTextEdit, self).keyReleaseEvent(e)

    def __mark_with_info(self,markinfo,textCursor):
        if markinfo:
            for k, v in markinfo.items():
                if int(self.__shutcut_map[v["shutcut"]]) == self.__key_press:
                    colorFormat = QTextCharFormat()
                    colorFormat.setForeground(QBrush(QColor(v["color"])))
                    textCursor.mergeCharFormat(colorFormat)
                    textCursor.clearSelection()
                    self.setTextCursor(textCursor)  # 反向设定
                    self.setFocus()
                    return

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            self.__menu.move(self.cursor().pos())
            self.__menu.show()
        elif e.button() == Qt.LeftButton:
            if self.__key_press:
                self.__beMark = True
        super(markTextEdit, self).mousePressEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.__beMove = True
        super(markTextEdit, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            if self.__beMark and self.__beMove:
                markinfo = self.check_legitimacy()
                select_text = self.textCursor()
                self.__mark_with_info(markinfo,select_text)
            else:
                select_text = self.textCursor()
                select_text.mergeCharFormat(self.__fmt_white)

        self.__beMark = False
        self.__beMove = False
        super(markTextEdit, self).mouseReleaseEvent(e)

    def refresh_text_selected(self,regexs):
        for reg,color in regexs:
            document = self.document()
            cursor = QTextCursor(document)
            hightLight = QTextCursor(document)
            cursor.beginEditBlock()
            while (not hightLight.isNull() and not hightLight.atEnd()):
                hightLight = document.find(QRegExp(reg), hightLight)
                colorFormat = QTextCharFormat()
                colorFormat.setForeground(QBrush(QColor(color)))
                hightLight.mergeCharFormat(colorFormat)
            cursor.endEditBlock()

    def setText_and_selected(self,text,regexs):
        self.setTextThread = uiThread((text, regexs))
        self.setTextThread.task_emit.connect(self.__setText_and_selected_sgl)
        self.setTextThread.start()

    def render_text(self,text,markinfo):
        self.setTextThread = uiThread((text, markinfo))
        self.setTextThread.task_emit.connect(self.__setText_and_render_sgl)
        self.setTextThread.start()

    def __setText_and_selected_sgl(self,args):
        text,regexs = args
        self.__clearHighlight()
        self.setText(f"<span style=\"color:#ffffff;font-size:14px\">{text}</span>")
        self.refresh_text_selected(regexs)

    def __setText_and_render_sgl(self,args):
        text,markinfo = args
        b4 = BeautifulSoup(text, "html.parser")
        full_tags = b4.find_all("p")
        context = "<p style=\"color:#ffffff;font-size:14px\">"
        for ft in full_tags:
            tags = ft.contents
            for tag in tags:
                text = str(tag)
                if "class" in text:
                    attrs = tag.attrs
                    class_ = attrs["class"][0]
                    text = f"<span style=\"color:{markinfo[class_]['color']};\">{tag.text}</span>"
                else:
                    text = f"<span style=\"color:#ffffff;\">{tag.text}</span>"
                context += text
        context += "</p>"
        self.setText(context)
        print(context)

    def __clearHighlight(self):
        select_text = self.textCursor()
        select_text.clearSelection()
        self.setTextCursor(select_text)  # 反向设定
        self.setFocus()

    def restore_text(self,text):
        document = self.document()
        cursor = QTextCursor(document)
        hightLight = QTextCursor(document)
        cursor.beginEditBlock()
        hightLight = document.find(text, hightLight)
        hightLight.mergeCharFormat(self.__fmt_white)
        cursor.endEditBlock()

    def cursorMove2end(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)


from ..someview import frameview
class shapeView(frameview):

    def __init__(self,cur_idx=0):
        super(shapeView, self).__init__()
        layout = QVBoxLayout()
        layout0 = QHBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        self.cells = []
        label0 = QLabel("标签 ")
        label0.setStyleSheet("font-size: 11px;")
        self.mark_edit = QLineEdit()
        reg = QRegExp("[a-zA-Z]{1,10}")
        self.mark_edit.setPlaceholderText(u"只能输入字母")
        self.mark_edit.setMaximumWidth(85)
        pValidator = QRegExpValidator(self.mark_edit)
        pValidator.setRegExp(reg)
        self.mark_edit.setValidator(pValidator)
        layout0.addWidget(label0)
        layout0.addWidget(self.mark_edit)
        layout0.addStretch(0)

        label1 = QLabel("颜色 ")
        label1.setStyleSheet("font-size: 11px;")
        self.__col_frame = QFrame()
        self.__col_frame.setMinimumSize(50,20)
        self.__col_frame.setStyleSheet("""QWidget{background-color:#D7686D;}""")
        self.colort_text = "#D7686D"
        col_select_btn = QPushButton("选择")
        col_select_btn.setMaximumWidth(30)
        col_select_btn.clicked.connect(self.__on_color_select_sgl)
        layout1.addWidget(label1)
        layout1.addWidget(self.__col_frame)
        layout1.addWidget(col_select_btn)
        layout1.addStretch(0)

        label2= QLabel("快捷键")
        label2.setStyleSheet("font-size: 11px;")
        self.shutcutBox = QComboBox()
        self.shutcutBox.addItems(["f" + str(i) for i in range(1,13)])
        self.shutcutBox.setCurrentIndex(cur_idx)
        layout2.addWidget(label2)
        layout2.addWidget(self.shutcutBox)
        layout2.addStretch(0)

        layout.addLayout(layout0)
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addStretch(0)
        self.setLayout(layout)

    def getCellLen(self):
        return len(self.cells)

    def appendcell(self,cell):
        self.cells.append(cell)

    def removecell(self,cell):
        self.cells.remove(cell)

    def __on_color_select_sgl(self):
        col = QColorDialog.getColor()

        # 检测用的选择是否合法(点击cancel就是非法,否则就是合法)
        if col.isValid():
            # 同前面一样,设置frame框架的颜色

            rgbs = list(col.getRgb())[:-1]
            rgbtext = "#"
            for c in rgbs:
                rgbtext += f"{''.join(hex(c)[2:])}"
            self.colort_text = rgbtext
            if not self.colort_text == "#ffffff":
                self.__col_frame.setStyleSheet('background-color: %s' % col.name())
                return

        self.colort_text = "#D7686D"
        self.__col_frame.setStyleSheet('background-color:#D7686D;')

class click_frame(QFrame):
    clicked_emit = pyqtSignal(QFrame)
    def __init__(self,color_str):
        super(click_frame, self).__init__()
        self.setMaximumSize(50, 20)
        self.__color_str = color_str
        self.setStyleSheet(f"QWidget{{background-color:{color_str};border:none;}}")
        self.is_click = False

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        super(click_frame, self).mousePressEvent(a0)
        self.set_is_click(not self.is_click)

    def get_color(self):
        return self.__color_str

    def set_is_click(self,is_click):
        self.is_click = is_click
        if self.is_click:
            self.setStyleSheet(f"""
                QWidget{{background-color:{self.__color_str};border:3px solid #000000;}}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget{{background-color:{self.__color_str};border:none;}}
            """)
        self.clicked_emit.emit(self)

class regexDialog(QDialog):
    # border: 1
    # px
    # solid  # 000000;
    add_color_emit = pyqtSignal(str,str)
    def __init__(self,*args,**kwargs):
        super(regexDialog, self).__init__(*args,**kwargs)
        self.resize(250,120)
        self.__is_init = False
        self.adjustSize()

    def execute(self,colors):
        if not self.__is_init:
            self.__is_init = True
            self.contentView = QWidget()
            layout0 = QHBoxLayout()
            label = QLabel("输入正则")
            self.regex_edit = QLineEdit()
            self.regex_edit.setPlaceholderText(u"此处输入正则")
            layout0.addWidget(label)
            layout0.addWidget(self.regex_edit)
            self.framelayout = QHBoxLayout()
            self.__frames = []
            self.__addColorFrame(colors)
            confirm_btn = QPushButton(u"确定")
            confirm_btn.clicked.connect(self.__confirm_sgl)
            cancel_btn = QPushButton(u"取消")
            cancel_btn.clicked.connect(self.__cancel_sgl)
            layout2 = QHBoxLayout()
            layout2.addStretch(1)
            layout2.addWidget(confirm_btn)
            layout2.addStretch(1)
            layout2.addWidget(cancel_btn)
            layout2.addStretch(1)

            layout = QVBoxLayout()
            layout.addLayout(layout0)
            layout.addLayout(self.framelayout)
            layout.addLayout(layout2)
            self.contentView.setLayout(layout)
            layout3 = QVBoxLayout()
            layout3.addWidget(self.contentView)
            self.setLayout(layout3)
        else:
            ln = len(self.__frames)
            self.regex_edit.setText("")
            for i in range(ln):
                frame = self.__frames[0]
                frame.setVisible(False)
                self.framelayout.removeWidget(frame)
                frame.deleteLater()
                self.__frames.pop(0)
                del frame
            self.__addColorFrame(colors)
        self.exec_()
        #
    # def execute(self):
    def __cancel_sgl(self):
        self.close()

    def __confirm_sgl(self):
        text = self.regex_edit.text().strip()
        if not len(text):
            return QMessageBox.warning(self, "警告", "正则表达式不能为空。")
        for f in self.__frames:
            if f.is_click:
                self.add_color_emit.emit(f.get_color(),text)
                self.close()
                return 1
        return QMessageBox.warning(self, "警告", "没有选中颜色，请选一种颜色。")


    def __addColorFrame(self,colors):
        for c in colors:
            frame = click_frame(c)
            frame.clicked_emit.connect(self.__frame_clicked_sgl)
            self.__frames.append(frame)
            self.framelayout.addWidget(frame)
            self.framelayout.setSpacing(10)

    def __frame_clicked_sgl(self,frame:click_frame):
        if frame.is_click:
            for f in self.__frames:
                if f != frame and f.is_click:
                    f.set_is_click(False)


class view(pkg_base_view):

    def __init__(self,*args,**kwargs):
        super(view, self).__init__(*args,**kwargs)
        self.__init_ui()
        self.markinfo = {}

    def __get_mark_items(self)->List[shapeView]:
        return self.mark_layout.items

    def check_legitimacy(self,showMessage=True):
        self.markinfo = {}
        items = self.__get_mark_items()
        for mi in items:
            mark_value = mi.mark_edit.text()
            if not len(mark_value):
                if showMessage:
                    return False,QMessageBox.warning(self, "警告", "存在标注为空,请补全。")
                else:
                    return False,None
            mark_col = mi.colort_text
            shutcut = mi.shutcutBox.currentText()
            for k,v in self.markinfo.items():
                if mark_col == v["color"]:
                    if showMessage:
                        return False,QMessageBox.warning(self,"警告","存在标注颜色重复,请修改")
                    else:
                        return False,None
                elif shutcut == v["shutcut"]:
                    if showMessage:
                        return False,QMessageBox.warning(self,"警告",f"存在标注快捷键重复,请修改:{shutcut}")
                    else:
                        return False,None
                elif k == mark_value:
                    if showMessage:
                        return False,QMessageBox.warning(self,"警告",f"存在标注名称重复,请修改:{mark_value}")
                    else:
                        return False,None
            self.markinfo[mark_value] = {}
            self.markinfo[mark_value]["color"] = mark_col
            self.markinfo[mark_value]["shutcut"] = shutcut
        return True,None

    def __init_ui(self):
        self.regex_dialog = regexDialog()
        self.regex_dialog.add_color_emit.connect(self.__add_listcell)
        layout0 = QHBoxLayout()
        self.input_edit = myLineEdit()
        self.input_edit.setPlaceholderText("将数据目录拖拽至此处。(必填)")
        self.input_edit.drop_emit.connect(self.__read_input_files)

        self.file_ext_box = QComboBox()
        self.file_ext_box.addItems([".txt"])
        layout0.addWidget(QLabel("数据目录"))
        layout0.addWidget(self.input_edit)
        layout0.addWidget(self.file_ext_box)

        layout1 = QHBoxLayout()
        self.export_edit = myLineEdit()
        self.export_edit.setPlaceholderText(u"生成的语料导出目录拖拽至此处。(必填)")
        layout1.addWidget(QLabel(u"导出目录"))
        layout1.addWidget(self.export_edit)

        self.textEdit = markTextEdit(self)
        self.textEdit.insert_part_emit.connect(self.__insert_part_sgl)

        self.listWgt = QListWidget()

        firstitem = QListWidgetItem(self.listWgt)
        size = self.listWgt.sizeHint()
        firstitem.setSizeHint(QSize(size.width(),28))
        self.listWgt.addItem(firstitem)
        titleLabel = QLabel(u"添加正则")
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
        self.next_btn.setShortcut("alt+q")
        self.recall_btn = QPushButton(text="撤回(w)")
        self.recall_btn.clicked.connect(self.__recall_sentence)
        self.recall_btn.setShortcut("w")
        self.rest_export_btn = QPushButton(text="导出剩余")
        self.rest_export_btn.clicked.connect(self.__rest_export)

        layout4 = QHBoxLayout()
        label = QLabel("隐名替换(*×xX)")
        self.ruleBox = QComboBox()
        self.ruleBox.addItems([u"不开启",u"[0-9]",u"[a-zA-Z0-9]",u"[a-zA-Z0-9_]"])
        layout4.addWidget(label)
        layout4.addWidget(self.ruleBox)

        layout3 = QHBoxLayout()
        layout3.addStretch(1)
        layout3.addWidget(self.next_btn)
        layout3.addStretch(1)
        layout3.addWidget(self.recall_btn)
        layout3.addStretch(1)
        # layout3.addWidget(self.rest_export_btn)
        # layout3.addStretch(1)
        layout3.addLayout(layout4)
        layout3.addStretch(1)

        layout6 = QVBoxLayout()
        self.countLabel = QLabel(f"导出数量:0")
        layout6.addWidget(splitter)
        layout6.addWidget(self.countLabel)
        layout6.addStretch(0)

        layout7 = QHBoxLayout()
        label1 = QLabel(u"添加标注\n (BIO)")
        layout7.addWidget(label1)
        self.mark_layout = shapeLayout()
        self.mark_layout.addWidget(shapeView())
        layout7.addLayout(self.mark_layout)

        layout8 = QHBoxLayout()
        self.mark_addBtn = QPushButton()
        self.mark_addBtn.setIcon(QIcon(":/add.png"))
        self.mark_addBtn.clicked.connect(self.__add_mark_sgl)
        self.mark_subBtn = QPushButton()
        self.mark_subBtn.setIcon(QIcon(":/sub.png"))
        self.mark_subBtn.clicked.connect(self.__sub_mark_sgl)
        layout8.addWidget(self.mark_addBtn)
        layout8.addWidget(self.mark_subBtn)
        layout8.addStretch(0)

        layout7.addLayout(layout8)
        layout7.addStretch(3)

        layout2.addLayout(layout0)
        layout2.addLayout(layout1)
        layout2.addLayout(layout7)
        layout2.addLayout(layout6)
        layout2.addLayout(layout3)
        layout2.addStretch(0)

        self.contentView.setLayout(layout2)

        self.setup_ui()
        self.textBrowser.setMinimumHeight(300)
        self.textBrowser.document().setMaximumBlockCount(500)

    def __inhibit_control(self):
        self.contentView.setEnabled(False)

    def __restore_control(self):
        self.contentView.setEnabled(True)

    #---------------QPushButton---------------#
    def __add_mark_sgl(self):
        self.mark_layout.addWidget(shapeView(self.mark_layout.getLen()))

    def __sub_mark_sgl(self):
        if self.mark_layout.getLen() > 1:
            lastWidget = self.mark_layout.items[-1]
            if lastWidget.getCellLen():
                return QMessageBox.warning(self,"警告",f"该标注还存在关联正则，请删除正则后再删除该标注。")
            self.mark_layout.deleteWidget()

    def __next_sentence(self):
        self.__inhibit_control()
        self.next_thread = uiThread()
        self.next_thread.task_no_args_emit.connect(self.__next_sentece_sgl)
        self.next_thread.start()
        self.next_thread.finished.connect(self.onlogthread_finished)

    def __next_sentece_sgl(self):
        try:
            input_edit = self.input_edit.text()
            if not os.path.exists(input_edit) and not os.path.isdir(input_edit):
                return QMessageBox.critical(self, "错误", f"数据目录为空或者不存在:{input_edit}")

            export_edit = self.export_edit.text()
            if not os.path.exists(export_edit) and not os.path.isdir(export_edit):
                return QMessageBox.critical(self, "错误", f"导出目录不存在或不是一个文件夹:{export_edit}")

            export_edit = os.path.join(export_edit,f"export{self.__t1}.txt")

            if self._line_count > 0:
                html = self.textEdit.document().toHtml()
                b4 = BeautifulSoup(html, "html.parser")
                full_tags = b4.find_all("p")

                rule = self.ruleBox.currentText()
                isrule = rule != u"不开启"
                brower_text = "<p style=\"color:#ffffff;font-size:14px;background-color:black;\">"
                for ft in full_tags:
                    tags = ft.contents
                    for tag in tags:
                        class_ = "O"
                        if "style" in str(tag):
                            attrs = tag.attrs
                            style = attrs["style"].strip()
                            if "color" in style:
                                color = style.split("color:")[1][:-1]
                                for k,v in self.markinfo.items():
                                    for key,item in v.items():
                                        if key =="color":
                                            if item.lower() == color:
                                                class_ = k
                            else:
                                color = "#ffffff"
                            string = str(tag.string).strip()
                        else:
                            color = "#ffffff"
                            string = str(tag)
                        brower_text += f"<span class=\"{class_}\" style=\"color:{color};\">"

                        for s in string:
                            if isrule and re.match("[*×xXｘＸ]",s):
                                if rule == u"[0-9]":
                                    s1 = random_d()
                                elif rule == u"[a-zA-Z0-9]":
                                    s1 = random_w_d()
                                else:
                                    s1 = random_w_d_()
                            else:
                                s1 = s
                            brower_text += s1

                        brower_text += "</span>"
                brower_text += "</p>"
                self.textBrowser.append(brower_text)

                with open(export_edit,"a",encoding="utf-8") as af:
                    af.write(brower_text+"\n")

                self._line_count -= 1
                self.__count += 1
                self.__setLabelCount()
                if self._line_count > 0:
                    text = self._file_content[self._total_count-self._line_count]
                    self.__setText_and_selected(text)
                    return

            self._filename = self._filename_iter.readline().strip()

            if len(self._filename):
                rw = open(self._filename, "r", encoding="utf-8")
                self._file_content = rw.read().strip().split("\n")
                self._total_count = len(self._file_content)
                self._line_count = len(self._file_content)
                self.textEdit.setText(self._file_content[0])
                rw.close()
                self.addLog(f"now read file:{self._filename}", 2)
            else:
                return QMessageBox.information(self, "消息", f"数据已标完。")
        except Exception as e:
            return QMessageBox.critical(self,"错误",f"{e}")

    def __rest_export(self):
        self.__inhibit_control()
        self.rest_thread = uiThread()
        self.rest_thread.task_no_args_emit.connect(self.__rest_export_sgl)
        self.rest_thread.start()
        self.rest_thread.finished.connect(self.onlogthread_finished)

    def __rest_export_sgl(self):
        input_edit = self.input_edit.text()
        if not os.path.exists(input_edit) and not os.path.isdir(input_edit):
            return QMessageBox.critical(self, "错误", f"数据目录为空或者不存在:{input_edit}")

        export_edit = self.export_edit.text()
        if not os.path.exists(export_edit) and not os.path.isdir(export_edit):
            return QMessageBox.critical(self, "错误", f"导出目录不存在或不是一个文件夹:{export_edit}")

        import datetime
        t1 = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        fn = f"{t1}{os.path.basename(self._filename)}"
        export_edit = os.path.join(export_edit, fn)

        _line_count = self._line_count
        if self._total_count > self._line_count:
            text = self._file_content[self._total_count - self._line_count:]
            with open(export_edit,"w",encoding="utf-8") as wf:
                wf.write(text)
            return QMessageBox.information(self, u"消息", f"导出成功:{export_edit}")
        else:
            return QMessageBox.warning(self,u"警告",f"文件{self._filename}导出失败。")


    def __recall_sentence(self):
        self.__inhibit_control()
        self.last_thread = uiThread()
        self.last_thread.task_no_args_emit.connect(self.__recall_sentece_sgl)
        self.last_thread.start()
        self.last_thread.finished.connect(self.onlogthread_finished)

    def __recall_sentece_sgl(self):
        try:
            input_edit = self.input_edit.text()
            if not os.path.exists(input_edit) and not os.path.isdir(input_edit):
                return QMessageBox.critical(self, "错误", f"数据目录为空或者不存在:{input_edit}")

            export_edit = self.export_edit.text()
            if not os.path.exists(export_edit) and not os.path.isdir(export_edit):
                return QMessageBox.critical(self, "错误", f"导出目录不存在或不是一个文件夹:{export_edit}")

            export_edit = os.path.join(export_edit, f"export{self.__t1}.txt")

            if self.__count > 0:
                self.__count -= 1
            if self._line_count < self._total_count:
                self._line_count += 1
            self.__setLabelCount()
            text = self._file_content[self._total_count - self._line_count]
            self.__setText_and_selected(text)
            with open(export_edit,"r",encoding="utf-8") as rf:
                content = rf.read().strip()
                print(content)
                sp = content.split("\n")
                while "" in sp:sp.remove("")
                if len(sp)>1:
                    with open(export_edit,"w",encoding="utf-8") as wf:
                        wf.write("\n".join(sp[:-1]))
                else:
                    with open(export_edit,"w",encoding="utf-8") as wf:
                        wf.write("")
        except Exception as e:
            return QMessageBox.critical(self, "错误", f"{e}")


    #---------------QListWidget---------------#
    def __add_listcell(self,color_str:str,regex_str:str):
        item = QListWidgetItem(self.listWgt)
        size = self.listWgt.sizeHint()
        item.setSizeHint(QSize(size.width(), 28))
        self.listWgt.addItem(item)
        view = self.listcell(item,regex_str,color_str)
        view.delete_cell_emit.connect(self.__deleteCell_sgl)
        self.listWgt.setSizeIncrement(size.width(), 28)
        self.listWgt.setItemWidget(item, view)
        for mi in self.mark_layout.items:
            if mi.colort_text == color_str:
                mi.appendcell(item)
                return self.__refresh_text_selected()

    class listcell(QWidget):
        delete_cell_emit = pyqtSignal(QListWidgetItem)
        def __init__(self, item,regex_str:str, color_str):
            super(QWidget, self).__init__()
            regex_str = regex_str.strip()
            self.edit = QLabel(regex_str)
            self.edit.setToolTip(regex_str)
            thLayout = QHBoxLayout()
            frame = QFrame()
            frame.setMaximumSize(50,20)
            frame.setStyleSheet(f"QWidget{{background-color:{color_str};}}")
            self.__color_str = color_str
            sub_btn = QPushButton()
            sub_btn.setIcon(QIcon(":/sub.png"))
            sub_btn.setMaximumSize(20,20)
            sub_btn.clicked.connect(lambda: self.__deleteCell(item))
            thLayout.addWidget(self.edit)
            thLayout.addWidget(frame)
            thLayout.addWidget(sub_btn)
            thLayout.setContentsMargins(0, 0, 0, 0)
            thLayout.setSpacing(0)
            self.setLayout(thLayout)
            self.setFixedHeight(28)

        def get_color(self):
            return self.__color_str

        def regex(self):
            return self.edit.text()

        def __deleteCell(self, item):
            self.delete_cell_emit.emit(item)

    def __addcell(self):
        legitimacy = self.check_legitimacy()
        if legitimacy[0]:
            colors = []
            for k,v in self.markinfo.items():
                colors.append(v["color"])
            self.regex_dialog.execute(colors)

    def __deleteCell_sgl(self,item):
        count = self.listWgt.count()
        for i in range(count):
            im = self.listWgt.item(i)
            if item == im:
                widget = self.listWgt.itemWidget(item)
                self.__marklayout_delete_cell_withWidget(widget)
                self.listWgt.takeItem(i)
                del item
                break

    def __marklayout_delete_cell_withWidget(self,widget):
        for mi in self.mark_layout.items:
            for cell in mi.cells:
                w = self.listWgt.itemWidget(cell)
                if widget == w:
                    mi.removecell(cell)
                    return

    def get_regexs(self):
        count = self.listWgt.count()
        regexs = []
        for i in range(count):
            item = self.listWgt.item(i)
            cell = self.listWgt.itemWidget(item)
            if isinstance(cell,self.listcell):
                reg = cell.regex()
                if not reg in regexs:
                    yield reg,cell.get_color()

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
        self.setTextThread.task_emit.connect(self.setEditTextSgl)
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
        self.__count = 0
        checked,_ = self.check_legitimacy(False)
        if checked:
            self.__setText_and_selected(self._file_content[0])
        else:
            self.setEditTextThread(self.textEdit,self._file_content[0])

    #---------------QLabel---------------#
    def __setLabelCount(self):
        self.countLabel.setText(f"导出数量:{self.__count}")

    def __insert_part_sgl(self):
        # refresh
        self.__refresh_text_selected()

    def __refresh_text_selected(self):
        self.textEdit.refresh_text_selected(self.get_regexs())

    def __setText_and_selected(self,text):
        if not text.startswith("<p>"):
            self.textEdit.setText_and_selected(text,self.get_regexs())
        else:
            self.textEdit.render_text(text,self.markinfo)

    def addLog(self,log,flag):
        if flag == 1:
            self.textBrowser.append(f"<p style='color:#65CB64;font-size:14px;'>{log}</p>")
        elif flag == 0:
            self.textBrowser.append(f"<p style='color:#D7686D;font-size:14px;'>{log}</p>")
        elif flag == 2:
            self.textBrowser.append(f"<p style='color:#ffffff;font-size:14px;'>{log}</p>")
        import time
        time.sleep(0.01)
