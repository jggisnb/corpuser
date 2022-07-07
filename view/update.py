import os
import time
import zipfile

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout

from window import MainWindow


class downloadThread(QThread):
    download_proess_signal = pyqtSignal(int)                        #创建信号

    def __init__(self, url, filesize, fileobj, buffer):
        super(downloadThread, self).__init__()
        self.url = url
        self.filesize = filesize
        self.fileobj = fileobj
        self.buffer = buffer


    def run(self):
        try:
            rsp = requests.get(self.url, stream=True)                #流下载模式
            offset = 0
            for chunk in rsp.iter_content(chunk_size=self.buffer):
                if not chunk: break
                self.fileobj.seek(offset)                            #设置指针位置
                self.fileobj.write(chunk)                            #写入文件
                offset = offset + len(chunk)
                proess = offset / int(self.filesize) * 100
                self.download_proess_signal.emit(int(proess))        #发送信号
            #######################################################################
            self.fileobj.close()    #关闭文件
            self.exit(0)            #关闭线程

        except Exception as e:
            print(e)


class dialog(QDialog):
    # close_emit = pyqtSignal()
    def __init__(self,url,pwd,version,pid):
        super(dialog, self).__init__()
        self.__main_pid = pid
        layout = QVBoxLayout(self)
        layout1 = QHBoxLayout(self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setValue(0)
        layout1.addWidget(self.progressBar)

        self.message_label = QLabel("检查更新")
        layout.addLayout(layout1)
        layout.addWidget(self.message_label)
        self.pwd = pwd
        the_url = url+f'/project{version}.zip'
        the_filesize = requests.get(the_url, stream=True).headers['Content-Length']
        self.the_filepath = os.path.join(self.pwd,f'project{version}.zip')
        the_fileobj = open(self.the_filepath, 'wb')
        #### 创建下载线程
        self.downloadThread = downloadThread(the_url, the_filesize, the_fileobj, buffer=10240)
        self.downloadThread.download_proess_signal.connect(self.set_progressbar_value)
        self.downloadThread.start()
        self.show()
        self.window = MainWindow()

    # 设置进度条
    def set_progressbar_value(self, value):
        if value > 0:
            self.message_label.setText("正在下载更新文件")
        self.progressBar.setValue(value)
        if value == 100:
            self.message_label.setText("下载完成,开始解压文件")
            self.close()
            os.system(f"{os.path.join(self.pwd,'update.exe')} {self.__main_pid} {self.the_filepath}")
            # self.window.setGeometry(100, 50, 1350, 800)
            # self.window.setWindowTitle("nlp tools")
            # self.window.show()
            # self.close_emit.emit()


# if __name__ == "__main__":
#     import sys
#     from PyQt5.QtWidgets import QApplication
#     app = QApplication(sys.argv[1:])
#     window = dialog()
#     window.setGeometry(100,50,400,100)
#     window.setWindowTitle("更新程序")
#     window.show()
#     sys.exit(app.exec_())






