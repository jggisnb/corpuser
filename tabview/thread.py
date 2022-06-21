from PyQt5.QtCore import QThread, pyqtSignal


class uiThread(QThread):
    task_emit = pyqtSignal(tuple)
    task_no_args_emit = pyqtSignal()
    def __init__(self,*args):
        super(uiThread, self).__init__()
        self.arg = args
    def run(self) -> None:
        if self.arg:
            self.task_emit.emit(*self.arg)
        else:
            self.task_no_args_emit.emit()

class uiThread_mode2(QThread):
    def __init__(self, func, args=None):
        super(uiThread_mode2, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)