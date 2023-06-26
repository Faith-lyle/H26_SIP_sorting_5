#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: UI_Main.py 
@time: 2021/11/09 
@email:631176465@qq.com
"""
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
VERSION = "1.1.5"

def ReadTestPlanFile(file_path):
    print(file_path)
    Test_Items = []
    if not os.path.exists(file_path):
        QMessageBox.critical(None, "错误", "未找到测试文档，请检查配置文件", QMessageBox.Yes)
        exit()
    with open(file_path, "r") as f:
        reader = list(csv.reader(f))
        for text in reader[1:]:
            map1 = dict(zip(reader[0], text))
            # print(**map1)
            item = TestItem.TestItem(**map1)
            Test_Items.append(item)
    return Test_Items


class Application(QMainWindow, main_UI.Ui_MainWindow):
    driver_finished_signal = pyqtSignal(bool, list)

    def __init__(self):
        super(Application, self).__init__()
        self.test_log_view_list = []
        self.result_view_list = []
        self.CT = 0
        self.test_tunnel_enabled_list = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.test_thread_flag = 0
        self.port_dict1 = {"slot1": None, "slot2": None, "slot3": None, "slot4": None, "slot5": None,
                           "slot6": None, "slot7": None, "slot8": None, "slot9": None, "slot10": None, }
        self.serial_port = []
        self.MES = mes.Mes()
        self.sava_log_path = ""
        self.test_plant_path = ""
        self.mes_mode = ""
        self.test_mode = ''
        self.equipment_slot = 1
        self.equipment_port = ''
        self.driver_finish = False
        self.config = configparser.ConfigParser()
        self.read_config()
        self.setupUi(self)
        self.setup_mes_mode()
        self.test_items = ReadTestPlanFile(self.test_plant_path)
        self.test_view = TestTable_pane.TestTableView(self.test_items)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout_func)
        self.timer_read = QTimer(self)
        self.timer_read.timeout.connect(self.read_log)
        self.ui_init()
        self.log_init()
        self.test_log1.setCurrentIndex(0)
        self.statusBar_init()
        self.t2 = driverThread.DriverThread(port=self.equipment_port, slot=self.equipment_slot)
        self.t2.setParent(self)
        self.t2.finished_signal.connect(self.response_driver_finished_signal)
        self.test_thread_list = []
        self.create_test_thread()
        self.pushButton.setVisible(False)
        self.lineEdit.editingFinished.connect(self.on_pushButton_clicked)

    def read_log(self):
        if self.driver_finish:
            for i in range(1, 11):
                if self.test_tunnel_enabled_list[i - 1]:
                    with open(os.path.expanduser(f"~/H26_SIP_Sorting/slot{i}.txt")) as f:
                        self.test_log_view_list[i - 1].set_text(f.read())
                    self.test_log_view_list[i - 1].set_flag_to_end()
                else:
                    self.test_log_view_list[i - 1].set_text('')

    def setup_mes_mode(self):
        if self.mes_mode == 'OnLine':
            self.label_14.setText("On Line")
            self.label_14.setStyleSheet("color: rgb(255, 97, 89);")
            self.label_2.setStyleSheet('color: rgb(255, 97, 89);font: 75 24pt "Arial";')
        elif self.mes_mode == "OffLine":
            self.label_14.setText("Off Line")
            self.label_14.setStyleSheet("color: rgba(150, 150, 150, 229);")
            self.label_2.setStyleSheet('color: rgba(150, 150, 150, 229);font: 75 24pt "Arial";')
        elif self.mes_mode == "DeBug":
            self.label_14.setText("DeBug")
            self.label_14.setStyleSheet("color: rgba(150, 150, 150, 229);")
            self.label_2.setStyleSheet('color: rgba(150, 150, 150, 229);font: 75 24pt "Arial";')

    def read_config(self):
        config_path = os.path.join(base_path, 'Config.ini')
        if os.path.exists(config_path):
            self.config.read(config_path)
        else:
            QMessageBox.critical(None, "\r\n错误", "未找到配置文件，请检查文件后重试！\r\n")
            exit(0)
        for key in self.port_dict1.keys():
            self.port_dict1[key] = "/dev/" + self.config.get("PORT1", key)
            try:
                term = serial.Serial(port=self.port_dict1[key], baudrate=921600, timeout=3)
                term.close()

            except:
                term = None
            self.serial_port.append(term)
        self.equipment_port_name = "/dev/" + self.config.get("DriverConfig", 'port')
        try:
            self.equipment_port = driver.Driver(portName=self.equipment_port_name)
        except:
            QMessageBox.critical(None, "\r\n错误", "未连接到PLC，请检查串口设备后重试！\r\n")
            # exit(0)
        self.test_plant_path = os.path.expanduser(self.config.get("Path", "testplanpath"))
        self.sava_log_path = os.path.expanduser(self.config.get("Path", "logpath"))
        self.mes_mode = self.config.get("Mode", "mesmode")
        self.test_mode = self.config.get("Mode", "testmode")

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
                slot_form.test_tunnel_enabled_siganl.connect(self.response_test_tunnel_enabled_siganl)
                self.result_view_list.append(slot_form)
                grid_layout.addWidget(slot_form, i, m, 1, 1)

    def statusBar_init(self):
        self.statusbar.addWidget(QLabel(self, text="  " * 10))
        for i in range(10):
            l1 = QLabel()
            l1.setStyleSheet(
                'margin:0px 6px;background-color:red;min-width:16px;min-height:16px;max-height:16px;max-width:16px;border-radius:8px')
            if self.serial_port[i]:
                l1.setStyleSheet(
                    'margin:0px 6px;background-color:lime;min-width:16px;min-height:16px;max-height:16px;max-width:16px;border-radius:8px')
            self.statusbar.addWidget(l1)

    def timeout_func(self):
        self.CT += 1
        self.label_4.setText("CT: {}".format(self.CT / 10))

    def response_start_signal(self, slot):
        self.result_view_list[slot - 1].set_test_state("test")

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

    def write_csv(self, base_path, result_list):
        file_path = os.path.join(base_path, f"H26_SIP_Sortong_{time.strftime('%Y-%m-%d')}.csv")
        if not os.path.exists(file_path):
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                writer.writerow(self.lower)
                writer.writerow(self.upper)
                writer.writerow(result_list)
        else:
            with open(file_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(result_list)

    def set_yield_form(self, result):
        self.label_9.setText('{}'.format(int(self.label_9.text()) + 1))
        if result == "pass":
            self.label_10.setText('{}'.format(int(self.label_10.text()) + 1))
        else:
            self.label_11.setText('{}'.format(int(self.label_11.text()) + 1))
        yield1 = int(self.label_10.text()) / int(self.label_9.text()) * 100
        self.label_12.setText('%0.2f' % yield1 + '%')

    def update_result_to_mes(self, slot, result, result_list):
        length = self.headers.index("Ear Reset")
        if len(result_list) > length:
            if self.mes_mode == "OnLine":
                if result == "pass":
                    fail_info = ''
                else:
                    fail_info = f'TestItem:{self.headers[len(result_list) - 1]};TestValue:{result_list[len(result_list) - 1]};' \
                                f'TestUpper:{self.upper[len(result_list) - 1]};TestLower:{self.lower[len(result_list) - 1]}'
                if slot > 9:
                    sn = '{}{}'.format(self.sn, slot)
                else:
                    sn = '{}0{}'.format(self.sn, slot)
                data = {"result": str(result).upper(), 'audio_mode': '0', 'start_time': result_list[1],
                        'stop_time': time.strftime("%H:%M:%S"),
                        'sn': sn, 'fixture_id': slot, 'test_head_id': slot, 'list_of_failing_tests': fail_info,
                        'failure_message': fail_info}
                if not self.MES.update_test_value_to_mes(data):
                    QMessageBox.information(self, "information", 'Update data to MES failed, please tay again!')

    def response_end_signal(self, slot, result, result_list):
        self.lineEdit.setText("")
        self.update_result_to_mes(slot, result, result_list)
        self.result_view_list[slot - 1].set_test_state(result)
        self.test_thread_flag -= 1
        self.set_yield_form(result)
        self.write_csv(self.sava_log_path, result_list)

        log_dir = os.path.join(self.sava_log_path, time.strftime("%Y-%m-%d"))
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        shutil.copy(os.path.join(base_path, f"slot{slot}.txt"),
                    os.path.join(log_dir, f"H26_SIP_Sortong_Slot_{slot}_{time.strftime('%H-%M-%S')}.txt"))
        if self.test_thread_flag == 0:
            self.driver_finish = False
            # t2.set_slot(self.equipment_slot)
            self.t2.set_func_name("Equipment_reset")
            self.t2.start()
            self.equipment_slot = 2 if self.equipment_slot == 1 else 1
            self.timer.stop()
            self.timer_read.stop()
            self.timeout_func()
            self.read_log()
            self.pushButton.setEnabled(True)

    def response_test_content_signal(self, y, x, value):
        self.test_view.add_data(row=y, col=x, value=value)

    def response_item_test_result_signal(self, y, x, color):
        self.test_view.change_item_font_color(row=y, col=x, color=color)

    def response_test_tunnel_enabled_siganl(self, slot, result):

        self.test_tunnel_enabled_list[slot - 1] = result

    def response_select_row_signal(self, row):
        self.test_view.tableView.selectRow(row)

    def start_test_allui_resrt(self):
        self.test_view.data_model_init()
        self.CT = 0
        for la in self.result_view_list:
            la.set_test_state("wait")

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

    def response_driver_finished_signal(self, flag, result):
        self.driver_finished_signal.emit(flag, result)
        self.driver_finish = True

    def create_test_thread(self):
        for i in range(1, 11):
            t1 = testThread.TestThread(slot=i, port=self.serial_port[i - 1], test_items=self.test_items)
            t1.setParent(self)
            t1.test_start_signal.connect(self.response_start_signal)
            t1.test_end_signal.connect(self.response_end_signal)
            t1.item_test_result_signal.connect(self.response_item_test_result_signal)
            t1.test_content_signal.connect(self.response_test_content_signal)
            t1.test_select_row_signal.connect(self.response_select_row_signal)
            self.driver_finished_signal.connect(t1.set_wait_old_thread_finished_flag)
            self.test_thread_list.append(t1)

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        if self.equipment_slot == 1:
            self.t2.set_slot(1)
            self.t2.set_func_name("Reset")
            self.t2.start()
            self.equipment_slot = 2
        elif self.equipment_slot == 2:
            if self.equipment_port:
                self.t2.set_slot(2)
                self.t2.set_func_name("Reset")
                self.t2.start()
                self.equipment_slot = 1

    @pyqtSlot()
    def on_pushButton_clicked(self):
        if len(self.lineEdit.text()) != 15:
            print('sn<15')
            return
        test_tunnel_enabled_list = self.test_tunnel_enabled_list.copy()
        # copy_list = [1,6,2,7,3,8,4,9,5,10]
        self.sn = self.lineEdit.text()
        self.pushButton.setEnabled(False)
        if self.mes_mode == "OnLine":
            result, msg = self.MES.get_SIP_X_num(sn=self.sn)
            if result:
                for i in msg:
                    test_tunnel_enabled_list[i - 1] = 0
                    self.update_result_to_mes(i, 'pass',
                                              ['', time.strftime("%H:%M:%S"), "", '', '', '', '', '', '', ''])
                for n, m in enumerate(test_tunnel_enabled_list):
                    if m:
                        if n < 9:
                            result, msg = self.MES.check_process(sn='{}0{}'.format(self.sn, n + 1))
                        else:
                            result, msg = self.MES.check_process(sn='{}{}'.format(self.sn, n + 1))
                        if not result:
                            QMessageBox.critical(self, "Error", msg)
                            self.pushButton.setEnabled(True)
                            return
            else:
                QMessageBox.critical(self, "Error", msg)
                self.pushButton.setEnabled(True)
                return


        self.start_test_allui_resrt()
        self.timer.start(100)
        self.t2.set_func_name("Equipment_init")
        self.t2.set_slot(self.equipment_slot)
        self.t2.start()
        for i in range(1, 11):
            if test_tunnel_enabled_list[i - 1]:
                self.result_view_list[i - 1].set_enabled(True)
                self.test_thread_list[i - 1].config_init()
                if self.test_mode == "FailStop":
                    self.test_thread_list[i - 1].set_continue_flag(False)
                else:
                    self.test_thread_list[i - 1].set_continue_flag(True)
                self.test_thread_list[i - 1].start()
                self.test_thread_flag += 1

        # QMessageBox.information(self,"slot",str(self.equipment_slot))

    @pyqtSlot()
    def on_action_2_triggered(self):
        QMessageBox.information(self, "帮助",
                                "Version: {}\r\nAnchor: Long.Hou\r\nEmail: Long.hou2@luxshare-ict.com\r\n使用过程"
                                "如有问题，请及时联系作者！".format(VERSION), QMessageBox.Yes)

    @pyqtSlot()
    def on_actiont_3_triggered(self):
        QApplication.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Application()
    win.resize(1500, 800)
    win.setWindowTitle("H26 SIP Sorting")
    win.show()
    sys.exit(app.exec_())
