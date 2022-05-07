from PyQt5.QtCore import QThread, pyqtSignal


class uiThread(QThread):
    task_sgl = pyqtSignal()
    def __init__(self):
        super(uiThread, self).__init__()

    def run(self) -> None:
        self.task_sgl.emit()