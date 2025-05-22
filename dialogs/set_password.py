import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QLineEdit, QPushButton, QHBoxLayout,
    QFormLayout, QMessageBox
)

from utils.svg_icon_set import PasswordVisibilityController

class SetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定登入密碼")
        self.new_password = None
        self.setFixedSize(350, 180)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # 密碼欄位
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.pwd_visibility_controller = PasswordVisibilityController(self.password_input, self)
        layout.addRow("輸入密碼:", self.password_input)

        # 確認密碼欄位
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pwd_visibility_controller = PasswordVisibilityController(self.confirm_password_input, self)
        layout.addRow("確認密碼:", self.confirm_password_input)

        # 底部按鈕
        buttons_layout = QHBoxLayout()
        self.submit_button = QPushButton("確定")
        self.submit_button.clicked.connect(self.check_password)
        buttons_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        layout.addRow(buttons_layout)
        self.setLayout(layout)

    def check_password(self):
        if self.password_input.text() == self.confirm_password_input.text():
            self.new_password = self.password_input.text()
            self.accept()
        else:
            QMessageBox.warning(self, "訊息", "密碼不一致")