from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                            QDialogButtonBox, QMessageBox, QTextEdit)

# 新增密碼項目對話框
class AddNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增資料")
        self.name = ""
        self.account = ""
        self.password = ""
        self.notes = ""
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("名稱:", self.name_input)

        self.account_input = QLineEdit()
        layout.addRow("帳號:", self.account_input)

        self.password_input = QLineEdit()
        layout.addRow("密碼:", self.password_input)

        self.notes_input = QTextEdit()
        layout.addRow("備註:", self.notes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("新增")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")

        buttons.accepted.connect(self.save_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # 保存輸入的數據
    def save_data(self):
        self.name = self.name_input.text().strip()
        self.account = self.account_input.text().strip()
        self.password = self.password_input.text().strip()
        self.notes = self.notes_input.toPlainText().strip()

        if not self.name:
            QMessageBox.warning(self, "訊息", "資料不能為空")
            return

        self.accept()