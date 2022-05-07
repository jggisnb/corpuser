
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtWidgets import QWidget, QTextBrowser, QSplitter, QHBoxLayout, QTextEdit, QLabel, QLineEdit, QComboBox, \
    QTreeWidget, QVBoxLayout, QPushButton, QTreeWidgetItem, QListWidget, QListWidgetItem
from control.myControl import myLineEdit
from ..base import view as baseView

class view(baseView):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__(*args,**kwargs)
        self.__init_ui()

    def __init_ui(self):
        self.contentView = QWidget()
        self.contentView.setAutoFillBackground(True)

        layout0 = QHBoxLayout()
        label = QLabel("数据目录")
        self.export_edit = myLineEdit()
        self.export_edit.setPlaceholderText("将数据目录拖拽至此或者输入目录路径。(必填)")
        self.file_ext_box = QComboBox()
        self.file_ext_box.addItems([".txt"])
        layout0.addWidget(label)
        layout0.addWidget(self.export_edit)
        layout0.addWidget(self.file_ext_box)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setStyleSheet("""
            background-color: #3c3f41;
        """)

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


        layout1 = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)
        splitter.insertWidget(0, self.textEdit)
        splitter.insertWidget(1, self.listWgt)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(2, 1)

        next_btn = QPushButton(text="下一个(alt+q)")
        last_btn = QPushButton(text="上一个(alt+w)")
        recall_btn = QPushButton(text="撤回(alt+e)")
        layout2 = QHBoxLayout()
        layout2.addStretch(1)
        layout2.addWidget(next_btn)
        layout2.addStretch(1)
        layout2.addWidget(last_btn)
        layout2.addStretch(1)
        layout2.addWidget(recall_btn)
        layout2.addStretch(1)

        layout1.addLayout(layout0)
        layout1.addWidget(splitter)
        layout1.addLayout(layout2)

        self.contentView.setLayout(layout1)

        self.textBrowser = QTextBrowser()
        self.textBrowser.setAutoFillBackground(True)
        self.textBrowser.setStyleSheet("""
            background-color: #3c3f41;
        """)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.insertWidget(0, self.contentView)
        self.splitter.insertWidget(1, self.textBrowser)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)



        layout = QHBoxLayout()
        layout.addWidget(self.splitter)

        self.setLayout(layout)

    #---------------QListWidget---------------#
    def __addcell(self):
        item = QListWidgetItem(self.listWgt)
        size = self.listWgt.sizeHint()
        item.setSizeHint(QSize(size.width(), 28))
        self.listWgt.addItem(item)
        edit = QLineEdit()
        edit.setPlaceholderText("此处输入正则")
        view = QWidget()
        thLayout = QHBoxLayout()
        sub_btn = QPushButton()
        sub_btn.setIcon(QIcon(":/sub.png"))
        sub_btn.clicked.connect(lambda: self.__deleteCell(item))
        thLayout.addWidget(edit)
        thLayout.addWidget(sub_btn)
        thLayout.setContentsMargins(0, 0, 0, 0)
        thLayout.setSpacing(0)
        view.setLayout(thLayout)
        view.setFixedHeight(28)

        self.listWgt.setSizeIncrement(size.width(), 28)
        self.listWgt.setItemWidget(item, view)

    def __deleteCell(self,item):
        self.listWgt.takeItem(item)
        del item

    #---------------QListWidget---------------#
    #---------------QListWidget---------------#

    def addLog(self,log,flag):
        if flag == 1:
            self.textBrowser.append(f"<p style='color:#65CB64;font-size:14px;'>{log}</p>")
        else:
            self.textBrowser.append(f"<p style='color:#D7686D;font-size:14px;'>{log}</p>")