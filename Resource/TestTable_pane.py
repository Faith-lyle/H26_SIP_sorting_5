#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:Long.Hou
@file: TestTable_pane.py
@time: 2021/11/09 
@email:631176465@qq.com
"""
from Resource.UI import Test_Table
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt


class TestTableView(Test_Table.Ui_Form, QWidget):

    def __init__(self,test_items):
        super(TestTableView, self).__init__()
        self.setupUi(self)
        self.tableView.setEditTriggers(self.tableView.NoEditTriggers)
        self.data_model = None
        self.test_items = test_items
        self.data_model_init()


    def data_model_init(self):
        self.data_model = QStandardItemModel(6, 12, self)
        heard = ['TestItem','Upper','Lower','Slot1','Slot2','Slot3','Slot4','Slot5','Slot6','Slot7','Slot8','Slot9','Slot10']
        self.data_model.setColumnCount(len(heard))
        self.data_model.setRowCount(len(self.test_items))
        self.data_model.setHorizontalHeaderLabels(heard)
        for i,test_item_row in enumerate(self.test_items):
            test_item_rows = [ test_item_row.TestName, test_item_row.TestUpper,
                              test_item_row.TestLower,
                              test_item_row.TestValue,
                              test_item_row.TestResult]
            if test_item_row.isEnabled:
                for col in range(len(test_item_rows)):
                    item = QStandardItem(test_item_rows[col])
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setEditable(False)
                    self.data_model.setItem(i, col, item)
        self.tableView.setModel(self.data_model)
        self.tableView.setColumnWidth(0, 210)


    def add_data(self, row, col, value):
        item = QStandardItem(value)
        item.setTextAlignment(Qt.AlignCenter)
        # item.setTextAlignment(Qt.AlignVCenter)
        item.setEditable(False)
        self.data_model.setItem(row, col + 2, item)

    def change_item_font_color(self, row, col, color):
        item = self.data_model.item(row, col + 2)
        item.setForeground(QColor(color))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = TestTableView()
    win.resize(400, 300)
    win.setWindowTitle("test")
    win.show()
    sys.exit(app.exec_())
