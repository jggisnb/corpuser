
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import queue     #如果不加载这个模板，pyinstaller打包后，可能无法运行requests模板
import requests
################################################


################################################
class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(self)

        # 增加进度条
        self.progressBar = QProgressBar(self, minimumWidth=400)
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        # 增加下载按钮
        self.pushButton = QPushButton(self, minimumWidth=100)
        self.pushButton.setText("下载")
        layout.addWidget(self.pushButton)

        # 绑定按钮事件
        self.pushButton.clicked.connect(self.on_pushButton_clicked)




    # 下载按钮事件
    def on_pushButton_clicked(self):
        the_url = 'http://cdn2.ime.sogou.com/b24a8eb9f06d6bfc08c26f0670a1feca/5c9de72d/dl/index/1553820076/sogou_pinyin_93e.exe'
        the_filesize = requests.get(the_url, stream=True).headers['Content-Length']
        the_filepath ="D:/sogou_pinyin_93e.exe"
        the_fileobj = open(the_filepath, 'wb')
        #### 创建下载线程
        self.downloadThread = downloadThread(the_url, the_filesize, the_fileobj, buffer=10240)
        self.downloadThread.download_proess_signal.connect(self.set_progressbar_value)
        self.downloadThread.start()



    # 设置进度条
    def set_progressbar_value(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            QMessageBox.information(self, "提示", "下载成功！")
            return






##################################################################
#下载线程
##################################################################
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





####################################
#程序入口
####################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())

#
# # coding='utf-8'
#
# from PyQt5.QtWidgets import QWidget, QApplication,\
#     QColorDialog, QFrame, QPushButton
# from PyQt5.QtGui import QColor
# import sys
#
#
# class Gui(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.start()
#
#     def start(self):
#         # Qt的颜色构造函数:
#         """
#         QColor(Qt.GlobalColor)
#         QColor(int)
#         QColor(QRgba64)
#         QColor(Any)
#         QColor()
#         QColor(int, int, int, alpha: int = 255)
#         QColor(str)
#         QColor(Union[QColor, Qt.GlobalColor, QGradient])
#         """
#         # 初始是黑色
#         color = QColor(0, 0, 0)
#
#         self.button = QPushButton('Dialog', self)
#         self.button.move(20, 20)
#         self.button.clicked.connect(self.show_dialog)
#
#         # QtFrame构造函数:\
#         # QFrame(parent: QWidget = None,\
#         # flags: Union[Qt.WindowFlags, Qt.WindowType]\
#         #           = Qt.WindowFlags())
#         self.frame = QFrame(self)
#         # 'QWidget {background-color: %s}' % color.name()\
#         # 这是一种特定格式的字符串,作用是设置颜色\
#         # color.name() --> 返回值是 # 000000这样的
#         self.frame.setStyleSheet(
#             'QWidget {background-color: %s}' % color.name())
#         self.frame.setGeometry(130, 22, 100, 100)
#
#         self.setGeometry(300, 300, 250, 180)
#         self.setWindowTitle('颜色选择对话框')
#         self.show()
#
#     def show_dialog(self):
#         # 弹出颜色选择对话框, 返回值是QColor
#         col = QColorDialog.getColor()
#
#         # 检测用的选择是否合法(点击cancel就是非法,否则就是合法)
#         if col.isValid():
#             # 同前面一样,设置frame框架的颜色
#             self.frame.setStyleSheet(
#             'QWidget {background-color: %s}'
#             % col.name())
#             print(col.getRgb())
#             rgbs = list(col.getRgb())[:-1]
#             rgbtext = "#"
#             for c in rgbs:
#                 rgbtext += f"{''.join(hex(c)[2:])}"
#             print(rgbtext)
#         # QColorDialog.colorSelected.emit(self.onColorSelected)
#
#
# app = QApplication(sys.argv)
# gui = Gui()
# sys.exit(app.exec_())
#
#
# # import os
# #
# #
# # with open(r"d:\Users\Administrator\Desktop\other4\export.txt","r",encoding="utf-8") as rf:
# #     read = rf.read().strip()
# #     sp = read.split("\n")
# #
# # writer1 = open(r"d:\Users\Administrator\Desktop\other4\part1.txt","a",encoding="utf-8")
# # writer2 = open(r"d:\Users\Administrator\Desktop\other4\part2.txt","a",encoding="utf-8")
# # writer3 = open(r"d:\Users\Administrator\Desktop\other4\part3.txt","a",encoding="utf-8")
# #
# # for i,s in enumerate(sp):
# #     if i % 3 == 0:
# #         writer1.write(s+"\n")
# #     elif i % 3 == 1:
# #         writer2.write(s+"\n")
# #     else:
# #         writer3.write(s+"\n")
#
#
# # os.remove(r"D:\Users\Administrator\Desktop\github\corpuser\temp\copy1652175971.py")
# # print("a"+str(chr(95)))
# # print(0*"1")
# # import subprocess
# # cmd = 'ping www.baidu.com'
# # screenData = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
# # aa = []
# # while True:
# #     line = screenData.stdout.readline()
# #     a = line.decode("gbk").strip("b'").strip()
# #     if len(a):
# #         aa.append(a)
# #     if line == b'' or subprocess.Popen.poll(screenData) == 0:
# #         screenData.stdout.close()
# #         break
# #
# # print(aa)
#
# # import re
# # with open(r"D:\Users\Administrator\Desktop\github\lawyee_ner_predict\ner\engines\model.py","r",encoding="utf-8") as rf:
# #     code = rf.read()
# #     class_name = re.findall("class\s+([\w\d_]+?)\(",code)
# #
# #
# #     # def call(self, inputs, inputs_length, targets, training=None):
# #     params = re.findall("def\s+call\s*\(\s*self([\w\W]+?)\)",code)
# #     if len(params):
# #         pass
# #     print(class_name)
#
