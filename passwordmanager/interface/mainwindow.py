# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 581)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralWidget)
        self.tableWidget.setEnabled(True)
        self.tableWidget.setGeometry(QtCore.QRect(0, 60, 701, 521))
        self.tableWidget.setAutoScroll(True)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(100)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(100)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(50)
        self.tableWidget.verticalHeader().setMinimumSectionSize(50)
        self.search_bar = QtWidgets.QLineEdit(self.centralWidget)
        self.search_bar.setGeometry(QtCore.QRect(210, 10, 121, 41))
        self.search_bar.setObjectName("search_bar")
        self.modify_account_button = QtWidgets.QPushButton(self.centralWidget)
        self.modify_account_button.setGeometry(QtCore.QRect(60, 10, 41, 41))
        self.modify_account_button.setObjectName("modify_account_button")
        self.remove_account_button = QtWidgets.QPushButton(self.centralWidget)
        self.remove_account_button.setGeometry(QtCore.QRect(110, 10, 41, 41))
        self.remove_account_button.setObjectName("remove_account_button")
        self.add_account_button = QtWidgets.QPushButton(self.centralWidget)
        self.add_account_button.setGeometry(QtCore.QRect(10, 10, 41, 41))
        self.add_account_button.setObjectName("add_account_button")
        self.add_column_button = QtWidgets.QPushButton(self.centralWidget)
        self.add_column_button.setGeometry(QtCore.QRect(160, 10, 41, 41))
        self.add_column_button.setObjectName("add_column_button")
        MainWindow.setCentralWidget(self.centralWidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Account"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Email"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Password"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "URL"))
        self.search_bar.setPlaceholderText(_translate("MainWindow", "Search"))
        self.modify_account_button.setText(_translate("MainWindow", "M"))
        self.remove_account_button.setText(_translate("MainWindow", "R"))
        self.add_account_button.setText(_translate("MainWindow", "A"))
        self.add_column_button.setText(_translate("MainWindow", "C"))


