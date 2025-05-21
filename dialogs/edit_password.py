from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit,
                            QPushButton, QLabel, QHBoxLayout, QTextEdit, QMessageBox,
                            QComboBox, QFrame)

# 編輯密碼項目
class EditPasswordDialog(QDialog):
    def __init__(self, parent, name, account, password, notes, category=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setWindowTitle(f"編輯 {name}")
        
        self.new_name = name
        self.new_account = account
        self.new_password = password
        self.new_notes = notes
        self.new_category = category

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit(self.new_name)
        layout.addRow("名稱:", self.name_input)

        self.account_input = QLineEdit(self.new_account)
        layout.addRow("帳號:", self.account_input)

        self.password_input = QLineEdit(self.new_password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        layout.addRow("密碼:", self.password_input)

        
        self.category_combo = QComboBox()
        self.category_combo.addItem("")  # 預設空（無分類）
        for category in self.parent_widget.settings_manager.get_categories():
            self.category_combo.addItem(category)

        # 預設選擇目前分類
        if self.new_category:
            index = self.category_combo.findText(self.new_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        layout.addRow("分類:", self.category_combo)

        self.notes_input = QTextEdit(self.new_notes)
        self.notes_input.setFrameShape(QFrame.Shape.StyledPanel)
        self.notes_input.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addRow("備註:", self.notes_input)

        button_layout = QHBoxLayout()

        self.submit_button = QPushButton("更改")
        self.submit_button.clicked.connect(self.on_submit)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.on_cancel)
        button_layout.addWidget(self.cancel_button)

        layout.addRow(button_layout)

        self.setLayout(layout)

    # 提交編輯結果
    def on_submit(self):
        self.new_name = self.name_input.text().strip()
        self.new_account = self.account_input.text().strip()
        self.new_password = self.password_input.text().strip()
        self.new_notes = self.notes_input.toPlainText().strip()
        self.new_category = self.category_combo.currentText().strip() or None

        missing_fields = []
        if not self.new_name:
            missing_fields.append("名稱")
        if not self.new_account:
            missing_fields.append("帳號")
        if not self.new_password:
            missing_fields.append("密碼")

        if missing_fields:
            QMessageBox.warning(self, "訊息", f"{'、'.join(missing_fields)}不能為空")
            return

        self.accept()

    def on_cancel(self):
        """取消編輯"""
        self.reject()
        # self.parent().close()