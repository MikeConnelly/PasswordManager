import sys
import os
from whoosh.fields import Schema, TEXT, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser, FuzzyTermPlugin
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QLineEdit,
                             QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel, QDialog,
                             QToolBar, QGroupBox, QGridLayout, QDialogButtonBox, QHBoxLayout)
from passwordmanager.src.password_manager import UserError, AccountError
from passwordmanager.interface.mainwindow import *


class CreateAccount(QDialog):
    def __init__(self, pm, parent=None):
        super(CreateAccount, self).__init__(parent)
        self.pm = pm
        self.name_label = QLabel('account name:', self)
        self.name_field = QLineEdit(self)
        self.pass_label = QLabel('password name:', self)
        self.pass_field = QLineEdit(self)
        self.pass_field.setEchoMode(QLineEdit.Password)
        self.confirm_pass_label = QLabel('confirm password:', self)
        self.confirm_pass_field = QLineEdit(self)
        self.confirm_pass_field.setEchoMode(QLineEdit.Password)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.handle_cancel)
        self.register_button = QPushButton('create account', self)
        self.register_button.clicked.connect(self.handle_register)
        self.error_message = QLabel('', self)

        grid_layout = QGridLayout(self)
        grid_layout.addWidget(self.name_label, 0, 0)
        grid_layout.addWidget(self.name_field, 0, 1)
        grid_layout.addWidget(self.pass_label, 1, 0)
        grid_layout.addWidget(self.pass_field, 1, 1)
        grid_layout.addWidget(self.confirm_pass_label, 2, 0)
        grid_layout.addWidget(self.confirm_pass_field, 2, 1)
        grid_layout.addWidget(self.register_button, 3, 0)
        grid_layout.addWidget(self.cancel_button, 3, 1)
        grid_layout.addWidget(self.error_message, 4, 0, 1, 2)

    def handle_register(self):
        try:
            if self.pass_field.text() == self.confirm_pass_field.text():
                self.pm.create_user_and_login(self.name_field.text(), self.pass_field.text())
                self.accept()
            else:
                self.error_message.setText('password do not match')
        except UserError as err:
            self.error_message.setText(str(err))

    def handle_cancel(self):
        self.close()


class Login(QDialog):
    def __init__(self, pm, parent=None):
        super(Login, self).__init__(parent)
        self.pm = pm
        self.name_label = QLabel('account name:', self)
        self.name_field = QLineEdit(self)
        self.pass_label = QLabel('password name:', self)
        self.pass_field = QLineEdit(self)
        self.pass_field.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('login', self)
        self.login_button.clicked.connect(self.handle_login)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.handle_cancel)
        self.create_button = QPushButton('create account', self)
        self.create_button.clicked.connect(self.handle_create)
        self.error_message = QLabel('', self)

        grid_layout = QGridLayout(self)
        grid_layout.addWidget(self.name_label, 0, 0)
        grid_layout.addWidget(self.name_field, 0, 1)
        grid_layout.addWidget(self.pass_label, 1, 0)
        grid_layout.addWidget(self.pass_field, 1, 1)
        grid_layout.addWidget(self.login_button, 2, 0)
        grid_layout.addWidget(self.cancel_button, 2, 1)
        grid_layout.addWidget(self.create_button, 3, 0)
        grid_layout.addWidget(self.error_message, 4, 0, 1, 2)

    def handle_login(self):
        try:
            self.pm.login(self.name_field.text(), self.pass_field.text())
            self.accept()
        except UserError as err:
            QMessageBox.warning(self, 'Error', str(err))

    def handle_cancel(self):
        self.close()

    def handle_create(self):
        self.hide()
        create = CreateAccount(self.pm)
        if create.exec_() == QDialog.Accepted:
            self.accept()


class AddRowDialog(QDialog):
    def __init__(self, pm, parent=None):
        super(AddRowDialog, self).__init__(parent)
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
        self.error_message = QLabel('', self)

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
        layout.addWidget(self.error_message, 5, 0, 1, 2)

    def handle_add(self):
        try:
            if self.name_field.text() and self.email_field.text() and self.password_field.text():
                self.pm.add_user_entry(
                    self.name_field.text(),
                    self.email_field.text(),
                    self.password_field.text(),
                    self.url_field.text()
                )
                self.accept()
        except AccountError as err:
            self.error_message.setText(str(err))

    def handle_cancel(self):
        self.close()


class ModifyDialog(QDialog):
    def __init__(self, pm, account, parent=None):
        super(ModifyDialog, self).__init__(parent)
        self.pm = pm
        self.account = account
        self.name_label = QLabel('*account name:', self)
        self.name_field = QLineEdit(self)
        self.name_field.setText(account['name'])
        self.email_label = QLabel('*email:', self)
        self.email_field = QLineEdit(self)
        self.email_field.setText(account['email'])
        self.password_label = QLabel('*password:', self)
        self.password_field = QLineEdit(self)
        self.password_field.setText(account['password'])
        self.url_label = QLabel('URL:', self)
        self.url_field = QLineEdit(self)
        self.url_field.setText(account['url'])
        self.modify_button = QPushButton('modify', self)
        self.modify_button.clicked.connect(self.handle_modify)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.handle_cancel)
        self.error_message = QLabel('', self)

        layout = QGridLayout(self)
        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.name_field, 0, 1)
        layout.addWidget(self.email_label, 1, 0)
        layout.addWidget(self.email_field, 1, 1)
        layout.addWidget(self.password_label, 2, 0)
        layout.addWidget(self.password_field, 2, 1)
        layout.addWidget(self.url_label, 3, 0)
        layout.addWidget(self.url_field, 3, 1)
        layout.addWidget(self.modify_button, 4, 0)
        layout.addWidget(self.cancel_button, 4, 1)
        layout.addWidget(self.error_message, 5, 0, 1, 2)

    def handle_modify(self):
        try:
            if self.name_field.text() and self.email_field.text() and self.password_field.text():
                if self.name_field.text() != self.account['name']:
                    self.pm.change_entry(self.account, 'name', self.name_field.text())
                if self.email_field.text() != self.account['email']:
                    self.pm.change_entry(self.account, 'email', self.email_field.text())
                if self.password_field.text() != self.account['password']:
                    self.pm.change_entry(self.account, 'password', self.password_field.text())
                if self.url_field.text() != self.account['url']:
                    self.pm.change_entry(self.account, 'url', self.url_field.text())
                self.accept()
        except AccountError as err:
            self.error_message.setText(str(err))

    def handle_cancel(self):
        self.close()


class Window(QMainWindow):
    """class docstring"""

    def __init__(self, pm, parent=None):
        super(Window, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pm = pm
        self.setup_table()
        self.setup_tools()

    def setup_table(self, results=[]):
        if results == []:
            account_table = self.pm.retrieve_table()
        else:
            account_table = results
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(len(account_table))
        index = 0
        for account in account_table:
            print(account)
            self.ui.tableWidget.setItem(index, 0, QTableWidgetItem(account['name']))
            self.ui.tableWidget.setItem(index, 1, QTableWidgetItem(account['email']))
            self.ui.tableWidget.setItem(index, 2, QTableWidgetItem(account['password']))
            self.ui.tableWidget.setItem(index, 3, QTableWidgetItem(account['url']))
            index += 1

    def setup_tools(self):
        self.ui.remove_account_button.clicked.connect(lambda: self.handle_remove(self.ui.tableWidget.selectedItems()))
        self.ui.modify_account_button.clicked.connect(lambda: self.handle_modify(self.ui.tableWidget.selectedItems()))
        self.ui.add_account_button.clicked.connect(self.add_dialog)

        account_table = self.pm.retrieve_table()
        schema = Schema(name=TEXT(stored=True), email=TEXT(stored=True), password=STORED, url=STORED)
        if not os.path.exists('index'):
            os.mkdir('index')
        ix = create_in('index', schema)
        writer = ix.writer()
        for account in account_table:
            writer.add_document(name=account['name'], email=account['email'], password=account['password'], url=account['url'])
        writer.commit()
        self.ui.search_bar.textEdited.connect(lambda: self.handle_search(self.ui.search_bar.text()))

    def add_dialog(self):
        add_dialog = AddRowDialog(self.pm)
        if add_dialog.exec_() == QDialog.Accepted:
            self.setup_table()

    def handle_modify(self, selected):
        if selected:
            account = {
                'name': selected[0].text(),
                'email': selected[1].text(),
                'password': selected[2].text(),
                'url': selected[3].text()
            }
            modify_dialog = ModifyDialog(self.pm, account)
            if modify_dialog.exec_() == QDialog.Accepted:
                self.setup_table()

    def handle_remove(self, selected):
        if selected:
            account = {
                'name': selected[0].text(),
                'email': selected[1].text(),
                'password': selected[2].text(),
                'url': selected[3].text()
            }
            msg = f"Are you sure you want to remove {account['name']}"
            choice = QMessageBox.question(self, 'Remove?', msg, QMessageBox.Yes, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.pm.remove_entry(account)
                self.setup_table()

    def handle_search(self, query):
        if query:
            ix = open_dir('index')
            with ix.searcher() as searcher:
                parser = MultifieldParser(['name', 'email'], ix.schema)
                parser.add_plugin(FuzzyTermPlugin())
                myquery = parser.parse(query + '~5')
                results = searcher.search(myquery)
                self.setup_table(results)
        else:
            self.setup_table()


def run(args, pm):
    app = QApplication(args)
    login = Login(pm)

    if login.exec_() == QDialog.Accepted:
        window = Window(pm)
        window.show()
        sys.exit(app.exec_())
