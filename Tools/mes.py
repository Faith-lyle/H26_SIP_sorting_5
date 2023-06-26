#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: mes.py 
@time: 2022/01/07 
@email:long.hou2@luxshare-ict.com
"""
import os.path
import json
import time

from Tools.logDriver import LogDriver
import requests

'''200
0 SFC_OK
NO X BOAR'''

'''
0 SFC_OK  tsid::SIP Measurement-A6-3F-S09-1::unit_process_check=UNIT OUT OF PROCESS TERMINAL_NAME ERROR!'''


class Mes:
    def __init__(self):
        self.url = 'http://10.100.2.69/Bobcat/Sfc_Response.aspx'
        self.config_path = os.path.expanduser("~/H26_SIP_Sorting/config.json")
        self.log = LogDriver(os.path.expanduser(f"~/H26_SIP_Sorting/MESLOG/MesLog{time.strftime('%Y%m%d%H%M')}.txt"))
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            self.log.mes_error_log(url=self.url,data='Not found config.json file,pleace try again!',error=e)
            self.config= {}


    def get_SIP_X_num(self, sn):
        result = False, None
        try:
            data = {'p': "SIP_X_NUM", "c": "QUERY_RECORD", "sn": sn}
            response = requests.post(url=self.url, data=data,timeout=3)
            self.log.mes_log(func_name='get_SIP_X_num',url=self.url,data=data,response=response)
            if response.status_code == 200:
                if "SFC_OK" in response.text:
                    l1 = response.text.split("SFC_OK")[1]
                    if 'NO X BOAR' in l1:
                        result = True, []
                    else:
                        result = True, map(int, l1.split(',')[1:])
        except Exception as e:
            result = False, "get_SIP_X_num Error\n{}".format(e)
        return result

    def check_process(self, sn):
        result = False, "Process Error\n unit_process_check=UNIT OUT OF PROCESS TERMINAL_NAME ERROR!"
        try:
            data = {'p': "unit_process_check", "c": "QUERY_RECORD", 'sw_version': self.config['sw_version'],
                    'tsid': self.config['station_id'],"sn": sn,'fixture_id': None}
            response = requests.post(url=self.url, data=data,timeout=3)
            self.log.mes_log(func_name="check_process",url=self.url, data=data, response=response)
            if response.status_code == 200:
                if "SFC_OK" in response.text:
                    if response.text.endswith("unit_process_check=OK"):
                        result = True, 'unit_process_check=OK'
                    else:
                        result = False, 'Process Error\n'+response.text.split('::')[-1]
        except Exception as e:
            result = False, "check_process Error\n{}".format(e)
        return result

    def update_test_value_to_mes(self, data):
        '''
        :param data: data 为字典，其中要有result<str>，audio_mode<int>,start_time<str>,stop_time<str>,sn<str>,
        fixture_id<int>,test_head_id<int>,list_of_failing_tests<str>,failure_message<str>
        :return:
        '''
        result = False
        try:
            for k in self.config.keys():
                data[k] = self.config[k]
            data["c"] = "ADD_RECORD"
            response = requests.post(url=self.url, data=data,timeout=3)
            self.log.mes_log(func_name='update_test_value_to_mes',url=self.url, data=data, response=response)
            if response.status_code == 200:
                if "SFC_OK" in response.text:
                    result = True
        except Exception as e:
            self.log.mes_error_log(func_name='update_test_value_to_mes',url=self.url,data=data,error=e)
            result = False
        return result


if __name__ == '__main__':
    mes = Mes()
    sn = 'CH26RB2102004CC'

    # mes.get_SIP_X_num(sn)
    # for i in range(10):
    #     if i==9:
    #         mes.check_process("{}{}".format(sn,i+1))
    #     else:
    #         mes.check_process("{}0{}".format(sn, i + 1))
    for i in range(1,10):
        data = {'result': 'PASS', 'audit_mode': 0, 'start_time': time.strftime("%H:%M:%S"),
                'stop_time': time.strftime("%H:%M:%S"),
                'sn': '{}0{}'.format(sn,i),
                'fixture_id': i, 'test_head_id': i, 'list_of_failing_tests': '', 'failure_message': ''}
        # mes.update_test_value_to_mes(data)
    data = {'result': 'PASS', 'audit_mode': 0, 'start_time': time.strftime("%H:%M:%S"),
            'stop_time': time.strftime("%H:%M:%S"),
            'sn': '{}10'.format(sn),
            'fixture_id': 10, 'test_head_id': 10, 'list_of_failing_tests': '', 'failure_message': ''}
    # mes.update_test_value_to_mes(data)
    mes.get_SIP_X_num(sn)