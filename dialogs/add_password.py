from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                            QDialogButtonBox, QMessageBox, QTextEdit, QComboBox, QPlainTextEdit,
                            QFrame)

# 新增密碼項目對話框
class AddNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setWindowTitle("新增資料")
        self.name = ""
        self.account = ""
        self.password = ""
        self.notes = ""
        self.category = None
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("名稱:", self.name_input)

        self.account_input = QLineEdit()
        layout.addRow("帳號:", self.account_input)

        self.password_input = QLineEdit()
        layout.addRow("密碼:", self.password_input)

        self.category_combo = QComboBox()
        self.category_combo.addItem("")
        for category in self.parent_widget.settings_manager.get_categories():
            self.category_combo.addItem(category)
        layout.addRow("分類:", self.category_combo)

        # 在 init_ui 方法中
        self.notes_input = QPlainTextEdit()
        # 在 PyQt6 中使用 QFrame 的常數來設定邊框樣式
        self.notes_input.setFrameShape(QFrame.Shape.StyledPanel)
        self.notes_input.setFrameShadow(QFrame.Shadow.Sunken)
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
        self.category = self.category_combo.currentText().strip() or None

        missing_fields = []
        if not self.name:
            missing_fields.append("名稱")
        if not self.account:
            missing_fields.append("帳號")
        if not self.password:
            missing_fields.append("密碼")

        if missing_fields:
            QMessageBox.warning(self, "訊息", f"{'、'.join(missing_fields)}不能為空")
            return

        self.accept()