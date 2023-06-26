# _*_ coding: UTF-8 _*_
"""
@author:A002832
@file:Setting_pane.py
@time:2021/09/09
"""
import sys
import configparser
import serial.tools.list_ports
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMessageBox
from Resource.UI import Setting_UI
from Resource import modbus_tool


class SettingUi(Setting_UI.Ui_Form, QtWidgets.QWidget):
    OK_signal = pyqtSignal()
    Back_signal = pyqtSignal()

    def __init__(self, config_path):
        super(SettingUi, self).__init__()
        self.IsSave = False
        self.port1_combobox_list = []
        self.config_path = config_path
        self.setupUi(self)
        self.Btn_init()
        self.Btn_Port1Setting.setStyleSheet("background-color: rgb(85, 255, 255);border-style:none")
        self.stackedWidget.setCurrentIndex(0)
        self.tunnel_Port_Init(self.tableWidget_2,self.port1_combobox_list)
        self.read_config()
        self.comboBox.setStyleSheet("color:black;background-color:white")
        self.driver_manual_setting_init()

    def tunnel_Port_Init(self,widget,port_combobox_list):
        widget.setColumnWidth(0, 50)
        port_list = [i.name for i in serial.tools.list_ports.comports()]
        self.comboBox.addItems(port_list)
        for num in range(widget.rowCount()):
            comboxob = QtWidgets.QComboBox()
            port_combobox_list.append(comboxob)
            comboxob.setStyleSheet('border-style:none;font: 87 11pt "Arial";selection-color: rgb(179, 215, 255);')
            comboxob.addItems(port_list)
            comboxob.setEditable(False)
            comboxob.setCurrentText(port_list[0])
            widget.setCellWidget(num, 2, comboxob)
            for i in range(2):
                item = widget.item(num, i)
                item.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                # item.setEditable(False)

    def driver_manual_setting_init(self):
        layout = QtWidgets.QHBoxLayout(self.page_7)
        app = modbus_tool.Application(self.page_7)
        layout.addWidget(app)
        app.show()
        # app.show()

    def Btn_init(self):
        self.Btn_Port1Setting.setStyleSheet("background-color: rgb(225, 237, 255);border-style:none")
        self.Btn_Port2Setting.setStyleSheet("background-color: rgb(225, 237, 255);border-style:none")
        self.Btn_itemSetting.setStyleSheet("background-color: rgb(225, 237, 255);border-style:none")
        self.Btn_modeSetting.setStyleSheet("background-color: rgb(225, 237, 255);border-style:none")

    def read_config(self):
        if not os.path.exists(self.config_path):
            QMessageBox.critical(self, "错误", "未找到测试文档，请检查配置文件", QMessageBox.Yes)
            exit()
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path, encoding="utf-8")
        for i in range(len(self.port1_combobox_list)):
            self.port1_combobox_list[i].setCurrentText(config_parser.get("PORT1", "slot{}".format(i + 1)))
        self.comboBox.setCurrentText(config_parser.get("DriverConfig", "Port"))
        self.comboBox_2.setCurrentText(config_parser.get("DriverConfig", "Baudrate"))
        self.comboBox_3.setCurrentText(config_parser.get("DriverConfig", "DataBit"))
        self.comboBox_4.setCurrentText(config_parser.get("DriverConfig", "StopBit"))
        self.comboBox_5.setCurrentText(config_parser.get("DriverConfig", "Parity"))
        self.lineEdit.setText(os.path.expanduser(config_parser.get("Path", "logpath")))
        self.lineEdit_2.setText(os.path.expanduser(config_parser.get("Path", "testplanpath")))

    def save_config(self):
        if not os.path.exists(self.config_path):
            QMessageBox.critical(self, "错误", "未找到测试文档，请检查配置文件", QMessageBox.Yes)
            exit()
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path, encoding="utf-8")
        for i in range(len(self.port1_combobox_list)):
            config_parser.set("PORT1", "slot{}".format(i + 1), self.port1_combobox_list[i].currentText())
        config_parser.set("Path", "logpath", self.lineEdit.text())
        config_parser.set("Path", "testplanpath", self.lineEdit_2.text())
        config_parser.set("DriverConfig", "Port", self.comboBox.currentText())
        config_parser.set("DriverConfig", "Baudrate", self.comboBox_2.currentText())
        config_parser.set("DriverConfig", "DataBit", self.comboBox_3.currentText())
        config_parser.set("DriverConfig", "StopBit", self.comboBox_4.currentText())
        config_parser.set("DriverConfig", "Parity", self.comboBox_5.currentText())
        if self.MesOnline.isChecked():
            config_parser.set("Mes", "mesmode", "OnLine")
        elif self.MesUnline.isChecked():
            config_parser.set("Mes", "mesmode", "OffLine")
        elif self.radioButton_3.isChecked():
            config_parser.set("Mes", "mesmode", "OffLine")
        if self.radioButton_5.isChecked():
            config_parser.set("Mes", "testmode", "FailContinue")
        elif self.radioButton_4.isChecked():
            config_parser.set("Mes", "testmode", "FailStop")
        with open(self.config_path, "w+", encoding="utf-8") as f:
            config_parser.write(f)
        print("saveOK")

    def closeEvent(self, event):
        super(SettingUi, self).closeEvent(event)
        if not self.IsSave:
            self.Back_signal.emit()

    @pyqtSlot()
    def on_logBrowser_clicked(self):
        fileDir = QtWidgets.QFileDialog.getExistingDirectory(self, "选择文件夹", ".")
        if fileDir:
            self.lineEdit.setText(fileDir)

    @pyqtSlot()
    def on_testPlanBrowser_clicked(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "选择TestPlant", "./", "CSV Files(*.csv);;ALL Files(*.*)")
        if file[0]:
            self.lineEdit_2.setText(file[0])

    @pyqtSlot()
    def on_Btn_Port1Setting_clicked(self):
        self.Btn_init()
        self.Btn_Port1Setting.setStyleSheet("background-color: rgb(85, 255, 255);border-style:none")
        self.stackedWidget.setCurrentIndex(0)

    @pyqtSlot()
    def on_Btn_Port2Setting_clicked(self):
        self.Btn_init()
        self.Btn_Port2Setting.setStyleSheet("background-color: rgb(85, 255, 255);border-style:none")
        self.stackedWidget.setCurrentIndex(3)

    @pyqtSlot()
    def on_Btn_itemSetting_clicked(self):
        self.Btn_init()
        self.Btn_itemSetting.setStyleSheet("background-color: rgb(85, 255, 255);border-style:none")
        self.stackedWidget.setCurrentIndex(1)

    @pyqtSlot()
    def on_Btn_Cancel_clicked(self):
        self.close()

    @pyqtSlot()
    def on_Btn_OK_clicked(self):
        self.OK_signal.emit()
        self.save_config()
        self.IsSave = True
        self.close()

    @pyqtSlot()
    def on_Btn_modeSetting_clicked(self):
        self.Btn_init()
        self.Btn_modeSetting.setStyleSheet("background-color: rgb(85, 255, 255);border-style:none")
        self.stackedWidget.setCurrentIndex(2)


if __name__ == '__main__':
    # from 界面转换.TestItem import TestItem

    app = QApplication(sys.argv)
    MainWindow = SettingUi("../config.ini")
    MainWindow.show()
    sys.exit(app.exec_())
