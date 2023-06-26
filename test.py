#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: test.py 
@time: 2022/02/09 
@email:long.hou2@luxshare-ict.com
"""
import time

import serial
from modbus_tk import modbus_rtu
import modbus_tk.defines as cst

port = "/dev/cu.usbserial-DUT2"
def serial_port():
    term = serial.Serial(port=port, baudrate=19200, bytesize=8, parity="E", stopbits=1,timeout=1)
    term.write(b'\x01\x05\x01,\xff\x00L\x0f')
    time.sleep(1)
    print(term.read_all().decode("utf-8"))

def mudbuds():
    term = modbus_rtu.RtuMaster(
        serial.Serial(port=port, baudrate=19200, bytesize=8, parity="E", stopbits=1))
    term.set_verbose(True)
    term.set_timeout(0.5)
    content = term.execute(1,cst.WRITE_SINGLE_COIL,304,output_value=0)
    print(content)

# mudbuds()
# serial_port()
'''
1# 旋转：b'\x01\x05\x01,\xff\x00L\x0f'
2# 旋转：b'\x01\x05\x01.\xff\x00\xed\xcf'
读1#下压状态  b'\x01\x01\x01-\x00\x01l?'
读2#下压状态  b'\x01\x01\x010\x00\x01\xfc9'
1# 上升    b'\x01\x05\x01-\x00\x00\\?'
2# 上升   b'\x01\x05\x010\x00\x00\xcc9'

'''
import binascii
a = b'\x01\x01\x01-\x00\x01l?'
print(a.hex())
print(type(a))
b = '0105012cff004c0f'
print(binascii.a2b_hex(b))
print(type(b'\x01\x05\x01-\x00\x00\\?'.hex()))

a = ['1','1','1','1','1','1','1']
b = map(int,a)
for m,i in enumerate(b):
    print(i)
    print(m)

text = '''0 SFC_OK
,02'''
l1 =text.split('SFC_OK')[1]
l2 = map(int, l1.split(',')[1:])
for i in l2:
    print(i)
copy_list = [1,6,2,7,3,8,4,9,5,10]
print(copy_list[2])
print('     aa'.strip())