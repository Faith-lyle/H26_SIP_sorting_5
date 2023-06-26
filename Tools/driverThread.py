#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: driverThread.py 
@time: 2022/01/18 
@email:long.hou2@luxshare-ict.com
"""
import time

from PyQt5.QtCore import QThread, pyqtSignal
from Tools import wait_event


class DriverThread(QThread):
    finished_signal = pyqtSignal(int, bool)

    def __init__(self, port, slot):
        super(DriverThread, self).__init__()
        # self.term = None
        self.port = port
        self.func_name = ''
        self.slot = slot
        self.result = [False, "FAIL"]

    def set_func_name(self, func_name):
        self.func_name = func_name

    def set_slot(self, slot):
        self.slot = slot

    def run(self):
        if self.func_name == "Equipment_init":
            try:
                if self.port.driver_start_test(self.slot):
                    if self.port.driver_wait_done(self.slot):
                        result = True
                        self.finished_signal.emit(1,result)
                        wait_event.set()
            except Exception as e:
                print(e)
        elif self.func_name == 'Equipment_reset':
            try:
                term = self.port
                if term.driver_reset(self.slot):
                    result = True
                    self.finished_signal.emit(1,result)
            except Exception as e:
                print(e)
        elif self.func_name == 'Reset':
            try:
                self.port.driver_start_test(self.slot)
                if self.port.driver_wait_done(self.slot):
                    self.port.driver_reset(self.slot)
            except Exception as e:
                print(e)
        # print(self.result)
