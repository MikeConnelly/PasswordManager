import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QLineEdit,
                             QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel, QDialog,
                             QToolBar)
from passwordmanager.src.password_manager import UserError
from passwordmanager.interface.mainwindow import *


class Login(QDialog):

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

'''
class Window(QMainWindow):

    def __init__(self, pm, parent=None):
        super(Window, self).__init__(parent)
        self.setGeometry(300, 200, 1400, 600)
        self.setWindowTitle('Password Manager')
        self.pm = pm

        toolbar = QToolBar('main toolbar')
        self.addToolBar(toolbar)

        welcome_label = QLabel('WELCOME ' + self.pm.user.username.upper())
        table_widget = self.create_table()

        layout = QVBoxLayout()
        layout.addWidget(welcome_label)
        layout.addWidget(table_widget)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def create_table(self):
        account_table = self.pm.retrieve_table()

        table_widget = QTableWidget()
        table_widget.setGeometry(50, 400, 500, 200)
        table_widget.setRowCount(len(account_table)+1)
        table_widget.setColumnCount(5)
        table_widget.columnWidth(100)
        table_widget.rowHeight(100)

        index = 0
        for account in account_table:
            modify_button = QPushButton('modify')
            remove_button = QPushButton('remove')
            layout = QVBoxLayout()
            layout.addWidget(modify_button)
            layout.addWidget(remove_button)
            first_col_widget = QWidget()
            first_col_widget.setLayout(layout)
            table_widget.setCellWidget(index, 0, first_col_widget)

            table_widget.setItem(index, 1, QTableWidgetItem(account['name']))
            table_widget.setItem(index, 2, QTableWidgetItem(account['email']))
            table_widget.setItem(index, 3, QTableWidgetItem(account['password']))
            table_widget.setItem(index, 4, QTableWidgetItem(account['url']))
            index += 1

        add_account_button = QPushButton('+')
        table_widget.setCellWidget(index, 0, add_account_button)

        return table_widget
'''

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
            modify_button = QPushButton('modify')
            remove_button = QPushButton('remove')
            layout = QVBoxLayout()
            layout.addWidget(modify_button)
            layout.addWidget(remove_button)
            first_col_widget = QWidget()
            first_col_widget.setLayout(layout)


            self.ui.tableWidget.setCellWidget(index, 0, first_col_widget)
            self.ui.tableWidget.setItem(index, 1, QTableWidgetItem(account['name']))
            self.ui.tableWidget.setItem(index, 2, QTableWidgetItem(account['email']))
            self.ui.tableWidget.setItem(index, 3, QTableWidgetItem(account['password']))
            self.ui.tableWidget.setItem(index, 4, QTableWidgetItem(account['url']))
            index += 1

        add_account_button = QPushButton('+')
        self.ui.tableWidget.setCellWidget(index, 0, add_account_button)

        return self.ui.tableWidget

def run(args, pm):

    app = QApplication(args)
    login = Login(pm)

    if login.exec_() == QDialog.Accepted:
        window = Window(pm)
        window.show()
        sys.exit(app.exec_())
