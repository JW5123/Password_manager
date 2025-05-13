from PyQt6.QtWidgets import (QDialog, QFormLayout, QPushButton,
                             QLabel, QHBoxLayout, QTextEdit, QMessageBox)

from dialogs.edit_password import EditPasswordDialog

class ViewPasswordDialog(QDialog):
    """查看密碼項目對話框"""
    def __init__(self, parent, name, account, password, notes):
        super().__init__(parent)
        self.setWindowTitle(f"查看 {name} 的帳號和密碼")
        self.parent_widget = parent
        self.setMinimumSize(300, 200)
        self.data_changed = False
        self.init_ui(name, account, password, notes)
        self.name = name
        self.account = account
        self.password = password
        self.notes = notes

    def init_ui(self, name, account, password, notes):
        layout = QFormLayout()

        self.name_label = QLabel(f"名稱: {name}")
        layout.addRow(self.name_label)

        self.account_label = QLabel(f"帳號: {account}")
        layout.addRow(self.account_label)

        self.password_label = QLabel(f"密碼: {password}")
        layout.addRow(self.password_label)

        self.notes_label = QLabel("備註:")
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(notes)
        self.notes_input.setReadOnly(True)
        layout.addRow(self.notes_label, self.notes_input)

        self.delete_button = QPushButton("刪除")
        self.delete_button.clicked.connect(self.delete_password)

        self.edit_button = QPushButton("編輯")
        self.edit_button.clicked.connect(self.edit_password)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.edit_button)
        
        layout.addRow(button_layout)

        self.setLayout(layout)

    def edit_password(self):
        """編輯密碼"""
        dialog = EditPasswordDialog(self, self.name, self.account, self.password, self.notes)
        if dialog.exec():
            new_name, new_account, new_password, new_notes = dialog.new_name, dialog.new_account, dialog.new_password, dialog.new_notes
            
            # 更新資料庫
            self.parent_widget.db_manager.update_password_entry(self.name, new_name, new_account, new_password, new_notes)

            # 更新介面
            self.name_label.setText(f"名稱: {new_name}")
            self.account_label.setText(f"帳號: {new_account}")
            self.password_label.setText(f"密碼: {new_password}")
            self.notes_input.setPlainText(new_notes)

            # 更新物件變數
            self.name = new_name
            self.account = new_account
            self.password = new_password
            self.notes = new_notes
            
            self.data_changed = True

        self.close()

    def delete_password(self):
        """刪除密碼"""
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要刪除此資料嗎？')

        delete_button = reply.addButton("刪除", QMessageBox.ButtonRole.ActionRole)
        cancel_button = reply.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        
        reply.exec()

        if reply.clickedButton() == delete_button:
            self.parent_widget.db_manager.delete_password_entry(self.name)
            self.data_changed = True
            self.close()

    def closeEvent(self, event):
        """關閉視窗時觸發"""
        if self.data_changed:
            self.parent_widget.load_names()
        super().closeEvent(event)