from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette

from ..base import view as baseView

class view(baseView):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__(*args,**kwargs)
        pal = QPalette()
        pal.setColor(QPalette.Background,Qt.blue)
        self.setPalette(pal)