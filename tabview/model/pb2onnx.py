from PyQt5.QtWidgets import QVBoxLayout

from tabview.model.pkg_base import model_pkg_base_view


class view(model_pkg_base_view):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__(*args,**kwargs)
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout()



        self.contentView.setLayout(layout)
        self.setup_ui()
