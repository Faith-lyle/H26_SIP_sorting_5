#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: actionThread.py 
@time: 2022/01/14 
@email:long.hou2@luxshare-ict.com
"""
import time, os
from PyQt5.QtCore import QThread, pyqtSignal
import modbus_tk.defines as cst


class TestThread(QThread):
    test_content_signal = pyqtSignal(str)  # 传递测试结果信号，int:测试项目，int:通道，str：测试值

    def __init__(self):
        super(TestThread, self).__init__()
        self.term = None
        self.func_name = ''

    def set_term(self,term):
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
                        result = "[Receive]:  raster is open!"
                    elif content[0] == 1 :
                        result = "[Receive]:  raster is close!"
                self.test_content_signal.emit(result)
            except Exception as e:
                self.textEdit.append('[Receive]: Error ' + str(e) + "\n")