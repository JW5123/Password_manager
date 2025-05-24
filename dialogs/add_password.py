from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                            QMessageBox, QComboBox, QPlainTextEdit,
                            QFrame, QHBoxLayout, QPushButton)

from utils.password_generator import PasswordGeneratorDialog

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

        # 生成密碼按鈕
        self.generate_password_btn = QPushButton("生成密碼")
        self.generate_password_btn.clicked.connect(self.open_password_generator)
        layout.addRow("", self.generate_password_btn)

        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        for category in self.parent_widget.settings_manager.get_categories():
            self.category_combo.addItem(category)
        layout.addRow("分類:", self.category_combo)

        self.notes_input = QPlainTextEdit()
        self.notes_input.setFrameShape(QFrame.Shape.StyledPanel)
        self.notes_input.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addRow("備註:", self.notes_input)

        button_layout = QHBoxLayout()
        self.submit_button = QPushButton("新增")
        self.submit_button.clicked.connect(self.save_data)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addRow(button_layout)

        self.setLayout(layout)
    
    def open_password_generator(self):
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec():
            generated_password = dialog.get_password()
            self.password_input.setText(generated_password)

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