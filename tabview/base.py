from PyQt5.QtWidgets import QWidget


class view(QWidget):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__()
        if "index" in kwargs.keys():
            self.index = kwargs["index"]
        self.setAutoFillBackground(True)
