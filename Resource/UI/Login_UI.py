# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Setting.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        Form.resize(352, 234)
        Form.setMaximumSize(QtCore.QSize(352, 234))
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(50, 80, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.label.setFont(font)
        self.label.setStyleSheet("font: 75 11pt \"Arial\";")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(50, 120, 81, 20))
        self.label_2.setStyleSheet("font: 75 11pt \"Arial\";")
        self.label_2.setObjectName("label_2")
        self.Bt_OK = QtWidgets.QPushButton(Form)
        self.Bt_OK.setGeometry(QtCore.QRect(50, 170, 90, 28))
        self.Bt_OK.setStyleSheet("font: 87 12pt \"Arial\";")
        self.Bt_OK.setObjectName("Bt_OK")
        self.Btn_Cancel = QtWidgets.QPushButton(Form)
        self.Btn_Cancel.setGeometry(QtCore.QRect(200, 170, 90, 28))
        self.Btn_Cancel.setStyleSheet("font: 87 12pt \"Arial\";")
        self.Btn_Cancel.setObjectName("Btn_Cancel")
        self.Cbb_Username = QtWidgets.QComboBox(Form)
        self.Cbb_Username.setGeometry(QtCore.QRect(140, 80, 150, 20))
        self.Cbb_Username.setStyleSheet("font: 75 11pt \"Arial\";")
        self.Cbb_Username.setObjectName("Cbb_Username")
        self.Cbb_Username.addItem("")
        self.Cbb_Username.addItem("")
        self.Edt_Password = QtWidgets.QLineEdit(Form)
        self.Edt_Password.setGeometry(QtCore.QRect(140, 120, 150, 20))
        self.Edt_Password.setStyleSheet("font: 75 11pt \"Arial\";")
        self.Edt_Password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Edt_Password.setObjectName("Edt_Password")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(20, 35, 311, 21))
        self.label_3.setStyleSheet("font: 87 16pt \"Arial\";\n"
"color: rgb(0, 0, 255);")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Longin"))
        self.label.setText(_translate("Form", "UserName:"))
        self.label_2.setText(_translate("Form", "Password"))
        self.Bt_OK.setText(_translate("Form", "确认"))
        self.Btn_Cancel.setText(_translate("Form", "取消"))
        self.Cbb_Username.setItemText(0, _translate("Form", "Engineer"))
        self.Cbb_Username.setItemText(1, _translate("Form", "Operator"))
        self.label_3.setText(_translate("Form", "Welcome to Load Detection"))
