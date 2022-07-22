


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from tabview.corpus.mark import view as mview
    from source import image
    app = QApplication(sys.argv[1:])
    window = mview()
    window.setGeometry(100, 50, 1350, 800)
    window.setWindowTitle("mark tool")
    window.show()
    sys.exit(app.exec_())