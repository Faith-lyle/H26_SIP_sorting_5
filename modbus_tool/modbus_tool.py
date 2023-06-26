#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: modbus_tool.py 
@time: 2022/01/12 
@email:long.hou2@luxshare-ict.com
"""
from PyQt5.QtWidgets import QApplication, QWidget, QGroupBox, QPushButton, QLabel, QComboBox, QTextEdit, QCheckBox
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QSize, QRect, QMetaObject, QCoreApplication
import sys, time
from serial.tools.list_ports import comports
import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

"""
上位机手动单步调试工艺流程：
1.旋转开关手动状态下置ON(M305)设备自动复位回一次原点位，回原完成进入上位机手动单步调试状态，
2.置ON(M306)气缸下压
   置ON(M307)气缸上升
   置ON(M308)1#工位旋转启动，M310为1 ， 1#位旋转到位
   置ON(M309)2#工位旋转启动，M311为1 ， 2#位旋转到位

3.置OFF(M305)可退出上位机手动单步调试状态，机台按钮单步调试有效
3.置ON(M501)可屏蔽光栅门
"""


class Ui_widget(object):
    def setupUi(self, widget):
        widget.setObjectName("widget")
        widget.resize(510, 317)
        widget.setMinimumSize(QSize(510, 317))
        widget.setMaximumSize(QSize(562, 358))
        widget.setStyleSheet("\n"
                             "QPushButton:hover{\n"
                             "    background-color: rgb(196, 204, 255);\n"
                             "}\n"
                             "QComboBox:hover{\n"
                             "background-color: rgb(196, 204, 255);\n"
                             "}")
        self.groupBox = QGroupBox(widget)
        self.groupBox.setGeometry(QRect(10, 10, 481, 61))
        self.groupBox.setObjectName("groupBox")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setGeometry(QRect(20, 24, 60, 16))
        self.label_3.setObjectName("label_3")
        self.comboBox = QComboBox(self.groupBox)
        self.comboBox.setGeometry(QRect(55, 24, 191, 22))
        self.comboBox.setObjectName("comboBox")
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setGeometry(QRect(290, 20, 75, 26))
        self.pushButton.setObjectName("pushButton")
        self.pushBautton_2 = QPushButton(self.groupBox)
        self.pushBautton_2.setGeometry(QRect(390, 20, 75, 26))
        self.pushBautton_2.setObjectName("pushBautton_2")
        self.groupBox_2 = QGroupBox(widget)
        self.groupBox_2.setGeometry(QRect(10, 75, 481, 91))
        self.groupBox_2.setObjectName("groupBox_2")
        self.pushButton_2 = QPushButton(self.groupBox_2)
        self.pushButton_2.setGeometry(QRect(20, 20, 95, 26))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QPushButton(self.groupBox_2)
        self.pushButton_3.setGeometry(QRect(140, 20, 95, 26))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QPushButton(self.groupBox_2)
        self.pushButton_4.setGeometry(QRect(270, 20, 95, 26))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_6 = QPushButton(self.groupBox_2)
        self.pushButton_6.setGeometry(QRect(20, 60, 95, 26))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QPushButton(self.groupBox_2)
        self.pushButton_7.setGeometry(QRect(140, 60, 95, 26))
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QPushButton(self.groupBox_2)
        self.pushButton_8.setGeometry(QRect(270, 60, 95, 26))
        self.pushButton_8.setObjectName("pushButton_8")
        self.checkBox = QCheckBox(self.groupBox_2)
        self.checkBox.setGeometry(QRect(380, 20, 85, 21))
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.groupBox_3 = QGroupBox(widget)
        self.groupBox_3.setGeometry(QRect(10, 170, 481, 131))
        self.groupBox_3.setObjectName("groupBox_3")
        self.textEdit = QTextEdit(self.groupBox_3)
        self.textEdit.setGeometry(QRect(10, 20, 461, 101))
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")

        self.retranslateUi(widget)
        QMetaObject.connectSlotsByName(widget)

    def retranslateUi(self, widget):
        _translate = QCoreApplication.translate
        widget.setWindowTitle(_translate("widget", "Tool"))
        self.groupBox.setTitle(_translate("widget", "配置设置"))
        self.label_3.setText(_translate("widget", "串口："))
        self.pushButton.setText(_translate("widget", "连接"))
        self.pushBautton_2.setText(_translate("widget", "断开"))
        self.groupBox_2.setTitle(_translate("widget", "Command"))
        self.pushButton_2.setText(_translate("widget", "整机复位"))
        self.pushButton_3.setText(_translate("widget", "气缸下压"))
        self.pushButton_4.setText(_translate("widget", "1#治具旋转"))
        self.pushButton_6.setText(_translate("widget", "退出单步调试"))
        self.pushButton_7.setText(_translate("widget", "气缸上升"))
        self.pushButton_8.setText(_translate("widget", "2#治具旋转"))
        self.checkBox.setText(_translate("widget", "开启光栅"))
        self.groupBox_3.setTitle(_translate("widget", "Receive"))


class Application(QWidget, Ui_widget):
    def __init__(self):
        super(Application, self).__init__()
        self.setupUi(self)
        self.read_port()
        self.term = None
        self.test_thread = TestThread()
        self.test_thread.test_content_signal.connect(self.append_content)
        self.test_thread.raster_signal.connect(self.set_checkBox_states)
        # self.checkBox.clicked

    def set_checkBox_states(self, result):
        self.checkBox.setChecked(result)

    def append_content(self, content):
        self.textEdit.append(time.strftime("%H:%M:%S  ") + content)

    def read_port(self):
        ports = [i.name for i in list(comports())]
        self.comboBox.addItems(ports)

    @pyqtSlot(bool)
    def on_checkBox_clicked(self, result):
        if self.test_thread.term:
            if result:
                self.test_thread.set_func_name('open_raster')
                self.test_thread.start()
            else:
                self.test_thread.set_func_name('close_raster')
                self.test_thread.start()

    @pyqtSlot()
    def on_pushButton_clicked(self):
        # print('连接')
        port = '/dev/' + self.comboBox.currentText()
        try:
            self.term = modbus_rtu.RtuMaster(
                serial.Serial(port=port, baudrate=19200, bytesize=8, parity="E"
                              , stopbits=1))
            self.term.set_verbose(True)
            self.term.set_timeout(1)
            self.label_11.setText(port)
            self.test_thread.set_term(self.term)
            self.append_content('[Open port]: Successful!')
        except Exception as e:
            self.label_11.setText("None")
            self.append_content('[Open port]: Error ' + str(e))
            return
        if self.test_thread.term:
            self.test_thread.set_func_name('read_raster')
            self.test_thread.start()

    @pyqtSlot()
    def on_pushBautton_2_clicked(self):
        if self.term:
            try:
                self.term.close()
                self.term = None
                self.test_thread.term = None
                self.label_11.setText("None")
                self.append_content('[Close port]: Successful!\n')
            except Exception as e:
                self.term = None
                self.test_thread.term = None
                self.label_11.setText("None")
                self.append_content('[Close port]: Error ' + str(e) + "\n")

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        # 整机复位
        if self.test_thread.term:
            self.test_thread.set_func_name('set_debug_mode')
            self.test_thread.start()

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        # 气缸下压
        if self.test_thread.term:
            self.test_thread.set_func_name('cylinder_press')
            self.test_thread.start()

    @pyqtSlot()
    def on_pushButton_4_clicked(self):
        # 1#治具旋转
        if self.test_thread.term:
            self.test_thread.set_func_name('rotary_driver_1')
            self.test_thread.start()

    @pyqtSlot()
    def on_pushButton_6_clicked(self):
        # 1#治具旋转
        if self.test_thread.term:
            self.test_thread.set_func_name('exit_debug_mode')
            self.test_thread.start()

    @pyqtSlot()
    def on_pushButton_7_clicked(self):
        # 1#治具旋转
        if self.test_thread.term:
            self.test_thread.set_func_name('cylinder_rise')
            self.test_thread.start()

    @pyqtSlot()
    def on_pushButton_8_clicked(self):
        # 2#治具旋转
        if self.test_thread.term:
            self.test_thread.set_func_name('rotary_driver_2')
            self.test_thread.start()


class TestThread(QThread):
    test_content_signal = pyqtSignal(str)
    raster_signal = pyqtSignal(bool)

    def __init__(self):
        super(TestThread, self).__init__()
        self.term = None
        self.func_name = ''

    def set_term(self, term):
        self.term = term

    def set_func_name(self, func_name):
        self.func_name = func_name

    def run(self):
        if self.func_name == "rotary_driver_1":
            self.rotary_driver_1()
        elif self.func_name == 'rotary_driver_2':
            self.rotary_driver_2()
        elif self.func_name == 'cylinder_rise':
            self.cylinder_rise()
        elif self.func_name == 'cylinder_press':
            self.cylinder_press()
        elif self.func_name == 'set_debug_mode':
            self.set_debug_mode()
        elif self.func_name == 'exit_debug_mode':
            self.exit_debug_mode()
        elif self.func_name == 'open_raster':
            self.open_raster()
        elif self.func_name == 'close_raster':
            self.close_raster()
        elif self.func_name == 'read_raster':
            self.read_raster()

    def rotary_driver_1(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 308, output_value=1)
                if len(content) == 2:
                    if content[0] == 308 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = "[Receive]: Error timeout!"
                                break
                            text = self.term.execute(1, cst.READ_COILS, 310, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = "[Receive]: 1# driver rota successful!"
                                break
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def rotary_driver_2(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 309, output_value=1)
                if len(content) == 2:
                    if content[0] == 309 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = "[Receive]: Error timeout!"
                                break
                            text = self.term.execute(1, cst.READ_COILS, 311, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = "[Receive]: 2# driver rota successful!"
                                break
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def cylinder_rise(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 306, output_value=1)
                if len(content) == 2:
                    if content[0] == 306 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = "[Receive]: Error timeout!"
                                break
                            text = self.term.execute(1, cst.READ_COILS, 312, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = "[Receive]: cylinder_rise successful!"
                                break
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def cylinder_press(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 307, output_value=1)
                if len(content) == 2:
                    if content[0] == 307 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = "[Receive]: Error timeout!"
                                break
                            text = self.term.execute(1, cst.READ_COILS, 312, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = "[Receive]: cylinder_press successful!"
                                break
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def set_debug_mode(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 305, output_value=1)
                if len(content) == 2:
                    if content[0] == 305 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = "[Receive]: Error timeout!"
                                break
                            text = self.term.execute(1, cst.READ_COILS, 350, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = "[Receive]: set_debug_mode successful!"
                                break
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def exit_debug_mode(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 305, output_value=0)
                if len(content) == 2:
                    if content[0] == 305 and content[1] == 0:
                        result = "[Receive]: exit_debug_mode successful!"
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def open_raster(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 501, output_value=0)
                if len(content) == 2:
                    if content[0] == 501 and content[1] == 0:
                        result = "[Receive]: raster open successful!"
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def close_raster(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.WRITE_SINGLE_COIL, 501, output_value=1)
                if len(content) == 2:
                    if content[0] == 501 and content[1] == 0xff00:
                        result = "[Receive]: raster close successful!"
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")

    def read_raster(self):
        result = "[Receive]: Status code error！"
        if self.term:
            try:
                content = self.term.execute(1, cst.READ_COILS, 501, 1)
                if len(content) == 1:
                    if content[0] == 0:
                        self.raster_signal.emit(True)
                        result = "[Receive]:  raster is open!"
                    elif content[0] == 1:
                        self.raster_signal.emit(False)
                        result = "[Receive]:  raster is close!"
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Application()
    # win.resize(1500, 800)
    win.setWindowTitle("Tool")
    win.show()
    sys.exit(app.exec_())
