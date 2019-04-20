import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, QLabel,
    QDialog, QComboBox, QGridLayout, QDialogButtonBox, QInputDialog, QVBoxLayout, QHBoxLayout,
    QMenu, QAction, QColorDialog, QStatusBar, QActionGroup
)
from passwordmanager.src.password_manager import generate_password, UserError, AccountError
from passwordmanager.interface.mainwindow import *


class CreateAccount(QDialog):
    def __init__(self, pm, parent=None):
        super(CreateAccount, self).__init__(parent)
        self.pm = pm
        self.name_label = QLabel('account name:', self)
        self.name_field = QLineEdit(self)
        self.pass_label = QLabel('password:', self)
        self.pass_field = QLineEdit(self)
        self.pass_field.setEchoMode(QLineEdit.Password)
        self.confirm_pass_label = QLabel('confirm password:', self)
        self.confirm_pass_field = QLineEdit(self)
        self.confirm_pass_field.setEchoMode(QLineEdit.Password)
        self.register_button = QPushButton('create account', self)
        self.register_button.clicked.connect(self.handle_register)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.close)
        self.error_message = QLabel('', self)
        self.setWindowTitle('Create Account')
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowTitleHint
        )

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.name_label, 0, 0)
        grid_layout.addWidget(self.name_field, 0, 1)
        grid_layout.addWidget(self.pass_label, 1, 0)
        grid_layout.addWidget(self.pass_field, 1, 1)
        grid_layout.addWidget(self.confirm_pass_label, 2, 0)
        grid_layout.addWidget(self.confirm_pass_field, 2, 1)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.register_button)
        horizontal_layout.addWidget(self.cancel_button)

        vertical_layout = QVBoxLayout(self)
        vertical_layout.addLayout(grid_layout)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(self.error_message)

    def handle_register(self):
        try:
            if self.pass_field.text() == self.confirm_pass_field.text():
                self.pm.create_user_and_login(self.name_field.text(), self.pass_field.text())
                self.accept()
            else:
                self.error_message.setText('password do not match')
        except UserError as err:
            self.error_message.setText(str(err))


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
        self.cancel_button.clicked.connect(self.close)
        self.create_button = QPushButton('create account', self)
        self.create_button.clicked.connect(self.handle_create)
        self.error_message = QLabel('', self)
        self.setWindowTitle('Login')
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowTitleHint
        )

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.name_label, 0, 0)
        grid_layout.addWidget(self.name_field, 0, 1)
        grid_layout.addWidget(self.pass_label, 1, 0)
        grid_layout.addWidget(self.pass_field, 1, 1)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.login_button)
        horizontal_layout.addWidget(self.cancel_button)
        horizontal_layout.addWidget(self.create_button)

        vertical_layout = QVBoxLayout(self)
        vertical_layout.addLayout(grid_layout)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(self.error_message)

    def handle_login(self):
        try:
            self.pm.login(self.name_field.text(), self.pass_field.text())
            self.accept()
        except UserError as err:
            self.error_message.setText(str(err))

    def handle_create(self):
        self.hide()
        create = CreateAccount(self.pm)
        if create.exec_() == QDialog.Accepted:
            self.accept()


class AddRowDialog(QDialog):
    def __init__(self, pm, parent=None):
        super(AddRowDialog, self).__init__(parent)
        self.pm = pm
        self.cols = self.pm.get_all_columns()
        self.labels, self.fields = ([], [])
        for col in self.cols:
            self.labels.append(QLabel(f"{col}:", self))
            self.fields.append(QLineEdit(self))
            if col == 'password':
                pass_field = self.fields[-1]
                self.generate_password_button = QPushButton('G', self)
                self.generate_password_button.setMinimumSize(20, 20)
                self.generate_password_button.setMaximumSize(20, 20)
                self.generate_password_button.clicked.connect(
                    lambda: pass_field.setText(generate_password(16))
                )
        self.add_button = QPushButton('add', self)
        self.add_button.clicked.connect(self.handle_add)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.close)
        self.error_message = QLabel('', self)
        self.setWindowTitle('Add Account')
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowTitleHint
        )

        grid_layout = QGridLayout()
        for i in range(len(self.cols)):
            grid_layout.addWidget(self.labels[i], i, 0)
            grid_layout.addWidget(self.fields[i], i, 1)
            if self.cols[i] == 'password':
                grid_layout.addWidget(self.generate_password_button, i, 2)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.add_button)
        horizontal_layout.addWidget(self.cancel_button)

        vertical_layout = QVBoxLayout(self)
        vertical_layout.addLayout(grid_layout)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(self.error_message)

    def handle_add(self):
        if len(self.cols) > 4:
            custom = {col: self.fields[index].text() for index, col in enumerate(self.cols[4:], 4)}
        try:
            if self.fields[0].text() and self.fields[1].text() and self.fields[2].text():
                self.pm.add_user_entry(
                    self.fields[0].text(),
                    self.fields[1].text(),
                    self.fields[2].text(),
                    self.fields[3].text(),
                    custom
                )
                self.accept()
            else:
                self.error_message.setText('name, email, and password fields required')
        except AccountError as err:
            self.error_message.setText(str(err))


class ModifyDialog(QDialog):
    def __init__(self, pm, account_list, parent=None):
        super(ModifyDialog, self).__init__(parent)
        self.pm = pm
        self.account = {}
        self.labels, self.fields = ([], [])
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
            if col == 'password':
                pass_field = self.fields[-1]
                self.generate_password_button = QPushButton('G', self)
                self.generate_password_button.setMinimumSize(20, 20)
                self.generate_password_button.setMaximumSize(20, 20)
                self.generate_password_button.clicked.connect(
                    lambda: pass_field.setText(generate_password(16))
                )
        self.modify_button = QPushButton('modify', self)
        self.modify_button.clicked.connect(self.handle_modify)
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self.close)
        self.error_message = QLabel('', self)
        self.setWindowTitle('Modify Account')
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowTitleHint
        )

        layout = QGridLayout(self)
        for i in range(len(self.cols)):
            layout.addWidget(self.labels[i], i, 0)
            layout.addWidget(self.fields[i], i, 1)
            if self.cols[i] == 'password':
                layout.addWidget(self.generate_password_button, i, 2)
        layout.addWidget(self.modify_button, i+1, 0)
        layout.addWidget(self.cancel_button, i+1, 1)
        layout.addWidget(self.error_message, i+2, 0, 1, 2)

    def handle_modify(self):
        try:
            if self.fields[0].text() and self.fields[1].text() and self.fields[2].text():
                cols, new_fields = ([], [])
                for index, col in enumerate(self.cols):
                    if col in self.account:
                        if self.fields[index].text() != self.account[col]:
                            cols.append(col)
                            new_fields.append(self.fields[index].text())
                    else:
                        cols.append(col)
                        new_fields.append(self.fields[index].text())
                self.pm.change_entry(self.account['name'], cols, new_fields)
                self.accept()
            else:
                self.error_message.setText('name, email, and password fields required')
        except AccountError as err:
            self.error_message.setText(str(err))


class RemoveColumnDialog(QDialog):
    def __init__(self, pm, parent=None):
        super(RemoveColumnDialog, self).__init__(parent)
        self.pm = pm
        self.combo = QComboBox(self)
        cols = ['']
        cols.extend(self.pm.get_custom_columns())
        self.combo.addItems(cols)
        self.message = QLabel('', self)
        self.combo.currentTextChanged.connect(self.update_message)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close, self)
        self.buttons.setEnabled(False)
        self.buttons.accepted.connect(self.handle_remove)
        self.buttons.rejected.connect(self.close)
        self.setWindowTitle('Remove Column')
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowTitleHint
        )

        vertical_layout = QVBoxLayout(self)
        vertical_layout.addWidget(self.combo)
        vertical_layout.addWidget(self.message)
        vertical_layout.addWidget(self.buttons)

    def update_message(self):
        if self.combo.itemText(0) == '':
            self.combo.removeItem(0)
        self.message.setText(f"Remove {self.combo.currentText()} column?")
        self.buttons.setEnabled(True)

    def handle_remove(self):
        self.pm.remove_column(self.combo.currentText())
        self.accept()


class RenameColumnDialog(QDialog):
    def __init__(self, pm, parent=None):
        super(RenameColumnDialog, self).__init__(parent)
        self.pm = pm
        self.column_to_rename = QLabel('column to rename:', self)
        self.combo = QComboBox(self)
        cols = ['']
        cols.extend(self.pm.get_custom_columns())
        self.combo.addItems(cols)
        self.combo.currentTextChanged.connect(self.handle_combo_change)
        self.new_name_label = QLabel('new name:', self)
        self.new_name_field = QLineEdit(self)
        self.new_name_field.textChanged.connect(self.handle_text_change)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close, self)
        self.buttons.setEnabled(False)
        self.buttons.accepted.connect(self.handle_rename)
        self.buttons.rejected.connect(self.close)
        self.setWindowTitle('Rename Column')
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowTitleHint
        )

        grid_layout = QGridLayout(self)
        grid_layout.addWidget(self.column_to_rename, 0, 0)
        grid_layout.addWidget(self.combo, 0, 1)
        grid_layout.addWidget(self.new_name_label, 1, 0)
        grid_layout.addWidget(self.new_name_field, 1, 1)
        grid_layout.addWidget(self.buttons, 2, 0, 1, 2)

    def handle_combo_change(self):
        if self.combo.itemText(0) == '':
            self.combo.removeItem(0)
        if self.new_name_field.text() != '':
            self.buttons.setEnabled(True)

    def handle_text_change(self):
        if self.new_name_field.text() != '' and self.combo.itemText(0) != '':
            self.buttons.setEnabled(True)
        else:
            self.buttons.setEnabled(False)

    def handle_rename(self):
        self.pm.rename_column(self.combo.currentText(), self.new_name_field.text())
        self.accept()


class FilterMenu(QMenu):
    def __init__(self, cols, default, parent=None):
        super(FilterMenu, self).__init__(parent)
        self.ag = QActionGroup(self, exclusive=True)
        self.setup_menu(cols)
        self.set_default(default)

    def setup_menu(self, cols):
        for col in cols:
            action = self.ag.addAction(QAction(col, self))
            action.setCheckable(True)
            self.addAction(action)

    def set_default(self, default):
        for action in self.actions():
            if action.text() == default:
                action.toggle()

    def get_checked(self):
        for action in self.actions():
            if action.isChecked():
                return action.text()


class Window(QMainWindow):
    """Main GUI window"""

    def __init__(self, pm, parent=None):
        super(Window, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pm = pm
        self.setup_table()
        self.setup_tools()

    def setup_table(self, results=None):
        self.ui.tableWidget.clearContents()
        account_table = results if results is not None else self.pm.retrieve_table()
        columns = self.pm.get_all_columns()
        self.ui.tableWidget.setRowCount(len(account_table))
        self.ui.tableWidget.setColumnCount(len(columns))
        for index, col in enumerate(columns):
            item = QTableWidgetItem()
            self.ui.tableWidget.setHorizontalHeaderItem(index, item)
            item.setText(QtCore.QCoreApplication.translate("MainWindow", col))
        for index, account in enumerate(account_table):
            for col_num, col in enumerate(columns):
                if col in account:
                    item = QTableWidgetItem(account[col])
                    self.ui.tableWidget.setItem(index, col_num, item)
                else:
                    item = QTableWidgetItem('')
                    self.ui.tableWidget.setItem(index, col_num, item)
                color = get_color_object(self.pm, account['name'])
                if color:
                    item.setBackground(color)

    def setup_tools(self):
        self.ui.add_account_button.clicked.connect(self.handle_add_account)
        self.ui.modify_account_button.clicked.connect(self.handle_modify)
        self.ui.remove_account_button.clicked.connect(self.handle_remove_account)
        self.ui.add_column_button.clicked.connect(self.handle_add_column)
        self.ui.rename_column_button.clicked.connect(self.handle_rename_column)
        self.ui.remove_column_button.clicked.connect(self.handle_remove_column)
        self.ui.reset_button.clicked.connect(self.handle_reset)
        self.ui.search_bar.textEdited.connect(self.handle_search)
        self.filter_menu = FilterMenu(self.pm.get_all_columns(), 'name')
        self.ui.filter_search_button.setMenu(self.filter_menu)

        modify_action = QAction('modify account', self)
        modify_action.triggered.connect(self.handle_modify)
        remove_action = QAction('remove account', self)
        remove_action.triggered.connect(self.handle_remove_account)
        color_action = QAction('color row', self)
        color_action.triggered.connect(self.color_row)
        self.ui.tableWidget.addAction(modify_action)
        self.ui.tableWidget.addAction(remove_action)
        self.ui.tableWidget.addAction(color_action)
        self.ui.tableWidget.itemSelectionChanged.connect(self.set_button_state)
        self.set_button_state()

    def set_button_state(self):
        if self.ui.tableWidget.selectedItems():
            self.ui.modify_account_button.setEnabled(True)
            self.ui.remove_account_button.setEnabled(True)
            self.ui.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        else:
            self.ui.modify_account_button.setEnabled(False)
            self.ui.remove_account_button.setEnabled(False)
            self.ui.tableWidget.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        if self.pm.get_custom_columns():
            self.ui.rename_column_button.setEnabled(True)
            self.ui.remove_column_button.setEnabled(True)
        else:
            self.ui.rename_column_button.setEnabled(False)
            self.ui.remove_column_button.setEnabled(False)

    def handle_add_account(self):
        add_dialog = AddRowDialog(self.pm)
        if add_dialog.exec_() == QDialog.Accepted:
            self.setup_table()

    def handle_modify(self):
        selected = self.ui.tableWidget.selectedItems()
        if selected:
            account_list = [field.text() for field in selected]
            modify_dialog = ModifyDialog(self.pm, account_list)
            if modify_dialog.exec_() == QDialog.Accepted:
                self.setup_table()

    def handle_remove_account(self):
        selected = self.ui.tableWidget.selectedItems()
        if selected:
            account_name = selected[0].text()
            msg = f"Are you sure you want to remove {account_name}"
            choice = QMessageBox.question(self, 'Remove?', msg, QMessageBox.Yes, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.pm.remove_entry(account_name)
                self.setup_table()

    def handle_add_column(self):
        text, ok_pressed = QInputDialog.getText(self, 'Add a column', 'name:', QLineEdit.Normal, '')
        try:
            if ok_pressed and text != '':
                self.pm.add_column(text)
                self.setup_table()
        except UserError:
            pass

    def handle_rename_column(self):
        rename_column_dialog = RenameColumnDialog(self.pm)
        if rename_column_dialog.exec_() == QDialog.Accepted:
            self.setup_table()
            self.set_button_state()

    def handle_remove_column(self):
        remove_column_dialog = RemoveColumnDialog(self.pm)
        if remove_column_dialog.exec_() == QDialog.Accepted:
            self.setup_table()
            self.set_button_state()

    def handle_reset(self):
        quit_msg = 'Are you sure you want to reset your table?'
        confirm = QMessageBox\
                .question(self, 'Reset Table', quit_msg, QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.pm.reset_all()
            self.setup_table()

    def handle_search(self):
        query = self.ui.search_bar.text()
        filter_field = self.filter_menu.get_checked()
        if query:
            results = []
            for account in self.pm.retrieve_table():
                if filter_field in account and query in account[filter_field]:
                    results.append(account)
            self.setup_table(results)
        else:
            self.setup_table()

    def color_row(self):
        selected = self.ui.tableWidget.selectedItems()
        if selected:
            row_name = selected[0].text()
            curr_color = get_color_object(self.pm, row_name)
            color_dialog = QColorDialog.getColor(curr_color) if curr_color else QColorDialog.getColor()
            if color_dialog.isValid():
                rgba = color_dialog.getRgb()
                color = ','.join(str(x) for x in rgba)
                self.pm.color_row(row_name, color)
                self.setup_table()


def get_color_object(pm, name):
    color = pm.get_row_color(name)
    rgba = None
    if color:
        rgba = [int(x) for x in color.split(',')]
    return QtGui.QColor(*rgba) if rgba else None


def run(args, pm):
    app = QApplication(args)
    login = Login(pm)

    if login.exec_() == QDialog.Accepted:
        window = Window(pm)
        window.show()
        sys.exit(app.exec_())
