from PyQt5 import QtWidgets
from src import password_manager, models
import main


class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.text_name = QtWidgets.QLineEdit(self)
        self.text_pass = QtWidgets.QLineEdit(self)
        self.button_login = QtWidgets.QPushButton('login', self)
        self.button_login.clicked.connect(self.handle_login)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.text_name)
        layout.addWidget(self.text_pass)
        layout.addWidget(self.button_login)

    def handle_login(self):
        
        path_file = './docs/paths.txt'
        paths = main.get_paths(path_file)
        pm = password_manager.PasswordManager(paths)
        user = pm.session.query(models.User).filter(models.User.username == self.text_name).one()
        if user:
            if user.master_password == pm.crypto.encrypt(self.text_pass):
                self.accept()
        if not self.Accepted:
            QtWidgets.QMessageBox.warning(self, 'Error', 'incorrect user or password')


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)


if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    login = Login()

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = Window()
        window.show()
        sys.exit(app.exec_())
