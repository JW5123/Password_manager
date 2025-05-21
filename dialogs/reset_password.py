from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QHBoxLayout, QMessageBox)

# 登入密碼重設對話框
class ResetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登入密碼重設")
        self.current_password = None
        self.new_password = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.current_password_label = QLabel("當前密碼")
        layout.addWidget(self.current_password_label)

        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.current_password_input)

        self.new_password_label = QLabel("新密碼")
        layout.addWidget(self.new_password_label)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_password_input)

        self.confirm_password_label = QLabel("確認密碼")
        layout.addWidget(self.confirm_password_label)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        button_layout = QHBoxLayout()

        self.submit_button = QPushButton("更改")
        self.submit_button.clicked.connect(self.check_passwords)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    # 檢查新密碼是否一致，並儲存密碼
    def check_passwords(self):
        if self.new_password_input.text() == self.confirm_password_input.text():
            self.current_password = self.current_password_input.text()
            self.new_password = self.new_password_input.text()
            self.accept()
        else:
            QMessageBox.warning(self, "訊息", "密碼不一致")