from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, 
                            QLabel, QDialogButtonBox, QFormLayout, QMessageBox)

class SetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定登入密碼")
        self.new_password = None
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("輸入密碼:", self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("確認密碼:", self.confirm_password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.check_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # 檢查輸入的密碼是否一致
    def check_password(self):
        if self.password_input.text() == self.confirm_password_input.text():
            self.new_password = self.password_input.text()
            self.accept()
        else:
            QMessageBox.warning(self, "訊息", "密碼不一致")