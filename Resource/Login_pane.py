# _*_ coding: UTF-8 _*_
"""
@author:A002832
@file:Login_pane.py
@time:2021/09/09
"""
import sys
import hashlib
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication
from Resource.UI import Login_UI


def CaculeKey(psw):
    hash = hashlib.md5()
    hash.update(bytes(psw, encoding='utf-8'))
    return hash.hexdigest()


class LoginUI(Login_UI.Ui_Form, QtWidgets.QWidget):
    OK_signal = pyqtSignal(str)
    Back_signal = pyqtSignal()

    def __init__(self,config_file):
        super(LoginUI, self).__init__()
        self.config_file = config_file
        self.login_mode = None
        self.setupUi(self)

    def closeEvent(self, event):
        super(LoginUI, self).closeEvent(event)
        if not self.login_mode:
            self.Back_signal.emit()

    @pyqtSlot()
    def on_Edt_Password_returnPressed(self):
        if self.login(self.Cbb_Username.currentText(), self.Edt_Password.text()):
            self.OK_signal.emit(self.login_mode)
            self.close()
            print("password ok")
        else:
            QtWidgets.QMessageBox.information(self, "提示！", "\n密码错误，请重试！\r\n", QtWidgets.QMessageBox.Yes)
            print("password ng")

    @pyqtSlot()
    def on_Bt_OK_clicked(self):
        if self.login(self.Cbb_Username.currentText(), self.Edt_Password.text()):
            self.OK_signal.emit(self.login_mode)
            self.close()
            print("password ok")
        else:
            QtWidgets.QMessageBox.information(self, "提示！", "\n密码错误，请重试！\r\n", QtWidgets.QMessageBox.Yes)
            print("password ng")

    @pyqtSlot()
    def on_Btn_Cancel_clicked(self):
        # self.Back_signal.emit()
        self.close()

    def login(self, userName, passWord):
        if userName == "Operator":
            if passWord == "123456":
                self.login_mode = "Operator"
                return True
        if userName == "Engineer":
            with open(self.config_file) as f:
                key = f.read()
            # print(CaculeKey(passWord))
            if CaculeKey(passWord) == key:

                self.login_mode = "Engineer"
                return True
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = LoginUI()
    MainWindow.show()
    sys.exit(app.exec_())
