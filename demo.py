#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: demo.py 
@time: 2022/01/19 
@email:long.hou2@luxshare-ict.com
"""
import socket
import logging

address = ('127.0.0.1', 6001)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)
server.listen(20)
while True:
    client, add = server.accept()
    date = client.recv(1024).decode("utf-8")
    print(date)
