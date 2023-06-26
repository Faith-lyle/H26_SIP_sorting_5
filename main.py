#!/usr/bin/python3
# -- coding: utf-8 --
# @Author : Long.Hou
# @Email : Long2.Hou@luxshare-ict.com
# @File : main.py
# @Project : H26_SIP_sorting_5
# @Time : 2023/6/15 08:17
# -------------------------------
import os, csv, sys, time, shutil, configparser, serial
import threading
import Tools.testThread
from Resource import TestItem
from Resource.mainPanel import MainPanel
from Tools.serialPort import SerialPort
from Tools import driverThread, driver, mes
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QGridLayout, QMessageBox, QLabel

BASE_DIR = os.path.expanduser("~/H26_SIP_Sorting")
VERSION = '2.2.0'


def read_testPlan(file_path):
    Test_Items = []
    if not os.path.exists(file_path):
        QMessageBox.critical(None, "错误", "未找到TestPlan文件，请检查配置文件", QMessageBox.Yes)
        exit()
    with open(file_path, "r") as f:
        reader = list(csv.reader(f))
        for text in reader[1:]:
            map1 = dict(zip(reader[0], text))
            # print(**map1)
            item = TestItem.TestItem(**map1)
            Test_Items.append(item)
    return Test_Items


def save_ini(file):
    pass


def read_int(file):
    if not os.path.exists(file):
        QMessageBox.critical(None, "错误", "未找到Config.ini文件，请检查配置文件", QMessageBox.Yes)
        exit()
    config = configparser.ConfigParser()
    config.read(file)
    data = {}
    for session in config.sections():
        data[session] = {}
        for key in config.options(session):
            try:
                value = int(config.get(session, key))
            except ValueError:
                value = config.get(session, key)
            data[session][key] = value

    # print(data)
    data['Mes']['sw_version'] = VERSION
    return data


is_Testing = False
test_thread_flag = 0


def response_main_start_test_signal_slot(sn):
    global is_Testing, test_thread_flag
    if len(sn) != config_ini['init']['snlenght']:
        # print('error')
        win.show_error("SN 长度错误，限制长度为{}".format(config_ini['init']['snlenght']))
        # QMessageBox.critical(None,'错误',"SN 长度错误，限制长度为{}".format(config_ini['init']['snlenght']),QMessageBox.Yes)
        return
    if is_Testing:
        return
    # print('run')
    win.clear_sn_edit_line()
    test_thread_flag = 0
    is_Testing = True
    for x in range(10):
        win.result_view_list[x].set_enabled(False)
    test_tunnel_enabled_list = win.test_tunnel_enabled_list.copy()
    # check the X-board
    result, msg = MES.get_SIP_X_num(sn=sn)
    if result:
        for i in msg:
            test_tunnel_enabled_list[i - 1] = 0
            # win.result_view_list[i-1].set_enabled(True)
    else:
        QMessageBox.critical(None, "Error", msg)
        is_Testing = False
        return
    if config_ini['Mes']['mesmode'] == "OnLine":
        # check the process for no x-board
        for n, m in enumerate(test_tunnel_enabled_list):
            if m:
                result, msg = MES.check_process("{}{:02d}".format(sn, n + 1))
                if not result:
                    QMessageBox.critical(None, "Error", msg)
                    is_Testing = False
                    return

    # clear the last test date
    win.tabel_clear_data()

    # test timer start count
    win.timer.start(100)

    # driver start rotate,running
    driver_thread.set_func_name("Equipment_init")
    driver_thread.set_slot(win.equipment_slot)
    driver_thread.start()

    # crate test thread start test
    for i in range(10):
        if test_tunnel_enabled_list[i]:
            win.result_view_list[i - 1].set_enabled(True)

            def func():
                test_thread = Tools.testThread.TestThread(i, term_dict[f'slot{i + 1}'], test_items,
                                                          config_ini["Path"]['logpath'], sn)
                test_thread.test_end_signal.connect(response_test_thread_test_end_signal_slot)
                test_thread.test_content_signal.connect(response_test_thread_test_content_signal_slot)
                test_thread.test_select_row_signal.connect(response_test_thread_test_select_row_signal_slot)
                # test_thread.item_test_result_signal.connect(response_test_thread_item_test_result_signal_slot)
                test_thread.start()

            func()
            test_thread_flag += 1


def response_test_thread_test_content_signal_slot(index, slot, value, color):
    win.add_value(index, slot, value, color)


def response_test_thread_test_select_row_signal_slot(index):
    win.tabel_select_row(index)


def response_test_thread_test_end_signal_slot(slot, result, sn, result_list):
    global test_thread_flag, is_Testing
    if result == 'init':
        win.show_error('设备init失败，请复位后重试！')
        return
    win.result_view_show_status(slot, result)
    win.add_yield_qty(result, 1)
    test_thread_flag -= 1
    # update result to MES
    data = {"result": result.upper(), 'audio_mode': 0, 'start_time': result_list[1],
            'stop_time': time.strftime("%Y-%m-%d %H:%M:%S"), "sn": sn,
            'fixture_id': win.equipment_slot, 'test_head_id': result_list[0],
            'list_of_failing_tests': result_list[-1], 'failure_message': result_list[-1]}
    # 为字典，其中要有result < str >，audio_mode < int >, start_time < str >, stop_time < str >, sn < str >,
    # fixture_id < int >, test_head_id < int >, list_of_failing_tests < str >, failure_message < str >
    MES.update_test_value_to_mes(data)
    if test_thread_flag == 0:
        # t2.set_slot(self.equipment_slot)
        driver_thread.set_func_name("Equipment_reset")
        driver_thread.start()
        win.equipment_slot = 2 if win.equipment_slot == 1 else 1
        win.timer.stop()
        is_Testing = False


def response_main_reset_signal_slot(slot):
    if slot == 1:
        if driver_thread:
            driver_thread.set_slot(1)
            win.equipment_slot = 2
            driver_thread.set_func_name("Reset")
            driver_thread.start()
    elif slot == 2:
        if driver_thread:
            driver_thread.set_slot(2)
            driver_thread.set_func_name("Reset")
            driver_thread.start()
            win.equipment_slot = 1


def signal_connect():
    # win.start_test_signal.connect(response_main_start_test_signal_slot)
    win.reset_signal.connect(response_main_reset_signal_slot)
    win.edit_text_signal.connect(response_main_start_test_signal_slot)


def init():
    term_dict1 = {}
    for key, value in config_ini['PORT1'].items():
        try:
            term = serial.Serial(port=value, baudrate=921600, timeout=0.5)
            term_dict1[key] = term
            win.set_status_label_status(int(key[-1]) - 1, True)
        except Exception:
            win.set_status_label_status(int(key[-1]) - 1, False)
            term_dict1[key] = None
    try:
        equipment_port = driver.Driver(portName=config_ini['DriverConfig']['port'],
                                       baudrate=config_ini['DriverConfig']['baudrate'])
        driver_thread1 = driverThread.DriverThread(equipment_port, 1)
    except:
        QMessageBox.critical(None, "\r\n错误", "未连接到PLC，请检查串口设备后重试！\r\n")
        driver_thread1 = None
    return term_dict1, driver_thread1


def close(data):
    win.close()
    save_ini(BASE_DIR + '/Config-1.ini')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test_items = read_testPlan(BASE_DIR + '/TestPlan.csv')
    config_ini = read_int(BASE_DIR + '/Config-1.ini')
    # term_dict, driver_thread = init()
    print(config_ini)
    MES = mes.Mes()
    win = MainPanel(test_items=test_items, config=config_ini)
    term_dict, driver_thread = init()
    signal_connect()
    win.resize(1500, 800)
    win.setWindowTitle("H26 SIP Sorting")
    win.show()
    sys.exit(app.exec_())
