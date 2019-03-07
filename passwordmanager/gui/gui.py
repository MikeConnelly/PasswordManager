from PyQt5 import QtWidgets
import sys
from passwordmanager import app
from passwordmanager.src import password_manager, models


class Login(QtWidgets.QDialog):
    def __init__(self, pm, parent=None):
        super(Login, self).__init__(parent)
        self.pm = pm

        self.text_name = QtWidgets.QLineEdit(self)
        self.text_pass = QtWidgets.QLineEdit(self)
        self.button_login = QtWidgets.QPushButton('login', self)
        self.button_login.clicked.connect(self.handle_login)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.text_name)
        layout.addWidget(self.text_pass)
        layout.addWidget(self.button_login)

    def handle_login(self):
        
        user = self.pm.session.query(models.User).filter(models.User.username == self.text_name.text()).one()
        if user:
            if self.pm.crypto.decrypt(user.master_password) == self.text_pass.text():
                self.accept()
        if not self.Accepted:
            QtWidgets.QMessageBox.warning(self, 'Error', 'incorrect user or password')


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)


def run(args, pm):

    app = QtWidgets.QApplication(args)
    login = Login(pm)

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = Window()
        window.show()
        sys.exit(app.exec_())
