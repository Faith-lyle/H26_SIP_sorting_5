#!/usr/bin/python3
# -- coding: utf-8 --
# @Author : Long.Hou
# @Email : Long2.Hou@luxshare-ict.com
# @File : mainPanel.py
# @Project : H26_SIP_sorting_5
# @Time : 2023/6/15 08:18
# -------------------------------

import os, csv, sys, time, shutil, configparser, serial
from Resource.Login_pane import LoginUI
from Resource.Setting_pane import SettingUi
from Resource import resulrView_pane, TestItem, TestLog_pane, TestTable_pane
from Resource.UI import main_UI
from Tools import testThread
from Tools import driverThread, driver, mes
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QGridLayout, QMessageBox, QLabel

base_path = os.path.expanduser("~/H26_SIP_Sorting")


class MainPanel(QMainWindow, main_UI.Ui_MainWindow):
    driver_finished_signal = pyqtSignal(bool, list)
    # start_test_signal = pyqtSignal(str)
    reset_signal = pyqtSignal(int)
    edit_text_signal = pyqtSignal(str)
    close_signal = pyqtSignal(dict)

    def __init__(self, config, test_items):
        super(MainPanel, self).__init__()
        self.test_log_view_list = []
        self.result_view_list = []
        self.CT = 0
        self.test_tunnel_enabled_list = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.test_thread_flag = 0
        self.port_dict1 = {"slot1": None, "slot2": None, "slot3": None, "slot4": None, "slot5": None,
                           "slot6": None, "slot7": None, "slot8": None, "slot9": None, "slot10": None, }
        self.serial_port = []
        # self.MES = mes.Mes()
        # self.sava_log_path = ""
        # self.test_plant_path = ""
        self.mes_mode = ""
        self.test_mode = ''
        self.equipment_slot = 1
        self.equipment_port = ''
        self.driver_finish = False
        self.status_label_list = []
        self.config = config
        self.setupUi(self)
        self.test_items = test_items
        self.test_view = TestTable_pane.TestTableView(self.test_items)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout_func)
        self.ui_init()
        self.setup_mes_mode(self.config['Mes']['mesmode'])
        self.pushButton.setVisible(False)
        self.lineEdit.returnPressed.connect(lambda: self.edit_text_signal.emit(self.lineEdit.text()))
        self.statusBar_init()
        self.add_yield_qty('pass',0)
        self.add_yield_qty('fail',0)
        # self.test_table

    def textChanged_slot(self):
        print('')
        # lambda: self.edit_text_signal.emit(self.lineEdit.text())

    def setup_mes_mode(self, mode):
        if mode == 'OnLine':
            self.label_14.setText("On Line")
            self.label_14.setStyleSheet("color: rgb(255, 97, 89);")
            self.label_2.setStyleSheet('color: rgb(255, 97, 89);font: 75 24pt "Arial";')
        elif mode == "OffLine":
            self.label_14.setText("Off Line")
            self.label_14.setStyleSheet("color: rgba(150, 150, 150, 229); background-color:red")
            self.label_2.setStyleSheet('color: rgba(150, 150, 150, 229);font: 75 24pt "Arial";')

    def ui_init(self):
        layout = QHBoxLayout(self.test_table)
        layout.setContentsMargins(0, 0, 1, 1)
        layout.addWidget(self.test_view)
        layout = QHBoxLayout(self.Test_Log1)
        layout.setContentsMargins(0, 0, 1, 1)
        for i in range(5):
            test_log_view = TestLog_pane.TestLogView()
            self.test_log_view_list.append(test_log_view)
            test_log_view.set_slot_title(f"Slot{i + 1} Log")
            layout.addWidget(test_log_view)
        layout = QHBoxLayout(self.test_log2)
        layout.setContentsMargins(0, 0, 1, 1)
        for i in range(5):
            test_log_view = TestLog_pane.TestLogView()
            self.test_log_view_list.append(test_log_view)
            test_log_view.set_slot_title(f"Slot{i + 6} Log")
            layout.addWidget(test_log_view)
        grid_layout = QGridLayout(self.frame_4)
        for i in range(2):
            for m in range(5):
                slot_form = resulrView_pane.ResultView(m + 1 + i * 5)
                slot_form.test_tunnel_enabled_siganl.connect(self.enable_slot)
                self.result_view_list.append(slot_form)
                grid_layout.addWidget(slot_form, i, m, 1, 1)

    def statusBar_init(self):
        self.statusbar.addWidget(QLabel(self, text="  " * 10))
        for i in range(10):
            l1 = QLabel()
            self.status_label_list.append(l1)
            l1.setStyleSheet('margin:0px 6px;background-color:red;min-width:16px;min-height:16px;max-height:16px;'
                             'max-width:16px;border-radius:8px')
            self.statusbar.addWidget(l1)

    def set_status_label_status(self, slot, status):
        if status:
            self.status_label_list[slot].setStyleSheet('margin:0px 6px;background-color:lime;min-width:16px;min-height:'
                                                       '16px;max-height:16px;max-width:16px;border-radius:8px')
        else:
            self.status_label_list[slot].setStyleSheet('margin:0px 6px;background-color:red;min-width:16px;min-height:'
                                                       '16px;max-height:16px;max-width:16px;border-radius:8px')

    def timeout_func(self):
        self.CT += 1
        self.label_4.setText("CT: {}".format(self.CT / 10))

    def result_view_show_status(self, slot, result):
        self.result_view_list[slot - 1].set_test_state(result)

    def add_yield_qty(self, result, qty):
        if result == "pass":
            self.config['init']['passqty']+= qty
            self.label_10.setText('{}'.format(self.config['init']['passqty']))
        else:
            self.config['init']['failqty'] += qty
            self.label_11.setText('{}'.format(self.config['init']['failqty']))
        self.label_9.setText('{}'.format(self.config['init']['passqty']+self.config['init']['failqty']))
        yield1 = int(self.label_10.text()) / int(self.label_9.text()) * 100
        self.label_12.setText('%0.2f' % yield1 + '%')

    def add_value(self, index, column, value, color):
        """
        add value for tabel
        :param index: col
        :param column: column
        :param value: value
        :param color: font color
        :return:
        """
        self.test_view.add_data(index, column, value)
        self.test_view.change_item_font_color(index, column, color)

    def tabel_select_row(self, row):
        """
        select a row of tabel
        :param row:
        :return:
        """
        self.test_view.tableView.selectRow(row)

    def clear_sn_edit_line(self):
        self.lineEdit.clear()

    def tabel_clear_data(self):
        self.test_view.data_model_init()
        self.CT = 0
        for la in self.result_view_list:
            la.set_test_state("wait")

    def enable_slot(self, slot, result):
        self.test_tunnel_enabled_list[slot - 1] = result

    def log_init(self):
        self.headers = ["Slot", "TestTime", 'Test Result']
        self.upper = [" ", "Upper", '']
        self.lower = [" ", "Lower", '']
        with open(self.test_plant_path, "r") as f1:
            rows = f1.readlines()
            for row in range(1, len(rows)):
                heard = rows[row].split(",")[0]
                self.headers.append(heard)
                self.lower.append(rows[row].split(",")[1])
                self.upper.append(rows[row].split(",")[2])

    def on_action_triggered(self):
        self.login = LoginUI(os.path.join(base_path, "Config"))
        self.login.show()
        self.login.Back_signal.connect(lambda: self.show())
        self.login.OK_signal.connect(self.OpenSettingUI)
        self.hide()

    def OpenSettingUI(self, level):
        self.set = SettingUi(os.path.join(base_path, "Config.ini"))
        self.set.show()
        self.set.Back_signal.connect(lambda: self.show())
        self.set.OK_signal.connect(lambda: QMessageBox.information(None, "提示",
                                                                   "请重启软件后配置生效！", QMessageBox.Yes))
        self.hide()

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        self.reset_signal.emit(self.equipment_slot)

    # @pyqtSlot()
    def on_pushButton_clicked1(self):
        if len(self.lineEdit.text().strip()) == self.config['init']['snlenght']:
            print('ok')
            self.start_test_signal.emit(self.lineEdit.text().strip())

            # QMessageBox.critical(None, "\r\n错误", "未连接到PLC，请检查串口设备后重试！\r\n")

    @pyqtSlot()
    def on_action_2_triggered(self):
        QMessageBox.information(self, "帮助",
                                "Version: {}\r\nAnchor: Long.Hou\r\nEmail: Long.hou2@luxshare-ict.com\r\n使用过程"
                                "如有问题，请及时联系作者！".format(self.config['Mes']['sw_version']), QMessageBox.Yes)

    @pyqtSlot()
    def on_actiont_3_triggered(self):
        QApplication.exit()

    @pyqtSlot()
    def closeEvent(self, a0):
        self.close_signal.emit(self.config)

    def show_error(self,msg):
        QMessageBox.information(self, "错误",msg, QMessageBox.Yes)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainPanel()
    win.resize(1500, 800)
    win.setWindowTitle("H26 SIP Sorting")
    win.show()
    sys.exit(app.exec_())
