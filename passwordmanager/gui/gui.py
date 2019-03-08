import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QLineEdit, 
                             QPushButton, QVBoxLayout, QMessageBox)
from passwordmanager import app
from passwordmanager.src.password_manager import UserError


class Login(QtWidgets.QDialog):

    def __init__(self, pm, parent=None):
        super(Login, self).__init__(parent)
        self.pm = pm

        self.name_field = QLineEdit(self)
        self.pass_field = QLineEdit(self)
        self.login_button = QPushButton('login', self)
        self.login_button.clicked.connect(self.handle_login)

        layout = QVBoxLayout(self)
        layout.addWidget(self.name_field)
        layout.addWidget(self.pass_field)
        layout.addWidget(self.login_button)

    def handle_login(self):
        
        try:
            self.pm.login(self.name_field.text(), self.pass_field.text())
            self.accept()
        except UserError as err:
            QMessageBox.warning(self, 'Error', str(err))


class Window(QtWidgets.QMainWindow):

    def __init__(self, pm, parent=None):
        super(Window, self).__init__(parent)
        self.setGeometry(750, 400, 500, 200)

        self.pm = pm
        self.create_table()

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_widget)

    def create_table(self):
        account_table = self.pm.retrieve_table()

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(0, 0, 500, 200)
        self.table_widget.setRowCount(len(account_table))
        self.table_widget.setColumnCount(4)

        index = 0
        for account in account_table:
            self.table_widget.setItem(index, 0, QTableWidgetItem(account['name']))
            self.table_widget.setItem(index, 1, QTableWidgetItem(account['email']))
            self.table_widget.setItem(index, 2, QTableWidgetItem(account['password']))
            self.table_widget.setItem(index, 3, QTableWidgetItem(account['url']))
            index += 1


def run(args, pm):

    app = QApplication(args)
    login = Login(pm)

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = Window(pm)
        window.show()
        sys.exit(app.exec_())
