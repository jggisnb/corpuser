from PyQt5.QtWidgets import QVBoxLayout

from ..base import pkg_base_view


class view(pkg_base_view):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__(*args,**kwargs)
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout()



        self.contentView.setLayout(layout)
        self.setup_ui()
