#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: testFunc.py
@time: 2021/12/13 
@email:long.hou2@luxshare-ict.com
"""
import re, math
import struct
import time

import requests

from Tools import serialPort


class TestFunc():

    def __init__(self, port, log):
        self.term = serialPort.SerialPort(Port_obj=port, log_driver=log)
        self.url = 'http://10.100.2.69/Bobcat/Sfc_Response.aspx'
        self.accel_axis_x_list = []
        self.accel_axis_y_list = []
        self.accel_axis_z_list = []
        self.gylo_axis_x_list = []
        self.gylo_axis_y_list = []
        self.gylo_axis_z_list = []
        self.accel_axis_t_list = []
        self.lis_LESTRADE_DARK_4 = []
        self.lis_HUDSON_DARK_4 = []
        self.inplane = []
        self.outplane = []
        self.normal_gain = 4.0 / 32768
        self.func_dict = {'Open SerialPort': self.open_port, 'Close Serial Port': self.close_port,"FT UVP":self.ft_uvp,
                          'MIC1 Test': self.mic1_test, 'Wait Tunnel Close': self.wait_tunnel_close,
                          'MIC2 Test': self.mic1_test, 'MIC3 Test': self.mic1_test,
                          'Optical Lestrade dark Mean': self.optical_lestrade_dark_mean,
                          'Optical Hudson Dark Mean': self.optical_hudson_dark_mean,
                          'Optical Sensor PDVF': self.optical_sensor_pdvf, 'Read Accel Info': self.read_accel_info,
                          'Read Gyro Info': self.read_gyro_info,
                          'Accel Normal Average Temp': self.accel_normal_average_temp,
                          "Accel Normal Average X": self.accel_normal_average_x,
                          "Accel Normal Average Y": self.accel_normal_average_y,
                          "Accel Normal Average Z": self.accel_normal_average_z,
                          'Accel Normal Std X': self.accel_normal_std_x,
                          'Accel Normal Std Y': self.accel_normal_std_y,
                          'Accel Normal Std Z': self.accel_normal_std_z,
                          'Gylo Normal Average X': self.gylo_normal_average_x,
                          'Gylo Normal Average Y': self.gylo_normal_average_y,
                          'Gylo Normal Average Z': self.gylo_normal_average_z,
                          'Gylo Normal Std X': self.gylo_normal_std_x,
                          'Gylo Normal Std Y': self.gylo_normal_std_y,
                          'Gylo Normal Std Z': self.gylo_normal_std_z,
                          'Get Kessel Rev Id': self.get_kessel_rev_id,
                          'Kessel Read Value': self.kessel_read_value,
                          'Kessel Accesl Average X': self.kessel_accesl_average_x,
                          'Kessel Accesl Average Z': self.kessel_accesl_average_z,
                          "Kessel Accesl Std X": self.kessel_accesl_std_x,
                          "Kessel Accesl Std Z": self.kessel_accesl_std_z,
                            'Read Optical Iedtest':self.read_optical_iedtest,
                          'IMU Read Value':self.imu_read_value,
                          }

    def close_func(self):
        text = self.term.send_and_read("ft tunnel close\n", 1)
        # self.term.close_port()
    def normal_send_cmd(self, cmd_list):
        text = ''
        for cmd in cmd_list:
            if '[' in cmd:
                text += self.term.send_and_read(cmd, 0.2)
            else:
                if cmd == "ft tunnel close" or cmd == "ft reset":
                    text += self.term.send_and_read(cmd+"\n", 0.8)
                    # text += self.term.send_and_read_until(cmd + '\n', timeout=3, terminator='CLOSED')
                elif 'selftest' in cmd:
                    text += self.term.send_and_read_until(cmd + '\n', timeout=5, terminator='> ')
                else:
                    text += self.term.send_and_read_until(cmd+'\n', timeout=3, terminator='> ')
        return text

    @staticmethod
    def parse_data(decision_mode, text, re_flag, upper=0, lower=0):
        result = False, 'None'
        if decision_mode == "IN":
            if re_flag in text:
                result = True, re_flag
        elif decision_mode == "Length":
            ReFlag = re.search(re_flag, text, re.MULTILINE)  # 用RE匹配关键信息
            if len(ReFlag.groups()[0]) == int(lower):
                result = True, ReFlag.groups()[0]
            else:
                result = False, ReFlag.groups()[0]
        elif decision_mode == "Compare":
            ReFlag = re.search(re_flag, text, re.MULTILINE)  # 用RE匹配关键信息
            print(ReFlag.groups())
            if float(lower) < float(ReFlag.groups()[0]) < float(upper):
                result = True, ReFlag.groups()[0]
            else:
                result = False, ReFlag.groups()[0]
        elif decision_mode == "Equality":
            ReFlag = re.search(re_flag, text, re.MULTILINE)  # 用RE匹配关键信息
            if lower == ReFlag.groups()[0]:
                result = True, ReFlag.groups()[0]
            else:
                result = False, ReFlag.groups()[0]
        return result

    def close_port(self, upper=0, lower=0):
        result = self.term.close_port()
        if result:
            return True, "--PASS--"
        else:
            return False,"--FAIL--"

    def open_port(self, upper=0, lower=0):
        result = self.term.open_port()
        if result:
            return True, "--PASS--"
        else:
            return False,"--FAIL--"

    def ft_uvp(self, upper=0, lower=0):
        result = False, "None"
        text = self.term.send_and_read(f"ft uvp", 0.3)
        text += self.term.send_and_read(f"ft tunnel close", 0.5)
        if "TUNNEL: CLOSED" not in text:
            result = True, "None"
        else:
            result = False, "--FAIL--"
        return result

    def wait_tunnel_close(self, timeout=50, upper=0, lower=0):
        result = False, "--FAIL--"
        time_flag = 0
        while True:
            content = self.term.read_all()
            if "TUNNEL: CLOSED" in content:
                result = True, "TUNNEL: CLOSED"
                break
            elif time_flag > timeout:
                result = False, "--FAIL--"
                break
            time.sleep(0.2)
            time_flag += 1
        return result

    def mic1_test(self, upper=0, lower=0):
        result = False, "None"
        time.sleep(1)
        self.term.send_and_read_until("audio stop\n", timeout=1, terminator="> ")
        text = self.term.send_and_read_until("audio dump\n", timeout=1, terminator="> ")
        flag = re.search(r"audio:ok begin(.*?)(:.*)?> audio:ok done", text, re.S)
        if len(flag.groups()) < 2:
            result = False, "--FAIL--"
        else:
            content = flag.groups()[1].split(":")[1:]
            if mic_test(content):
                result = True, content
            else:
                result = False, content
        return result

    def read_optical_iedtest(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("kadabra iedtest none 15 36000 36000 4 4\n", timeout=10, terminator="> ")
        if '> kadabra:ok' in text:
            for item in text.split("\n")[2:16]:
                self.lis_LESTRADE_DARK_4.append(int(item.split("|")[5].strip()))
                self.lis_HUDSON_DARK_4.append(int(item.split("|")[9].strip()))
                self.lis_HUDSON_DARK_4.append(int(item.split("|")[11].strip()))
            result = True, "kadabra:ok"
        else:
            result = False, "--FAIL--"
        return result

    def optical_lestrade_dark_mean(self, upper=0, lower=0):
        value = sum(self.lis_LESTRADE_DARK_4) / len(self.lis_LESTRADE_DARK_4)
        if float(lower) < value < float(upper):
            result = True, value
        else:
            result = False, value
        return result

    def optical_hudson_dark_mean(self, upper=0, lower=0):
        result = False, "--FAIL--"
        value = sum(self.lis_HUDSON_DARK_4) / len(self.lis_HUDSON_DARK_4)
        if float(lower) < value < float(upper):
            result = True, value
        else:
            result = False, value
        return result

    def optical_sensor_pdvf(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("kadabra pdvf\n", timeout=1, terminator="> ")
        lis_KADABRA_PDVF = []
        if '> kadabra:ok' in text:
            for item in text.split("\n")[2:3]:
                lis_KADABRA_PDVF.append(int(item.split("|")[6].strip()))
                lis_KADABRA_PDVF.append(int(item.split("|")[12].strip()))
            value = sum(lis_KADABRA_PDVF) / len(lis_KADABRA_PDVF) * (1.4 / 8192)
            if float(lower) < value < float(upper):
                result = True, value
            else:
                result = True, value
        return result

    def read_accel_info(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("accel info\n", timeout=1, terminator="> ")
        flag = re.search(r"Sensor type : (.*)?\nDevice      : (.*)?\n(.*)?\nCal matrix  : (.*)?\nCal offset", text,
                         re.S)
        if len(flag.groups()) < 4:
            result = False, "--FAIL--"
        else:
            if flag.groups()[0] == "accel" :
                result = True, flag.groups()[0]
            else:
                result = False, flag.groups()[0]
        return result

    def read_gyro_info(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("gyro info\n", timeout=1, terminator="> ")
        flag = re.search(r"Sensor type : (.*)?\nDevice      : (.*)?\n(.*)?\nCal matrix  : (.*)?\nCal offset", text,
                         re.S)
        if len(flag.groups()) < 4:
            result = False, "--FAIL--"
        else:
            if flag.groups()[0] == "gyro" :
                result = True, flag.groups()[0]
            else:
                result = False, flag.groups()[0]
        return result

    def imu_read_value(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("imu stream 5000 30\n", timeout=7, terminator="> ")
        if "ERROR" not in text.upper():
            arr = text.replace('\r', '').split('\n')
            for subarr in arr:
                if 'accel:: sample:' in subarr:
                    accel_x = subarr.split('x:')[1].split('y:')[0].strip()
                    accel_y = subarr.split('y:')[1].split('z:')[0].strip()
                    accel_z = subarr.split('z:')[1].split('temp:')[0].strip()
                    accel_t = subarr.split('temp:')[1].split('timestamp:')[0].strip()
                    self.accel_axis_x_list.append(int(accel_x) * 16.0 / 32767)
                    self.accel_axis_y_list.append(int(accel_y) * 16.0 / 32767)
                    self.accel_axis_z_list.append(int(accel_z) * 16.0 / 32767)
                    self.accel_axis_t_list.append(float(accel_t))

                elif 'gyro:: sample:' in subarr:
                    gyro_x = subarr.split('x:')[1].split('y:')[0].strip()
                    gyro_y = subarr.split('y:')[1].split('z:')[0].strip()
                    gyro_z = subarr.split('z:')[1].split('temp:')[0].strip()
                    gyro_t = subarr.split('timestamp:')[1].strip()
                    self.gylo_axis_x_list.append(int(gyro_x) * 2000.0 / 32767)
                    self.gylo_axis_y_list.append(int(gyro_y) * 2000.0 / 32767)
                    self.gylo_axis_z_list.append(int(gyro_z) * 2000.0 / 32767)
            result = True, "--PASS--"
        else:
            result = False, "--FAIL--"
        return result

    def accel_normal_average_x(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.accel_axis_x_list:
            avg = calculate_avg(self.accel_axis_x_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def accel_normal_average_temp(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.accel_axis_t_list:
            avg = calculate_avg(self.accel_axis_t_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def accel_normal_average_y(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.accel_axis_y_list:
            avg = calculate_avg(self.accel_axis_y_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def accel_normal_average_z(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.accel_axis_z_list:
            avg = calculate_avg(self.accel_axis_z_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def accel_normal_std_z(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.accel_axis_z_list:
            avg = calculate_std(self.accel_axis_z_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def accel_normal_std_y(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.accel_axis_y_list:
            avg = calculate_std(self.accel_axis_y_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def accel_normal_std_x(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.accel_axis_x_list:
            avg = calculate_std(self.accel_axis_x_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def gylo_normal_std_x(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.gylo_axis_x_list:
            avg = calculate_std(self.gylo_axis_x_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def gylo_normal_std_y(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.gylo_axis_y_list:
            avg = calculate_std(self.gylo_axis_y_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def gylo_normal_std_z(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.gylo_axis_z_list:
            avg = calculate_std(self.gylo_axis_z_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def gylo_normal_average_z(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.gylo_axis_z_list:
            avg = calculate_avg(self.gylo_axis_z_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def gylo_normal_average_y(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.gylo_axis_y_list:
            avg = calculate_avg(self.gylo_axis_y_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def gylo_normal_average_x(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.gylo_axis_x_list:
            avg = calculate_avg(self.gylo_axis_x_list)
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def get_kessel_chip_id(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("i2c read reg8 aon 48 1 2\n", timeout=1, terminator="> ")
        flag = re.search(r"i2c:ok (.*)?\n", text, re.S)
        if len(flag.groups()) < 1:
            result = False, "--FAIL--"
        else:
            content = flag.groups()[0]
            if content == upper or content == lower:
                result = True, content
        return result

    def get_kessel_manu_id(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("i2c read reg8 aon 48 0 2\n", timeout=1, terminator="> ")
        flag = re.search(r"i2c:ok (.*)?\n", text, re.S)
        if len(flag.groups()) < 1:
            result = False, "--FAIL--"
        else:
            content = flag.groups()[0]
            result = True, content
        return result

    def get_kessel_rev_id(self, upper=0, lower=0):
        result = False, "--FAIL--"
        text = self.term.send_and_read_until("i2c read reg8 aon 48 2 2\n", timeout=1, terminator="> ")
        flag = re.search(r"i2c:ok (.*)?\n", text, re.S)
        if len(flag.groups()) < 1:
            result = False, "--FAIL--"
        else:
            content = flag.groups()[0]
            if content[-2:] == "20" or content[-2:] == "10":
                self.normal_gain = 4.3 / 32768
                result = True, content
            elif content[-2:] == "00":
                self.normal_gain = 4.0 / 32768
                result = True, content
        return result

    def kessel_read_value(self, upper=0, lower=0):
        result = False, "--FAIL--"
        self.term.send_and_read_until("audio init\n", timeout=5, terminator="> ")
        self.term.send_and_read_until("audio kessel start\n", timeout=5, terminator="> ")
        self.term.send_and_read_until("audio kessel stop\n", timeout=5, terminator="> ")
        time.sleep(0.5)
        text = self.term.send_and_read_until("audio kessel dump\n", timeout=10, terminator="> ")
        self.term.send_and_read_until("audio kessel stop\n", timeout=5, terminator="> ")
        if "ERROR" not in text.upper():
            expectstr = ""
            for substr in text.split('\n'):
                if substr.startswith(':'):
                    expectstr += substr[1:]
            b = bytearray.fromhex(expectstr)
            c = struct.unpack("<%dh" % (len(b) / 2), b)
            for k in range(0, len(c), 3):
                if (c[k] != 0) and (c[k + 1] != 0):
                    self.inplane.append(c[k])
                    self.outplane.append(c[k + 1])
            result = True, "--PASS--"
        else:
            result = False, "--FAIL--"
        return result

    def kessel_accesl_average_x(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.inplane:
            avg = calculate_avg(self.inplane) * self.normal_gain
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def kessel_accesl_std_x(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.inplane:
            avg = calculate_std(self.inplane) * self.normal_gain
            if float(lower )< avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def kessel_accesl_average_z(self, upper=0, lower=0):
        result = False, "--FAIL--"

        if self.outplane:
            avg = calculate_avg(self.outplane) * self.normal_gain

            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def kessel_accesl_std_z(self, upper=0, lower=0):
        result = False, "--FAIL--"
        if self.outplane:
            avg = calculate_std(self.outplane) * self.normal_gain
            if float(lower) < avg < float(upper):
                result = True, str(avg)
            else:
                result = False, str(avg)
        return result

    def get_SIP_X_num(self,sn):
        result = False, "--FAIL--"
        data = {'p': "SIP_X_NUM", "c": "QUERY_RECORD", "sn": sn}
        response = requests.post(url=self.url, data=data)
        if response.status_code == 200:
            if "SFC_OK" in response.text:
                print(response.text)

    def check_process(self, sn):
        result = False, "--FAIL--"
        data = {'p': "unit_process_check", "c": "QUERY_RECORD", 'sw_version': '', 'tsid': '', "sn": sn,
                'fixture_id': None}
        response = requests.post(url=self.url, data=data)
        if response.status_code == 200:
            if "SFC_OK" in response.text:
                if response.text.endswith("unit_process_check=OK"):
                    result =  True, "--PASS--"

        return result


def get_x_y_z(text):
    flag = re.findall(r"x: (.*)?y:(.*)?z:(.*)?temp:", text)
    x_list = []
    y_list = []
    z_list = []
    for li in flag:
        x_list.append(int(li[0]))
        y_list.append(int(li[1]))
        z_list.append(int(li[2]))
    return x_list, y_list, z_list


def calculate_std(l1: list):
    sum = 0
    for i in l1:
        sum += i
    avg = sum / (len(l1))
    sum2 = 0
    for i in l1:
        sum2 += (i - avg) * (i - avg)
    std = math.sqrt(sum2 / len(l1))
    return std


def calculate_avg(l1: list):
    sum = 0
    for i in l1:
        sum += i
    avg = sum / (len(l1))
    return avg


def mic_test(result):
    if len(result) != 6:
        return False
    value = 0
    for t1 in result:
        m = 8
        for a in range(7):
            ok1 = t1[m - 8:m]
            ok2 = t1[m:m + 8]
            if ok1 == ok2:
                value += 1
            else:
                value += 0
            m += 8
    if value >= 7:
        final = False
    else:
        final = True
    return final


if __name__ == '__main__':
    t = TestFunc("CM1", 1)
