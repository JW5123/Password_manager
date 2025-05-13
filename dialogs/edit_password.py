from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                             QPushButton, QLabel, QHBoxLayout, QTextEdit, QMessageBox)

class EditPasswordDialog(QDialog):
    """編輯密碼項目對話框"""
    def __init__(self, parent, name, account, password, notes):
        super().__init__(parent)
        self.setWindowTitle("編輯帳號密碼")
        
        self.new_name = name
        self.new_account = account
        self.new_password = password
        self.new_notes = notes

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # 名稱輸入框
        self.name_input = QLineEdit(self.new_name)
        layout.addRow("名稱:", self.name_input)

        # 帳號輸入框
        self.account_input = QLineEdit(self.new_account)
        layout.addRow("帳號:", self.account_input)

        # 密碼輸入框
        self.password_input = QLineEdit(self.new_password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        layout.addRow("密碼:", self.password_input)

        # 備註多行輸入框
        self.notes_input = QTextEdit(self.new_notes)
        layout.addRow("備註:", self.notes_input)

        # 按鈕佈局
        button_layout = QHBoxLayout()

        # 提交按鈕
        self.submit_button = QPushButton("更改")
        self.submit_button.clicked.connect(self.on_submit)
        button_layout.addWidget(self.submit_button)

        # 取消按鈕
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.on_cancel)
        button_layout.addWidget(self.cancel_button)

        layout.addRow(button_layout)

        self.setLayout(layout)

    def on_submit(self):
        """提交編輯結果"""
        self.new_name = self.name_input.text().strip()
        self.new_account = self.account_input.text().strip()
        self.new_password = self.password_input.text().strip()
        self.new_notes = self.notes_input.toPlainText().strip()

        if not self.new_name:
                QMessageBox.warning(self, "訊息", "名稱不能為空")
                return

        self.accept()

    def on_cancel(self):
        """取消編輯"""
        self.reject()
        self.parent().close()