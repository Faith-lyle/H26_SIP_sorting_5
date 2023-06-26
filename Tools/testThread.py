#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: testThread.py 
@time: 2021/12/13 
@email:long.hou2@luxshare-ict.com
"""
import csv
import time, os
from PyQt5.QtCore import QThread, pyqtSignal
from Tools import logDriver
from Tools import testFunc, wait_event


class TestThread(QThread):
    test_content_signal = pyqtSignal(int, int, str, str)  # 传递测试结果信号，int:测试项目，int:通道，str：测试值
    # item_test_result_signal = pyqtSignal(int, int, str)  # 单项测试结果，用于修改字体颜色,int:测试项目，int:通道,str 结果
    test_select_row_signal = pyqtSignal(int)  # 测试项目选择信号
    test_end_signal = pyqtSignal(int, str, str, list)  # 测试结束信号   str 测试结果

    def __init__(self, slot, port, test_items, base_path, sn):
        super(TestThread, self).__init__()
        self.fail_continue_flag = False
        self.port = port
        self.base_path = base_path
        self.slot = slot
        self.sn = sn
        self.wait_old_thread_finished_flag = False
        self.test_value = {}
        self.on_line_test = True
        self.log = logDriver.LogDriver(os.path.join(self.base_path, 'slot{}.txt'.format(self.slot)))
        self.TestItems = test_items  # 测试序列，是个TestItem类的列表
        self.test_func = testFunc.TestFunc(port, self.log)
        self.result_list = ["slot{}".format(self.slot),
                            time.strftime("%Y-%m-%d %H:%M:%S")]  # 创建一个列表，用于记录单项测试的值，方便生成CSV文件

    def config_init(self):
        self.fail_continue_flag = False
        self.on_line_test = True
        self.wait_old_thread_finished_flag = False
        self.test_value = {}
        self.log = logDriver.LogDriver(
            os.path.join(self.base_path, f"H26_SIP_Sortong_Slot_{self.slot}_{time.strftime('%H-%M-%S')}.txt"))
        self.test_func = testFunc.TestFunc(self.port, self.log)
        self.result_list = ["slot{}".format(self.slot), time.strftime("%Y-%m-%d %H:%M:%S")]

    def set_continue_flag(self, flag: bool):
        self.fail_continue_flag = flag

    def set_equipment_result(self, result):
        self.equipment_result = result

    def set_wait_old_thread_finished_flag(self, flag, result):
        self.wait_old_thread_finished_flag = flag
        self.set_equipment_result(result)

    def run(self):
        self.full_test()
        if False not in self.test_value.values():
            self.result_list.insert(2, "PASS")
            failure_message = ''
            result = self.result_list.append(failure_message)
            self.test_end_signal.emit(self.slot, "pass", self.sn, result)
        else:
            self.result_list.insert(2, "FAIL")
            failure_message = ''
            for key, value in self.test_value.items():
                if not value:
                    failure_message += f'{key}:--FAIL--;'
            result = self.result_list.append(failure_message)
            self.test_end_signal.emit(self.slot, "fail", self.sn, result)
        self.write_csv()

    def full_test(self):
        i = 0
        for item in self.TestItems:
            if item.isEnabled:
                self.log.item_start(item)
                self.test_select_row_signal.emit(i)
                for a in range(int(item.ReTestTime)):
                    try:
                        if item.TestMode == "Normal":
                            cmd_list = [i.strip() for i in item.TestCmd.split(',')]
                            text = self.test_func.normal_send_cmd(cmd_list)
                            result, value = self.test_func.parse_data(decision_mode=item.DecisionMode, text=text,
                                                                      re_flag=item.ReMarket,
                                                                      upper=item.TestUpper, lower=item.TestLower)
                            self.result_list.append(value)
                            if result:
                                self.test_content_signal.emit(i, self.slot, str(value), "green")
                                # self.item_test_result_signal.emit(i, self.slot, "green")
                                self.log.set_item_result(value, "--PASS--")
                                if item.TestName == 'Ear Reset':
                                    time.sleep(2)
                                self.test_value[item.TestName] = True
                                break
                            else:
                                self.test_content_signal.emit(i, self.slot, str(value), 'red')
                                # self.item_test_result_signal.emit(i, self.slot, "red")
                                self.log.set_item_result(value, "--FAIL--")
                                self.test_value[item.TestName] = False
                        elif item.TestMode == "Special":
                            result, value = self.test_func.func_dict[item.TestName](lower=item.TestLower,
                                                                                    upper=item.TestUpper)
                            self.result_list.append(value)
                            if result:
                                self.test_content_signal.emit(i, self.slot, str(value), "green")
                                # self.item_test_result_signal.emit(i, self.slot, "green")
                                self.log.set_item_result(value, "--PASS--")
                                break
                            else:
                                self.test_content_signal.emit(i, self.slot, str(value), 'red')
                                # self.item_test_result_signal.emit(i, self.slot, "red")
                                self.log.set_item_result(value, "--FAIL--")
                                self.test_value[item.TestName] = False
                        elif item.TestMode == 'Equipment_init':
                            result, value = True, "PASS"
                            s_time = time.time()
                            wait_event.wait(10)
                            if time.time() - s_time > 10:
                                self.test_content_signal.emit(i, self.slot, str(value), 'red')
                                # self.item_test_result_signal.emit(i, self.slot, "red")
                                self.test_end_signal.emit(self.slot, "fail-init",self.sn, self.result_list)
                                return
                            else:
                                self.result_list.append(value)
                                if result:
                                    self.test_content_signal.emit(i, self.slot, str(value), "green")
                                    # self.item_test_result_signal.emit(i, self.slot, "green")
                                    self.log.set_item_result(value, "--PASS--")
                                    self.test_value[item.TestName] = True
                        elif item.TestMode == 'Equipment_reset':
                            result, value = True, "PASS"
                            self.result_list.append(value)
                            if result:
                                self.test_content_signal.emit(i, self.slot, str(value), "green")
                                # self.item_test_result_signal.emit(i, self.slot, "green")
                                self.log.set_item_result(value, "--PASS--")
                                self.test_value[item.TestName] = True
                            else:
                                self.test_content_signal.emit(i, self.slot, str(value), 'red')
                                # self.item_test_result_signal.emit(i, self.slot, "red")
                                self.log.set_item_result(value, "--FAIL--")
                                self.test_value[item.TestName] = False
                    except Exception as e:
                        self.test_content_signal.emit(i, self.slot, "--FAIL--", 'red')
                        # self.item_test_result_signal.emit(i, self.slot, "red")
                        self.log.set_item_result(e, "Error")
                        self.test_value[item.TestName] = False
                        break
                self.log.item_end(item)
            i += 1
            if not self.fail_continue_flag:
                if not self.test_value[item.TestName]:
                    break

    def write_csv(self):
        file_path = os.path.join(self.base_path, f"H26_SIP_Sortong_{time.strftime('%Y-%m-%d')}.csv")
        if not os.path.exists(file_path):
            headers = ["Slot", "TestTime", 'Test Result']
            upper = [" ", "Upper", '']
            lower = [" ", "Lower", '']
            for item in self.TestItems:
                headers.append(item.TestName)
                lower.append(item.TestLower)
                upper.append(item.TestUpper)
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerow(lower)
                writer.writerow(upper)
                writer.writerow(self.result_list)
        else:
            with open(file_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.result_list)

    def read_information_from_mes(self):
        result = True
        return result

    def update_information_to_mes(self, data):
        result = True


if __name__ == '__main__':
    pass
    # print(os.path.join(base_path, 'slo1.txt'))
