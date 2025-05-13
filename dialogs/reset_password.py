from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QHBoxLayout, QMessageBox)

class ResetPasswordDialog(QDialog):
    """重設登入密碼對話框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("重設登入密碼")
        self.current_password = None
        self.new_password = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 當前密碼
        self.current_password_label = QLabel("當前密碼")
        layout.addWidget(self.current_password_label)

        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.current_password_input)

        # 新密碼
        self.new_password_label = QLabel("新密碼")
        layout.addWidget(self.new_password_label)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_password_input)

        # 確認新密碼
        self.confirm_password_label = QLabel("確認新密碼")
        layout.addWidget(self.confirm_password_label)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        button_layout = QHBoxLayout()

        # 更改按鈕
        self.submit_button = QPushButton("更改")
        self.submit_button.clicked.connect(self.check_passwords)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def check_passwords(self):
        """檢查新密碼是否一致，並儲存密碼值"""
        if self.new_password_input.text() == self.confirm_password_input.text():
            self.current_password = self.current_password_input.text()
            self.new_password = self.new_password_input.text()
            self.accept()
        else:
            QMessageBox.warning(self, "訊息", "新密碼不一致")