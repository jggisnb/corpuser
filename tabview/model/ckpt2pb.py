import re
import shutil
import sys
import typing
from PyQt5 import QtCore, QtGui
import os
import time
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIcon, QRegExpValidator
from control.myControl import myLineEdit
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QPushButton, QHBoxLayout, \
    QVBoxLayout, QWidget, QFrame, QTextEdit, QMessageBox, QSpinBox
from typing import List
from ..base import pkg_base_view
from ..layout import shapeLayout
from ..thread import uiThread
from ..someview import frameview


class fview(frameview):
    def __init__(self, title, maxheight):
        super(fview, self).__init__()
        self.title = QLabel(title)
        self.vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()
        layout0.addStretch(1)
        layout0.addWidget(self.title)
        layout0.addStretch(1)
        self.vlayout.addLayout(layout0)
        self.setLayout(self.vlayout)
        self.setMaximumHeight(maxheight)

    def addlayout(self, layout):
        self.vlayout.addLayout(layout)
        self.vlayout.addStretch(0)

class shapeView(frameview):
    def __init__(self,count):
        super(shapeView, self).__init__()
        self.count = count

        self.setAutoFillBackground(True)
        layout = QVBoxLayout()
        _layout0 = QHBoxLayout()
        _layout1 = QHBoxLayout()

        label0 = QLabel("shape")
        label0.setStyleSheet("font-size: 11px;")
        self.shape_edit = QLineEdit()
        reg = QRegExp("[,\d]+")
        self.shape_edit.setPlaceholderText(u"格式:[0-9]+,")
        pValidator = QRegExpValidator(self.shape_edit)
        pValidator.setRegExp(reg)
        self.shape_edit.setValidator(pValidator)

        self.typebox = QComboBox()
        self.typebox.addItems(["int16", "int32", "int64", "int8", "float16", "float32", "float64",
                               "bfloat16", "double", "bool", "complex128", "complex64", "half",
                               "qint16", "qint32", "qint8", "quint16", "quint8", "resource",
                               "string", "uint16", "uint32", "uint64", "uint8", "variant"])

        _layout0.addWidget(label0)
        _layout0.addWidget(self.shape_edit)
        _layout0.addWidget(self.typebox)
        _layout0.addStretch(0)

        label1 = QLabel("name ")
        label1.setStyleSheet("font-size: 11px;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(f"param{count}")
        _layout1.addWidget(label1)
        _layout1.addWidget(self.name_edit)
        _layout1.addStretch(0)
        layout.addLayout(_layout1)
        layout.addLayout(_layout0)
        self.setLayout(layout)

    def type(self):
        return self.typebox.currentText()

    def name(self):
        name = self.name_edit.text()
        if not len(name):
            name = f"param{self.count}"
        return name

    def shape(self):
        shape_edit = self.shape_edit.text()
        if len(shape_edit):
            shape_edit = shape_edit.split(",")
            while "" in shape_edit:shape_edit.remove("")
            for i in range(len(shape_edit)):
                shape_edit[i] = shape_edit[i]
            return shape_edit
        else:
            return None


class view(pkg_base_view):
    def __init__(self,*args,**kwargs):
        super(view, self).__init__(*args,**kwargs)
        self.__init_ui()

    class shapeModel:
        def __init__(self,shape,name,type_):
            self.shape = shape
            self.name = name
            self.type = type_

    def __init_ui(self):
        self.transforView = fview("模型转换",250)

        label = QLabel(u"checkpoint路径 ")
        self.model_path = myLineEdit()
        self.model_path.setPlaceholderText(u"将checkpoint目录文件夹拖拽至输入框。(必填)")
        label0 = QLabel(u"ckpt类型")
        self.modelBox = QComboBox()
        self.modelBox.addItems(["tf2","pytorch"])

        layout0 = QVBoxLayout()
        layout01 = QHBoxLayout()
        layout01.addWidget(label)
        layout01.addWidget(self.model_path)
        layout01.addWidget(label0)
        layout01.addWidget(self.modelBox)

        layout02 = QHBoxLayout()
        label1 = QLabel(u"预训练模型路径 ")
        self.premodel_path = myLineEdit()
        self.premodel_path.setPlaceholderText(u"将预训练模型文件夹拖拽至输入框,也可以选择右侧提供的可选项。(可选)")
        self.premodelBox = QComboBox()
        self.premodelBox.addItems(["bert-base-chinese","albert-tiny-chinese"])
        layout02.addWidget(label1)
        layout02.addWidget(self.premodel_path)
        layout02.addWidget(self.premodelBox)

        layout03 = QHBoxLayout()
        label2 = QLabel(u"keras模型py    ")
        self.kerasmodel_path = myLineEdit()
        self.kerasmodel_path.drop_emit.connect(self.__read_kerasmodel)
        self.kerasmodel_path.setPlaceholderText(u"将模型的py文件拖拽至输入框,py文件的初始化函数中要有且仅有包含一个参数:预训练模型路径,例如\"__init__(self,premodel=None):\"(必填)")
        layout03.addWidget(label2)
        layout03.addWidget(self.kerasmodel_path)

        layout04 = QHBoxLayout()
        label3 = QLabel(u"checkpoint name")
        self.ckptname_edit = QLineEdit()
        self.ckptname_edit.setPlaceholderText(u"checkpoint成员变量名,默认:ner_model(可选)")
        layout04.addWidget(label3)
        layout04.addWidget(self.ckptname_edit)
        layout04.addStretch(0)

        layout05 = QHBoxLayout()
        label4 = QLabel(u"pb导出路径     ")
        self.export_edit = myLineEdit()
        self.export_edit.setPlaceholderText(u"将导出文件夹拖拽至此处,也可以不填,默认为checkpoint路径同级目录下导出。(可选)")
        layout05.addWidget(label4)
        layout05.addWidget(self.export_edit)

        layout0.addLayout(layout01)
        layout0.addLayout(layout02)
        layout0.addLayout(layout03)
        layout0.addLayout(layout04)
        layout0.addLayout(layout05)

        layout1 = QHBoxLayout()

        self.input_layout = shapeLayout()
        self.input_layout.addWidget(shapeView(0))

        layout11 = QHBoxLayout()
        self.input_addBtn = QPushButton()
        self.input_addBtn.setIcon(QIcon(":/add.png"))
        self.input_addBtn.clicked.connect(self.__add_inputShape_sgl)
        self.input_subBtn = QPushButton()
        self.input_subBtn.setIcon(QIcon(":/sub.png"))
        self.input_subBtn.clicked.connect(self.__sub_inputShape_sgl)
        layout11.addWidget(self.input_addBtn)
        layout11.addWidget(self.input_subBtn)

        layout12 = QVBoxLayout()
        label5 = QLabel(u"模型输入")
        layout12.addStretch(2)
        layout12.addWidget(label5)
        layout12.addStretch(1)

        layout13 = QVBoxLayout()
        layout13.addStretch(2)
        layout13.addLayout(layout11)
        layout13.addStretch(1)

        layout1.addLayout(layout12)
        layout1.addLayout(self.input_layout)
        layout1.addLayout(layout13)
        layout1.addStretch(3)

        layout2 = QHBoxLayout()
        startBtn = QPushButton()
        startBtn.setText("转化模型")
        startBtn.clicked.connect(self.__start_ckpt2pb)
        layout2.addStretch(1)
        layout2.addWidget(startBtn)
        layout2.addStretch(1)

        layout3 = QVBoxLayout()
        layout3.addLayout(layout0)
        layout3.addLayout(layout1)
        layout3.addLayout(layout2)
        layout3.addStretch(0)
        self.transforView.addlayout(layout3)

        self.testView = fview("模型测试",200)
        label = QLabel(u"pb路径  ")
        self.test_model_path = myLineEdit()
        self.test_model_path.setPlaceholderText(u"将模型目录文件夹拖拽至此处。")
        label0 = QLabel(u"最大长度")
        self.maxLengthBox = QSpinBox()
        self.maxLengthBox.setMaximum(999)
        self.maxLengthBox.setSingleStep(100)
        self.maxLengthBox.setValue(300)

        layout0 = QHBoxLayout()
        layout0.addWidget(label)
        layout0.addWidget(self.test_model_path)
        layout0.addWidget(label0)
        layout0.addWidget(self.maxLengthBox)

        layout1 = QHBoxLayout()
        label1 = QLabel(u"测试句子")
        self.textEdit = QTextEdit()
        self.textEdit.setPlaceholderText("在这里输入测试句子")
        layout1.addWidget(label1)
        layout1.addWidget(self.textEdit)

        layout2 = QHBoxLayout()
        startTestBtn = QPushButton()
        startTestBtn.setText("测试句子")
        startTestBtn.clicked.connect(self.__start_pbTest)
        layout2.addStretch(1)
        layout2.addWidget(startTestBtn)
        layout2.addStretch(1)

        layout3 = QVBoxLayout()
        layout3.addLayout(layout0)
        layout3.addLayout(layout1)
        layout3.addLayout(layout2)
        layout3.addStretch(0)
        self.testView.addlayout(layout3)

        layout = QVBoxLayout()
        layout.addWidget(self.transforView)
        layout.addWidget(self.testView)

        self.contentView.setLayout(layout)
        self.setup_ui()
        self.textBrowser.setMinimumHeight(225)


    # -------------------kerasmodel pre fix-------------------#
    def __read_kerasmodel(self,kerasmodel_path:str):
        if os.path.exists(kerasmodel_path) and os.path.isfile(kerasmodel_path) and kerasmodel_path.endswith(".py"):
            try:
                with open(kerasmodel_path,"r",encoding="utf-8") as rf:
                    code = rf.read().strip()
                    params:List = re.findall("def\s+call\s*\(\s*self([\w\W]+?)\)", code)
                    if len(params):
                        params:str = params[0]
                        params:List = params.split(",")
                        while "" in params:params.remove("")
                        params = [pm.split("=")[0] for pm in params]
                        ln = self.input_layout.getLen()
                        for i,pm in enumerate(params):
                            if i+1 <= ln:
                                shapeview = self.input_layout.items[i]
                                shapeview.name_edit.setText(pm.strip())
                            else:
                                self.__add_inputShape_sgl()
                                shapeview = self.input_layout.items[-1]
                                shapeview.name_edit.setText(pm.strip())
                    else:
                        return
            except Exception as e:
                return QMessageBox.warning(self, "警告", f"tf.keras.model的py文件格式有误:{kerasmodel_path}")

    #-------------------sub/add shapeView-------------------#
    def __add_inputShape_sgl(self):
        self.input_layout.addWidget(shapeView(self.input_layout.getLen()))

    def __sub_inputShape_sgl(self):
        if self.input_layout.getLen() > 1:
            self.input_layout.deleteWidget()

    #--------------------set widget enabled-------------------#
    def __inhibit_control(self):
        self.testView.setEnabled(False)
        self.transforView.setEnabled(False)

    def __restore_control(self):
        self.testView.setEnabled(True)
        self.transforView.setEnabled(True)

    #--------------------test pb available-------------------#
    def __start_pbTest(self):
        self.__inhibit_control()
        try:
            self.pbTest_thread = uiThread()
            self.pbTest_thread.task_no_args_emit.connect(self.__pbTest)
            self.pbTest_thread.start()
        except Exception as e:
            return QMessageBox.critical(self, "错误", f"{str(e)}")
        self.__restore_control()

    def __pbTest(self):
        data = self.__pre_pbTest()
        if type(data) == tuple:
            test_file, pythonexe = data
            self.__cmdProcess(f'{pythonexe} {test_file}',"pbTest")
            self._pythonfile = test_file

    def __pre_pbTest(self):
        pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
        test_model_path = self.test_model_path.text()
        if not os.path.exists(test_model_path) and not os.path.isdir(test_model_path):
            return QMessageBox.critical(self, "错误", f"不存在pb目录:{test_model_path}")
        textEdit = self.textEdit.toPlainText().strip()
        if not len(textEdit):
            return QMessageBox.critical(self, "错误",  "测试句子不能为空!")
        maxLengthBox = self.maxLengthBox.value()
        if maxLengthBox == 0:
            return QMessageBox.critical(self, "错误", "最大句子长度不能为0!")
        elif maxLengthBox < len(textEdit):
            return QMessageBox.critical(self, "错误", f"句子长度不能大于最大长度{maxLengthBox}!")
        tokenizer_path = os.path.join(pwd,"pretrain","bert-base-chinese")
        if not os.path.exists(tokenizer_path):
            return QMessageBox.critical(self, "错误", f"失去目录:{tokenizer_path}")
        ckptname_edit = self.ckptname_edit.text().strip()
        if len(ckptname_edit):
            if not re.match("[\w_]", ckptname_edit[0]):
                return QMessageBox.critical(self, "错误", f"checkpoint name不能以非字母下划线开头:{ckptname_edit}")
        else:
            ckptname_edit = "ner_model"

        if not os.path.exists("temp"):
            os.mkdir("temp")
        t1 = int(time.time())
        filename = f"temp/copy{t1}.py"
        with open(filename, "w", encoding="utf-8") as wf:
            code =  "import tensorflow as tf\nfrom transformers import BertTokenizer\nimport numpy as np\n"
            objname = f"m{t1}"
            code += f"{objname} = tf.saved_model.load(r\"{test_model_path}\")\n"
            code += f"tokenizer = BertTokenizer.from_pretrained(r\"{tokenizer_path}\")\n"
            code += f"sentence = list(u\"{textEdit}\")\n"
            code += f"x = tokenizer.encode(sentence)\n" \
                    f"att_mask = [1] * len(x)\n" \
                    f"a = len(x)\n" \
                    f"b = len(att_mask)\n" \
                    f"x += [0 for _ in range({maxLengthBox} - a)]\n" \
                    f"att_mask += [0 for _ in range({maxLengthBox} - b)]\n" \
                    f"x = np.array([x])\n" \
                    f"att_mask = np.array([att_mask])\n" \
                    f"logits = {objname}.{ckptname_edit}.call(x, att_mask)\n" \
                    f"print(logits)\n"
            wf.write(code)

        sp = filename.split("/")
        tempdir = os.path.join(pwd, sp[0])
        test_file = os.path.join(tempdir, sp[1])
        pythonexe = os.path.join(pwd, "env", "pbenv", "python.exe")
        return test_file,pythonexe

    #--------------------transform model 2 pb------------------#
    def __start_ckpt2pb(self):
        self.__inhibit_control()
        try:
            self.ckpt2pb_thread = uiThread()
            self.ckpt2pb_thread.task_no_args_emit.connect(self.__ckpt2pb)
            self.ckpt2pb_thread.start()
        except Exception as e:
            return QMessageBox.critical(self, "错误", f"{str(e)}")
        self.__restore_control()

    def __ckpt2pb(self):
        data = self.__pre_ckpt2pb()
        if type(data)==tuple:
            transform_file, pythonexe = data
            self.__cmdProcess(f'{pythonexe} {transform_file}',"ckpt2pb")
            self._pythonfile = transform_file

    def __pre_ckpt2pb(self):
        pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
        modelpath = self.model_path.text().strip()
        if not os.path.exists(modelpath) or not os.path.isdir(modelpath):
            return QMessageBox.critical(self, "错误", f"不存在checkpoint目录:{modelpath}")
        premodel_path = self.premodel_path.text().strip()
        if len(premodel_path):
            if not os.path.exists(premodel_path) and not os.path.isdir(premodel_path):
                return QMessageBox.critical(self, "错误", f"不存在预训练模型目录:{premodel_path}")
        else:
            premodel_path = os.path.join(pwd,"pretrain",self.premodelBox.currentText())
        kerasmodel_path = self.kerasmodel_path.text().strip()
        if not os.path.exists(kerasmodel_path) or not os.path.isfile(kerasmodel_path) or not kerasmodel_path.endswith(".py"):
            return QMessageBox.critical(self, "错误", f"不存在tf.keras.model的py文件:{kerasmodel_path}")
        ckptname_edit = self.ckptname_edit.text().strip()
        if len(ckptname_edit):
            if not re.match("[\w_]",ckptname_edit[0]):
                return QMessageBox.critical(self, "错误", f"checkpoint name不能以非字母下划线开头:{ckptname_edit}")
        else:
            ckptname_edit = "ner_model"

        t1 = int(time.time())

        self.__export_edit = self.export_edit.text().strip()
        if len(self.__export_edit):
            if not os.path.exists(self.__export_edit) and not os.path.isdir(self.__export_edit):
                return QMessageBox.critical(self, "错误", f"不存在导出路径或者不是一个目录:{self.__export_edit}")
        else:
            self.__export_edit =  os.path.join(os.path.dirname(modelpath),f"pb{os.path.basename(modelpath)}{t1}")

        shapeViews = self.input_layout.items
        models = []
        for shapeView in shapeViews:
            shape = shapeView.shape()
            if not shape:
                return QMessageBox.critical(self, "错误", f"shape不能为空:param{shapeView.count}")
            name = shapeView.name().strip()
            models.append(self.shapeModel(shape,name,shapeView.type()))
        if not os.path.exists("temp"):
            os.mkdir("temp")
        filename = f"temp/copy{t1}.py"
        with open(filename,"w",encoding="utf-8") as wf:
            with open(kerasmodel_path,"r",encoding="utf-8") as rf:
                code = rf.read()

                class_name = re.findall("class\s+([\w\d_]+?)\(", code)
                if not len(class_name):
                    return QMessageBox.critical(self, "错误", f"tf.keras.model的py文件不存在class:{kerasmodel_path}")
                else:
                    class_name = class_name[0]
                objname = f"m{t1}"
                transform_code = f"{objname} = {class_name}(r\"{premodel_path}\")\r\n"
                transform_code +=  "import tensorflow as tf\r\n"
                transform_code += f"checkpoint = tf.train.Checkpoint({ckptname_edit}={objname})\r\n"
                transform_code += f"checkpoint.restore(tf.train.latest_checkpoint(r\"{modelpath}\"))\r\n"

                transform_code += f"tf.saved_model.save(checkpoint, r\"{self.__export_edit}\", signatures={objname}.call.get_concrete_function("
                for m in models:
                    transform_code += f"tf.TensorSpec([{','.join(m.shape)}],tf.{m.type},name=\"{m.name}\"),"
                transform_code = transform_code[:-1]+"))"

                code += "\n\n"+transform_code
                if not os.path.exists(self.__export_edit):
                    os.mkdir(self.__export_edit)
                wf.write(code)
                sp = filename.split("/")
                tempdir = os.path.join(pwd,sp[0])
                transform_file = os.path.join(tempdir,sp[1])
                pythonexe = os.path.join(pwd,"env","pbenv","python.exe")
                return transform_file,pythonexe

    # --------------------transform model 2 pb------------------#
    def __cmdProcess(self,cmd,message):
        try:
            self.__message = message
            if message == "ckpt2pb":
                self.textBrowser.setText(u"<p style='color:#6495ED;font-weight:bold;font-size:14px'>ckpt转化pb:</p>")
            elif message == "pbTest":
                self.textBrowser.setText(u"<p style='color:#6495ED;font-weight:bold;font-size:14px'>pb模型测试:</p>")
        
            self.process = QtCore.QProcess()
            self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
            self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
            self.process.finished.connect(self.onFinished)
            self.process.start(cmd)
        except Exception as e:
            return QMessageBox.critical(self, "错误", f"cmd wrong:{str(e)}")

    def onReadyReadStandardError(self):
        error = self.process.readAllStandardError().data().decode().strip()
        self.addLog(error,0)

    def onReadyReadStandardOutput(self):
        result = self.process.readAllStandardOutput().data().decode().strip()
        self.addLog(result,1)

    def onFinished(self,p_int, QProcess_ExitStatus):

        print(p_int,QProcess_ExitStatus)

        if p_int == 0:
            if self.__message == "ckpt2pb":
                self.addLog(f"转换完成,导出路径:{self.__export_edit}", 1)
            elif self.__message == "pbTest":
                self.addLog(f"模型可用!", 1)
        else:
            if self.__message == "ckpt2pb":
                self.addLog(f"转换失败!", 0)
            elif self.__message == "pbTest":
                self.addLog(f"模型不可用!", 0)

        if hasattr(self,"_pythonfile") and os.path.exists(self._pythonfile):
            os.remove(self._pythonfile)

    def addLog(self,log,flag):
        if flag == 1:
            self.textBrowser.append(f"<p style='color:#65CB64;font-size:14px;'>{log}</p>")
        else:
            self.textBrowser.append(f"<p style='color:#D7686D;font-size:14px;'>{log}</p>")







