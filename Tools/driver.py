#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: driver.py 
@time: 2021/12/31 
@email:long.hou2@luxshare-ict.com
"""
import time
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import serial


class Driver:

    def __init__(self, portName,baudrate=19200, bytesize=8, parity="E", stopbits=1):
        # self._term
        self._term = modbus_rtu.RtuMaster(
            serial.Serial(port=portName, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits))
        self._term.set_verbose(True)
        self._term.set_timeout(0.5)

    def close(self):
        if self._term.is_opened:
            self._term.close()

    def open(self):
        if not self._term.is_opened:
            self._term.open()

    def isOpen(self):
        return self._term.is_opened

    def driver_reset(self, slot):
        result = False
        if slot == 1:
            response = self._term.execute(1, cst.WRITE_SINGLE_COIL, 301, output_value=0)
            if len(response) == 2:
                if response[0] == 301 and response[1] == 0:
                    result = True
        elif slot == 2:
            response = self._term.execute(1, cst.WRITE_SINGLE_COIL, 304, output_value=0)
            if len(response) == 2:
                if response[0] == 304 and response[1] == 0:
                    result = True
        return result

    def cylinder_rise(self):
        result = False
        if self._term:
            try:
                content = self._term.execute(1, cst.WRITE_SINGLE_COIL, 306, output_value=1)
                if len(content) == 2:
                    if content[0] == 306 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = False
                                break
                            text = self._term.execute(1, cst.READ_COILS, 312, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = True
                                break
            except Exception as e:
                pass
            return result

    def rotary_driver_1(self):
        result = False
        if self._term:
            try:
                content = self._term.execute(1, cst.WRITE_SINGLE_COIL, 308, output_value=1)
                if len(content) == 2:
                    if content[0] == 308 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = False
                                break
                            text = self._term.execute(1, cst.READ_COILS, 310, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = True
                                break
            except Exception as e:
                result = False
            return result

    def rotary_driver_2(self):
        result = False
        if self._term:
            try:
                content = self._term.execute(1, cst.WRITE_SINGLE_COIL, 309, output_value=1)
                if len(content) == 2:
                    if content[0] == 309 and content[1] == 0xFF00:
                        start_time = time.time()
                        while True:
                            if time.time() - start_time > 5:
                                result = False
                                break
                            text = self._term.execute(1, cst.READ_COILS, 311, 1)
                            if len(text) == 1 and text[0] == 1:
                                result = True
                                break
            except Exception as e:
                pass
            return result

    def reset(self,slot):
        self.cylinder_rise()
    def driver_wait_done(self, slot, timeout=9):
        result = False
        start = time.time()
        while True:
            if time.time() - start > timeout:
                break
            if slot == 1:
                response = self._term.execute(1, cst.READ_COILS, 301, 1)
                if len(response) == 1:
                    if response[0] == 1:
                        # time.sleep(0.5)
                        result = True
                        break
            elif slot == 2:
                response = self._term.execute(1, cst.READ_COILS, 304, 1)
                if len(response) == 1:
                    if response[0] == 1:
                        result = True
                        # time.sleep(0.5)
                        break

        return result

    def driver_start_test(self, slot):
        result = False
        if slot == 1:
            response = self._term.execute(1, cst.WRITE_SINGLE_COIL, 300, output_value=1)
            if len(response) == 2:
                if response[0] == 300 and response[1] == 0xFF00:
                    result = True
        elif slot == 2:
            response = self._term.execute(1, cst.WRITE_SINGLE_COIL, 302, output_value=1)
            if len(response) == 2:
                if response[0] == 302 and response[1] == 0xFF00:
                    result = True
        return result


class Driver1:

    def __init__(self, portName):
        # self._term
        self._term = serial.Serial(port=portName, baudrate=19200, bytesize=8, parity="E", stopbits=1, timeout=1)

    def close(self):
        if self._term.is_open:
            self._term.close()

    def send_and_readall(self, cmd,size=1):
        start_time = time.time()
        if not self._term.is_open:
            self.open()
        self._term.write(cmd)
        while True:
            if (time.time() - start_time) > 0.5:
                return
            if self._term.in_waiting:
                text = self._term.read(size).hex()
                return text

    def open(self):
        if not self._term.is_open:
            self._term.open()

    def driver_reset(self, slot):
        result = False
        if slot == 1:
            response = self.send_and_readall(b'\x01\x05\x01-\x00\x00\\?',16)
            # print(response)
            # print('0105012d00005c3f')
            if response == '0105012d00005c3f':
                result = True
        elif slot == 2:
            response = self.send_and_readall(b'\x01\x05\x010\x00\x00\xcc9',16)
            # print(response)
            # print('010501300000cc39')
            if response == '010501300000cc39':
                result = True
        return result

    def driver_wait_done(self, slot, timeout=5):
        result = False
        start = time.time()
        while True:
            if time.time() - start > timeout:
                break
            if slot == 1:
                response = self.send_and_readall(b'\x01\x01\x01-\x00\x01l?',12)
                # print(response)
                # print('010101019048')
                if response == '010101019048':
                    result = True
                    break
                # time.sleep(0.5)
            elif slot == 2:
                response = self.send_and_readall(b'\x01\x01\x010\x00\x01\xfc9',12)
                # print(response)
                # print('010101019048')
                if response == '010101019048':
                    result = True
                    break
                # time.sleep(0.5)
        return result

    def driver_start_test(self, slot):
        result = False
        if slot == 1:
            response = self.send_and_readall(b'\x01\x05\x01,\xff\x00L\x0f',16)
            # print(response)
            # print('0105012cff004c0f')
            if response=='0105012cff004c0f':
                result =True
        elif slot == 2:
            response = self.send_and_readall(b'\x01\x05\x01.\xff\x00\xed\xcf',16)
            # print(response)
            # print('0105012eff00edcf')
            if response=='0105012eff00edcf':
                result =True
        return result

if __name__ == '__main__':
    port = '/dev/cu.usbserial-FTAVNF9J'
    d = Driver1(portName=port)
    print("1# 旋转开始")
    result = d.driver_start_test(1)
    print(result)
    time.sleep(2)
    print("1# 旋转结束")
    print("1# 读取下压状态开始")
    r = d.driver_wait_done(1)
    print(r)
    print("1# 读取下压状态结束")
    print("1# 气缸上升开始")
    r = d.driver_reset(1)
    print(r)
    print("1# 气缸上升结束")
    time.sleep(2)
    print("2# 旋转开始")
    r = d.driver_start_test(2)
    print(r)
    time.sleep(2)
    print("2# 旋转结束")
    print("2# 读取下压状态开始")
    r = d.driver_wait_done(2)
    print(r)
    print("2# 读取下压状态结束")
    print("2# 气缸上升开始")
    r = d.driver_reset(2)
    print(r)
    print("2# 气缸上升结束")
aaa = '''
1# 旋转开始
b'\x01\x05\x01,\xff\x00L\x0f'
1# 旋转结束
1# 读取下压状态开始
b'\x01\x01\x01\x00'
b'Q\x88'
b'\x01\x01\x01\x00Q\x88'
b'\x01\x01\x01\x00Q\x88'
b'\x01\x01\x01\x00Q\x88'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
1# 读取下压状态结束
1# 气缸上升开始
b'\x01\x01\x01\x01\x90H'
1# 气缸上升结束
2# 旋转开始
b'\x01\x05\x01-\x00\x00\\?'
2# 旋转结束
2# 读取下压状态开始
b'\x01\x05\x01.\xff\x00\xed\xcf'
b'\x01\x01\x01\x00Q\x88'
b'\x01\x01\x01\x00Q\x88'
b'\x01\x01\x01\x00Q\x88'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
b'\x01\x01\x01\x01\x90H'
2# 读取下压状态结束
2# 气缸上升开始
b'\x01\x01\x01\x01\x90H'
2# 气缸上升结束

1# 旋转开始
0105012cff00
1# 旋转结束
1# 读取下压状态开始
4c0f
010101005188
010101005188
010101005188
010101005188
010101019048
010101019048
010101019048
010101019048
010101019048
1# 读取下压状态结束
1# 气缸上升开始
010101019048
1# 气缸上升结束
2# 旋转开始
0105012d00005c3f
2# 旋转结束
2# 读取下压状态开始
0105012eff00edcf
010101005188
010101005188
010101005188
010101019048
010101019048
010101019048
010101019048
010101019048
010101019048
2# 读取下压状态结束
2# 气缸上升开始
010101019048
2# 气缸上升结束
'''