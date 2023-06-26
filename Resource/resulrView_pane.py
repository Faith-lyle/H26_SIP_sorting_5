#!usr/bin/env python  
# -*- coding:utf-8 _*-
"""
@author:Long.Hou
@file: TestLog_pane.py
@time: 2021/11/09
@email:631176465@qq.com
"""

from Resource.UI import Result_Form_UI
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal


class ResultView(Result_Form_UI.Ui_Form, QWidget):
    test_tunnel_enabled_siganl = pyqtSignal(int,bool)

    def __init__(self,slot):
        super(ResultView, self).__init__()
        self.slot = slot
        self.setupUi(self)
        self.set_slot_title()
        self.cb_checkEnable.setChecked(True)
        self.IsEnabled = True
        self.cb_checkEnable.stateChanged.connect(self.change_form_state)

    def set_slot_title(self):
        self.lb_slotName.setText(f"Slot{self.slot}")

    def set_sn(self, sn):
        self.lb_ShowSN.setText(sn)

    def set_test_state(self, state="wait"):
        if state == "test":
            self.lb_ShowSN.setText("TESTING")
            self.lb_ShowSN.setStyleSheet('font: 75 18pt "Songti SC";background-color: yellow;')
        elif state == "pass":
            self.lb_ShowSN.setText("PASS")
            self.lb_ShowSN.setStyleSheet('font: 75 18pt "Songti SC";background-color: lime;')
        elif state == "fail":
            self.lb_ShowSN.setText("FAIL")
            self.lb_ShowSN.setStyleSheet('font: 75 18pt "Songti SC";background-color: red;')
        else:
            self.lb_ShowSN.setStyleSheet('font: 75 18pt "Songti SC";background-color: rgb(193, 193, 193);')

    def change_form_state(self):
        self.lb_ShowSN.setEnabled(self.cb_checkEnable.isChecked())
        self.IsEnabled = self.cb_checkEnable.isChecked()
        self.test_tunnel_enabled_siganl.emit(self.slot,self.cb_checkEnable.isChecked())

    def set_enabled(self,isenabled):
        self.lb_ShowSN.setEnabled(isenabled)
        # self.cb_checkEnable.setChecked(isenabled)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = ResultView()
    win.resize(400, 300)
    win.setWindowTitle("test")
    win.show()
    sys.exit(app.exec_())
