#!usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:Long.Hou
@file: logDriver.py
@time: 2021/12/13
@email:long.hou2@luxshare-ict.com
"""
import datetime
import logging


class LogDriver:
    def __init__(self, file_name):
        self._log = logging.Logger(name="admin", level=logging.DEBUG)
        self.file_name = file_name
        self.setup_log()
        self.index = 1

    def setup_log(self):
        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(filename=self.file_name, encoding="utf-8", mode="w")
        file_handler.setFormatter(logging.Formatter("[%(asctime)s]  %(message)s"))
        file_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter("[%(threadName)s] [%(asctime)s]  %(message)s"))
        stream_handler.setLevel(logging.DEBUG)
        self._log.addHandler(file_handler)
        self._log.addHandler(stream_handler)

    def mes_log(self,func_name,url,data,response):
        self._log.debug(f"{'-'*20}\nFunction:{func_name}\nRequest URL:{url}\nRequest Method: POST\nRequest Date:{data}\n"
                        f"Response Status Code:{response.status_code}\nResponse Text:{response.text}\n")

    def mes_error_log(self,func_name,url,data,error):
        self._log.error(f"{'-'*20}\nFunction:{func_name}\nRequest URL:{url}\nRequest Method: POST\nRequest Date:{data}\nError information:{error}\n")

    def send_log(self, msg):
        self._log.debug("Send Cmd: " + msg)

    def send_error(self, msg):
        self._log.debug("Error: " + msg)

    def receive_log(self, msg):
        self._log.debug("Receive Content:\n " + msg)

    def set_item_result(self, value, result):
        self._log.debug(f"Get Value: {value}")
        self._log.debug(f'Test Result: {result}')

    def item_end(self, item):
        EndTime = datetime.datetime.now().__sub__(self.stratTime)
        msg = f"Elapsed Second:{EndTime.microseconds / 1000}"
        self._log.info(msg)
        self._log.info(f'Step{self.index}  "{item.TestName}"  End   <------------------------------\n')
        self.index += 1

    def item_start(self, item):
        self.stratTime = datetime.datetime.now()
        msg = f'Step{self.index}  "{item.TestName}" Start   ------------------------------>'
        self._log.info(msg)
        msg = f"low limit:{item.TestLower} up limit:{item.TestUpper}"
        self._log.info(msg)

    def system_reset_start(self):
        self.stratTime = datetime.datetime.now()
        msg = f'Step{self.index}  "System Reset" Start   ------------------------------>'
        self._log.info(msg)

    def system_reset_end(self):
        EndTime = datetime.datetime.now().__sub__(self.stratTime)
        msg = f"Elapsed Second:{EndTime.microseconds / 1000}"
        self._log.info(msg)
        self._log.info(f'Step{self.index}  "System Reset"  End   <------------------------------\n')
        self.index += 1
