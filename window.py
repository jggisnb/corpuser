import shutil

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QTreeWidget, QTabWidget, QSplitter, QHBoxLayout, QWidget, \
    QTreeWidgetItem
import os
from source import image
from tabview.baseSplitter import splitter


class myTreeWidgetItem(QTreeWidgetItem):
    def __init__(self,**kwargs):
        super(myTreeWidgetItem, self).__init__()
        self.Class_ = kwargs["Class_"]
        self.tab = None

class myTabWidget(QTabWidget):
    close_tab_emit = pyqtSignal(int)
    def __init__(self,*args,**kwargs):
        super(myTabWidget, self).__init__(*args,**kwargs)
        self.Tabs = []
        self.CellSet = {}
        self.tabCloseRequested.connect(self.closeTab)
        self.setTabsClosable(True)
        if os.path.exists("temp"):
            shutil.rmtree("temp")

    def refreshTabAfterIndex(self,index):
        for i in range(index,len(self.Tabs)):
            tab = self.Tabs[i]
            tab.index = i

    def closeTab(self,index):
        print(index)
        currentIndex = self.currentIndex()
        self.Tabs.pop(index)
        currentWidget = self.widget(index)
        cell = self.CellSet.pop(str(id(currentWidget)))
        cell.tab = None
        self.removeTab(index)
        currentWidget.deleteLater()
        del currentWidget
        self.refreshTabAfterIndex(index)
        if len(self.Tabs):
            if currentIndex == index:
                if index>0:
                    index = index-1
                self.setCurrentIndex(index)

    def addCell(self,tab,cell):
        self.CellSet[str(id(tab))] = cell

    def addTab(self, widget: QWidget, a1: str) -> int:
        self.Tabs.append(QWidget)
        return super(myTabWidget, self).addTab(widget,a1)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.__init_menuBar()
        mainView = QWidget()
        self.setCentralWidget(mainView)

        splitterHorizontal = splitter(Qt.Horizontal)
        tabWidget = self.__init_tabWidget()
        treeWidget = self.__init_treeWidget()
        splitterHorizontal.insertWidget(0, treeWidget)
        splitterHorizontal.insertWidget(1, tabWidget)
        splitterHorizontal.setStretchFactor(0, 1)
        splitterHorizontal.setStretchFactor(1, 20)

        layout = QHBoxLayout()
        layout.addWidget(splitterHorizontal)
        mainView.setLayout(layout)

    #--------------------tabWidget---------------------#
    def __init_tabWidget(self):
        self.tabWidget = myTabWidget()
        return self.tabWidget

    #--------------------treeWidget--------------------#
    def __init_treeWidget(self):
        from tabview.corpus.correction import view as ccview
        from tabview.corpus.regularity import view as crview
        from tabview.corpus.randomCorpus import view as rcview
        from tabview.corpus.mark import view as mview
        from tabview.model.ckpt2pb import view as cpview
        from tabview.model.pb2onnx import view as pnview
        from tabview.jige.excel_tool import view as jetview
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabel("功能大全")
        group_set = {
            u"语料": {
                u"cells": {u"语料乱序": rcview, u"语料标注工具": mview, u"基于正则语料生成": crview, u"语料纠错": ccview},
                u"icon": ":/functions.png"
            },
            u"小工具": {
                u"cells": {u"excel映射生成": jetview},
                u"icon": ":/functions.png"
            },

            # u"模型": {
            #     u"cells": {u"ckpt转pb": cpview,u"pb转onnx": pnview},
            #     u"icon": ":/model.png"
            # }
        }
        self.treeWidget.itemClicked.connect(self.treeWidget_clicked_sgl)

        for k,v in group_set.items():
            gcell = QTreeWidgetItem()
            gcell.setText(0,k)
            gcell.setIcon(0,QIcon(v["icon"]))
            items = v["cells"]
            count = 0
            for j,item in items.items():
                cell = myTreeWidgetItem(Class_=item)
                if not len(self.tabWidget.Tabs):
                    tab = item()
                    tab.index = 0
                    self.tabWidget.addTab(tab,f"{j}")
                    self.tabWidget.addCell(tab,cell)
                    cell.tab = tab
                cell.setText(0, f"{count+1}.{j}")
                gcell.addChild(cell)
                count += 1
            self.treeWidget.addTopLevelItem(gcell)

        return self.treeWidget

    def treeWidget_clicked_sgl(self,item:QTreeWidgetItem,column):
        if isinstance(item,myTreeWidgetItem):
            class_ = item.Class_
            text = item.text(column)[2:]
            if item.tab == None:
                tab = class_()
                tab.index = len(self.tabWidget)
                self.tabWidget.addTab(tab,text)
                self.tabWidget.addCell(tab,item)
                item.tab = tab
                self.tabWidget.setCurrentIndex(tab.index)
            else:
                self.tabWidget.setCurrentIndex(item.tab.index)

    #--------------------menuBar-----------------------#
    def __init_menuBar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu(u"设置")
        action1 = QAction(self, text=u"检查更新")
        fileMenu.addAction(action1)
        action1.triggered.connect(self.checkUpdate)
        self.addAction(action1)

    def checkUpdate(self):
        print("check update action")