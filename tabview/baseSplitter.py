from PyQt5.QtWidgets import QSplitter


class splitter(QSplitter):
    def __init__(self,*args,**kwargs):
        super(splitter, self).__init__(*args,**kwargs)
        self.setStyleSheet("QSplitter::handle { background-color: lightgray }")
        self.setHandleWidth(2)