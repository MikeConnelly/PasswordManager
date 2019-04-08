import sys
import os
from whoosh.fields import Schema, TEXT, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, FuzzyTermPlugin
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QLineEdit,
                             QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel, QDialog,
                             QToolBar, QGroupBox, QGridLayout, QDialogButtonBox, QHBoxLayout, QInputDialog)
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


'''
get list of all field
loop through all self.fields, create field and label for each one
map col to those in dictionary, keep track of indices and put in layout
'''
class AddRowDialog(QDialog):
    def __init__(self, pm, parent=None):
        super(AddRowDialog, self).__init__(parent)
        self.pm = pm
        self.cols = self.pm.get_all_columns()
        self.labels = []
        self.fields = []
        for col in self.cols:
            self.labels.append(QLabel(f"{col}:", self))
            self.fields.append(QLineEdit(self))
        self.add_button = QPushButton('add', self)
        self.add_button.clicked.connect(self.handle_add)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.handle_cancel)
        self.error_message = QLabel('', self)

        layout = QGridLayout(self)
        for i in range(len(self.cols)):
            layout.addWidget(self.labels[i], i, 0)
            layout.addWidget(self.fields[i], i, 1)
        layout.addWidget(self.add_button, i+1, 0)
        layout.addWidget(self.cancel_button, i+1, 1)
        layout.addWidget(self.error_message, i+2, 0, 1, 2)

    def handle_add(self):
        custom_cols = {}
        if len(self.cols) > 4:
            for index, col in enumerate(self.cols[4:], 4):
                print(f"{index}, {col}")
                custom_cols[col] = self.fields[index].text()
        try:
            if self.fields[0].text() and self.fields[1].text() and self.fields[2].text():
                self.pm.add_user_entry(
                    self.fields[0].text(),
                    self.fields[1].text(),
                    self.fields[2].text(),
                    self.fields[3].text(),
                    custom_cols
                )
                self.accept()
            else:
                self.error_message.setText('name, email, and password fields required')
        except AccountError as err:
            self.error_message.setText(str(err))

    def handle_cancel(self):
        self.close()


class ModifyDialog(QDialog):
    def __init__(self, pm, account_list, parent=None):
        super(ModifyDialog, self).__init__(parent)
        self.pm = pm
        self.account = {}
        self.labels = []
        self.fields = []
        self.cols = self.pm.get_all_columns()
        for index, col in enumerate(self.cols):
            if index < len(account_list) and account_list[index]:
                self.account[col] = account_list[index]
        for col in self.cols:
            self.labels.append(QLabel(f"{col}:", self))
            field = QLineEdit(self)
            if col in self.account:
                field.setText(self.account[col])
            self.fields.append(field)
        self.modify_button = QPushButton('modify', self)
        self.modify_button.clicked.connect(self.handle_modify)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.handle_cancel)
        self.error_message = QLabel('', self)

        layout = QGridLayout(self)
        for i in range(len(self.cols)):
            layout.addWidget(self.labels[i], i, 0)
            layout.addWidget(self.fields[i], i, 1)
        layout.addWidget(self.modify_button, i+1, 0)
        layout.addWidget(self.cancel_button, i+1, 1)
        layout.addWidget(self.error_message, i+2, 0, 1, 2)

    def handle_modify(self):
        try:
            if self.fields[0].text() and self.fields[1].text() and self.fields[2].text():
                for index, col in enumerate(self.cols):
                    if col in self.account:
                        if self.fields[index].text() != self.account[col]:
                            self.pm.change_entry(self.account, col, self.fields[index].text())
                    else:
                        self.pm.change_entry(self.account, col, self.fields[index].text())
                self.accept()
            else:
                self.error_message.setText('name, email, and password fields required')
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
        self.ui.tableWidget.clearContents()
        account_table = results or self.pm.retrieve_table()
        custom_cols = self.pm.user.custom_cols.split(',')
        self.ui.tableWidget.setRowCount(len(account_table))
        self.ui.tableWidget.setColumnCount(4 + len(custom_cols))
        col_num = 4
        for col in custom_cols:
            item = QTableWidgetItem()
            self.ui.tableWidget.setHorizontalHeaderItem(col_num, item)
            item.setText(QtCore.QCoreApplication.translate("MainWindow", col))
            col_num += 1
        index = 0
        for account in account_table:
            self.ui.tableWidget.setItem(index, 0, QTableWidgetItem(account['name']))
            self.ui.tableWidget.setItem(index, 1, QTableWidgetItem(account['email']))
            self.ui.tableWidget.setItem(index, 2, QTableWidgetItem(account['password']))
            self.ui.tableWidget.setItem(index, 3, QTableWidgetItem(account['url']))
            col_num = 4
            for col in custom_cols:
                if col in account:
                    self.ui.tableWidget.setItem(index, col_num, QTableWidgetItem(account[col]))
                else:
                    self.ui.tableWidget.setItem(index, col_num, QTableWidgetItem(''))
                col_num += 1
            index += 1

    def setup_tools(self):
        self.ui.remove_account_button.clicked.connect(lambda: self.handle_remove(self.ui.tableWidget.selectedItems()))
        self.ui.modify_account_button.clicked.connect(lambda: self.handle_modify(self.ui.tableWidget.selectedItems()))
        self.ui.add_account_button.clicked.connect(self.add_dialog)
        self.ui.add_column_button.clicked.connect(self.handle_add_column)

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
            account_list = []
            for field in selected:
                account_list.append(field.text())
            modify_dialog = ModifyDialog(self.pm, account_list)
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

    def handle_search(self, query, field='name'):
        if query:
            ix = open_dir('index')
            with ix.searcher() as searcher:
                parser = QueryParser(field, ix.schema)
                parser.add_plugin(FuzzyTermPlugin())
                myquery = parser.parse(query + '~5')
                results = searcher.search(myquery)
                self.setup_table(results)
        else:
            self.setup_table()

    def handle_add_column(self):
        text, ok = QInputDialog.getText(self, 'Add a column', 'name:', QLineEdit.Normal, '')
        try:
            if ok and text != '':
                self.pm.add_column(text)
                self.setup_table()
        except UserError:
            pass


def run(args, pm):
    app = QApplication(args)
    login = Login(pm)

    if login.exec_() == QDialog.Accepted:
        window = Window(pm)
        window.show()
        sys.exit(app.exec_())
