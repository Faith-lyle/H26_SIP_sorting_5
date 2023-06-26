#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: Xpanel_update.py 
@time: 2022/03/09 
@email:long.hou2@luxshare-ict.com
"""
import tkinter as tk
from Tools import mes
from tkinter import messagebox
import time


class Application(tk.Frame):
    def __init__(self, master=None):
        self.master = master
        tk.Frame.__init__(self, master)
        self.sn = tk.StringVar(self)
        self.MES = mes.Mes()
        self.sn.set(" ")
        self.UIinit()

    def UIinit(self):
        self.Title_UI()
        self.test_UI()
        self.LogUi()

    def LogUi(self):
        F1 = tk.Frame(self.master, heigh=100, bg="SkyBlue")
        tk.Label(F1, text="Author: Long.Hou", heigh=1, font=('Arial', 13), bg="SkyBlue", fg='red').pack(pady=5,
                                                                                                        side='right')
        tk.Label(F1, text="Luxshare-ict", heigh=1, font=('Arial', 17), bg="SkyBlue", fg='red').pack(pady=5, side='left')
        F1.pack(fill=tk.BOTH)

    def Title_UI(self):
        F1 = tk.Frame(self.master, heigh=200, )
        tk.Label(F1, text="H26 X板上传工具", heigh=1, font=('Arial', 21), fg='red').pack(pady=5, side='top')
        self.content_Frame = tk.Text(F1, height=15, relief='solid', borderwidth=1)
        self.content_Frame.pack(fill=tk.X, side='bottom')
        F1.pack(fill=tk.BOTH)

    def test_UI(self):
        F1 = tk.Frame(self.master, heigh=100)
        F1.pack(fill=tk.X)
        tk.Label(F1, text="SN:", width=3).grid(row=0, column=0, padx=30, pady=10)
        tk.Entry(F1, width=30, textvariable=self.sn).grid(row=0, column=1, padx=0, pady=10)
        self.lb = tk.Label(F1, text="PASS", bg="lime", width=8)
        self.lb.grid(row=0, column=3, pady=10)
        self.btn = tk.Button(F1, text='上传', width=5, command=self.update_X_info)
        self.btn.grid(row=0, column=2, padx=30, pady=10)

    def update_X_info(self):
        if len(self.sn.get()) > 10:
            self.btn.config(state='disabled')
            result, msg = self.MES.get_SIP_X_num(sn=self.sn.get().strip())
            if result:
                for i in msg:
                        self.update_result_to_mes(i)
            else:
                messagebox.showerror("information", 'Update data to MES failed, please tay again!\n')
                self.content_Frame.insert(tk.END, "[{}] Update data to MES failed, please tay again!\n".format(
                    time.strftime("%Y-%m-%d %H:%M:%S")))
                self.lb.config(text='FAIL', bg='red')
        self.btn.config(state='normal')

    def update_result_to_mes(self, slot):
        if slot > 9:
            sn = '{}{}'.format(self.sn.get().strip(), slot)
        else:
            sn = '{}0{}'.format(self.sn.get().strip(), slot)
        data = {"result": "PASS", 'audio_mode': '0', 'start_time': time.strftime("%H:%M:%S"),
                'stop_time': time.strftime("%H:%M:%S"),
                'sn': sn, 'fixture_id': slot, 'test_head_id': slot, 'list_of_failing_tests': "",
                'failure_message': ""}
        if not self.MES.update_test_value_to_mes(data):
            messagebox.showerror("information", 'Update data to MES failed, please tay again!\n')
            self.content_Frame.insert(tk.END, "[{}] Update data to MES failed, please tay again!\n".format(
                time.strftime("%Y-%m-%d %H:%M:%S")))
            self.lb.config(text='FAIL', bg='red')
        else:
            self.content_Frame.insert(tk.END, "[{}] Update data to MES success! sn:{}\n".format(
                time.strftime("%Y-%m-%d %H:%M:%S"), sn))
            self.lb.config(text='PASS', bg='lime')


if __name__ == '__main__':
    win = tk.Tk()
    win.title("H26 X板上传工具")
    win.geometry("600x360")
    win.resizable(0, 0)
    app = Application(master=win)
    win.mainloop()
