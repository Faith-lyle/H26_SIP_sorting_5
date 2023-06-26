#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: TestLog_pane.py
@time: 2021/11/09 
@email:631176465@qq.com
"""
# !usr/bin/env python
# -*- coding:utf-8 _*-
from PyQt5.QtGui import QTextCursor

""" 
@author:Long.Hou
@file: TestTable_pane.py 
@time: 2021/11/09 
@email:631176465@qq.com
"""
from Resource.UI import TestLogUI
from PyQt5.QtWidgets import QWidget


class TestLogView(TestLogUI.Ui_Form, QWidget):

    def __init__(self):
        super(TestLogView, self).__init__()
        self.setupUi(self)

    def set_slot_title(self, title):
        self.lb_slot_name.setText(title)

    def append_test(self, text):
        self.tet_log.append(text)

    def get_text_side(self):
        return len(self.tet_log.toPlainText())

    def set_text(self, text):
        self.tet_log.setText(text)

    def set_flag_to_end(self):
        self.tet_log.moveCursor(QTextCursor.End)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = TestLogView()
    win.resize(400, 300)
    win.setWindowTitle("test")
    win.show()
    sys.exit(app.exec_())
