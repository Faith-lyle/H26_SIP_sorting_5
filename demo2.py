#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: demo2.py 
@time: 2022/01/20 
@email:long.hou2@luxshare-ict.com
"""
import logging
import socket
address = ('127.0.0.1', 6001)
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(address)
log = logging.Logger("Admin")
# stream_handler = logging.StreamHandler(client)  17：05：45      17：11：00
# stream_handler.setFormatter(logging.Formatter("[%(t  hreadName)s] [%(asctime)s]  %(message)s"))
# stream_handler.setLevel(logging.DEBUG)
# log.addHandler(stream_handler)
log.debug("hello")