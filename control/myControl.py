
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLineEdit


class myLineEdit(QLineEdit):
    drop_sgl = pyqtSignal(str)
    def __init__(self,*args,**kwargs):
        super(myLineEdit, self).__init__()
        self.setAcceptDrops(True)  # 设置接受拖放动作
        self.setAttribute(Qt.WA_StyledBackground)

    def dragEnterEvent(self, e):
        if e.mimeData().text():  # 如果是.srt结尾的路径接受
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):  # 放下文件后的动作
        path = e.mimeData().text().replace('file:///', '')  # 删除多余开头
        self.setText(path)
        self.drop_sgl.emit(path)