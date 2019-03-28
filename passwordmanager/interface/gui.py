import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QLineEdit,
                             QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel, QDialog,
                             QToolBar, QGroupBox, QGridLayout, QDialogButtonBox, QHBoxLayout)
from passwordmanager.src.password_manager import UserError
from passwordmanager.interface.mainwindow import *


class CreateAccount(QDialog):
    pass


class Login(QDialog):
    def __init__(self, pm, parent=None):
        super(Login, self).__init__(parent)
        self.pm = pm
        self.name_label = QLabel('account name:', self)
        self.name_field = QLineEdit(self)
        self.pass_label = QLabel('password name:', self)
        self.pass_field = QLineEdit(self)
        self.login_button = QPushButton('login', self)
        self.login_button.clicked.connect(self.handle_login)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.handle_cancel)
        
        grid_layout = QGridLayout(self)
        grid_layout.addWidget(self.name_label, 0, 0)
        grid_layout.addWidget(self.name_field, 0, 1)
        grid_layout.addWidget(self.pass_label, 1, 0)
        grid_layout.addWidget(self.pass_field, 1, 1)
        grid_layout.addWidget(self.login_button, 2, 0)
        grid_layout.addWidget(self.cancel_button, 2, 1)

    def handle_login(self):
        try:
            self.pm.login(self.name_field.text(), self.pass_field.text())
            self.accept()
        except UserError as err:
            QMessageBox.warning(self, 'Error', str(err))

    def handle_cancel(self):
        self.close()


class AddRow(QDialog):
    def __init__(self, pm, parent=None):
        super(AddRow, self).__init__(parent)
        self.pm = pm
        self.name_label = QLabel('*account name:', self)
        self.name_field = QLineEdit(self)
        self.email_label = QLabel('*email:', self)
        self.email_field = QLineEdit(self)
        self.password_label = QLabel('*password:', self)
        self.password_field = QLineEdit(self)
        self.url_label = QLabel('URL:', self)
        self.url_field = QLineEdit(self)
        self.add_button = QPushButton('add', self)
        self.add_button.clicked.connect(self.handle_add)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.handle_cancel)

        layout = QGridLayout(self)
        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.name_field, 0, 1)
        layout.addWidget(self.email_label, 1, 0)
        layout.addWidget(self.email_field, 1, 1)
        layout.addWidget(self.password_label, 2, 0)
        layout.addWidget(self.password_field, 2, 1)
        layout.addWidget(self.url_label, 3, 0)
        layout.addWidget(self.url_field, 3, 1)
        layout.addWidget(self.add_button, 4, 0)
        layout.addWidget(self.cancel_button, 4, 1)

    def handle_add(self):
        if self.name_field.text() and self.email_field.text() and self.password_field.text():
            self.pm.add_user_entry(
                self.name_field.text(),
                self.email_field.text(),
                self.password_field.text(),
                self.url_field.text()
            )
            self.accept()
        else:
            pass
    
    def handle_cancel(self):
        self.close()


class Window(QMainWindow):
    def __init__(self, pm, parent=None):
        super(Window, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pm = pm
        self.setup_table()

    def setup_table(self):
        account_table = self.pm.retrieve_table()
        self.ui.tableWidget.setRowCount(len(account_table)+1)
        index = 0
        for account in account_table:
            groupBox = QGroupBox()
            groupBox.setGeometry(QtCore.QRect(100, 330, 100, 50))
            groupBox.setObjectName("groupBox")
            pushButton_3 = QPushButton(groupBox)
            pushButton_3.setGeometry(QtCore.QRect(0, 25, 100, 25))
            pushButton_3.setText('REMOVE')
            pushButton_4 = QPushButton(groupBox)
            pushButton_4.setGeometry(QtCore.QRect(0, 0, 100, 25))
            pushButton_4.setText('MODIFY')

            self.ui.tableWidget.setCellWidget(index, 0, groupBox)
            self.ui.tableWidget.setItem(index, 1, QTableWidgetItem(account['name']))
            self.ui.tableWidget.setItem(index, 2, QTableWidgetItem(account['email']))
            self.ui.tableWidget.setItem(index, 3, QTableWidgetItem(account['password']))
            self.ui.tableWidget.setItem(index, 4, QTableWidgetItem(account['url']))
            index += 1

        add_account_button = QPushButton('ADD')
        add_account_button.clicked.connect(self.add_dialog)
        self.ui.tableWidget.setCellWidget(index, 0, add_account_button)
        return self.ui.tableWidget
    
    def add_dialog(self):
        add_dialog = AddRow(self.pm)
        if add_dialog.exec_() == QDialog.Accepted:
            self.setup_table


def run(args, pm):
    app = QApplication(args)
    login = Login(pm)

    if login.exec_() == QDialog.Accepted:
        window = Window(pm)
        window.show()
        sys.exit(app.exec_())
