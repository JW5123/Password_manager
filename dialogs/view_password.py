from PyQt6.QtWidgets import (QDialog, QFormLayout, QPushButton,
                            QLabel, QLineEdit, QHBoxLayout, QApplication, QPlainTextEdit)

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor

from .password_operations import edit_password_entry, delete_password_entry

# 查看密碼項目對話框
class ViewPasswordDialog(QDialog):
    password_updated = pyqtSignal()
    
    def __init__(self, parent, name, account, password, notes, category=None):
        super().__init__(parent)
        self.setWindowTitle(f"{name}")
        self.parent_widget = parent
        self.setMinimumSize(300, 200)
        self.data_changed = False
        self.name = name
        self.account = account
        self.password = password
        self.notes = notes
        self.category = category
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # 名稱輸入框 (唯讀)
        self.name_input = QLineEdit(self.name)
        self.name_input.setReadOnly(True)
        layout.addRow("名稱:", self.name_input)

        # 帳號輸入框 (唯讀並可複製)
        self.account_input = QLineEdit(self.account)
        self.account_input.setReadOnly(True)
        self.account_input.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.account_input.mousePressEvent = lambda e: self.copy_to_clipboard(self.account_input)
        layout.addRow("帳號:", self.account_input)

        # 密碼輸入框 (唯讀並可複製)
        self.password_input = QLineEdit(self.password)
        self.password_input.setReadOnly(True)
        self.password_input.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.password_input.mousePressEvent = lambda e: self.copy_to_clipboard(self.password_input)
        layout.addRow("密碼:", self.password_input)

        # 分類輸入框 (唯讀)
        self.category_input = QLineEdit(self.category)
        self.category_input.setReadOnly(True)
        layout.addRow("分類:", self.category_input)

        # 備註文本框 (唯讀)
        self.notes_input = QPlainTextEdit(self)
        self.notes_input.setPlainText(self.notes)
        self.notes_input.setReadOnly(True)
        layout.addRow("備註:", self.notes_input)

        # 複製提示標籤
        self.copy_label = QLabel("")
        self.copy_label.setVisible(False)
        layout.addRow(self.copy_label)

        self.delete_button = QPushButton("刪除")
        self.delete_button.clicked.connect(self.delete_password)

        self.edit_button = QPushButton("編輯")
        self.edit_button.clicked.connect(self.edit_password)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.edit_button)
        
        layout.addRow(button_layout)

        self.setLayout(layout)

    # 複製內容到剪貼簿
    def copy_to_clipboard(self, widget):
        text = widget.text()
        QApplication.clipboard().setText(text)
        
        self.copy_label.setText(f"已複製「{text}」到剪貼簿")
        self.copy_label.setVisible(True)

        QTimer.singleShot(3000, lambda: self.copy_label.setVisible(False))

    def edit_password(self):
        new_name = edit_password_entry(self.parent_widget, self.parent_widget.db_manager, self.name)
        if new_name:
            # 更新本地變數
            self.name = new_name
            self.name_input.setText(new_name)

            # 重新讀取資料
            entry = self.parent_widget.db_manager.get_password_entry(self.name)
            account, password, notes, category = entry
            self.account_input.setText(account)
            self.password_input.setText(password)
            self.notes_input.setPlainText(notes)

            # 更新分類欄位
            self.category = category
            category_display = self.category
            self.category_input.setText(category_display)

            self.account = account
            self.password = password
            self.notes = notes
            self.data_changed = True

            # 當密碼資料有更新時
            self.password_updated.emit()

    def delete_password(self):
        if delete_password_entry(self, self.parent_widget.db_manager, self.name):
            self.data_changed = True
            self.close()

    # 關閉視窗時觸發
    def closeEvent(self, event):
        if self.data_changed:
            self.password_updated.emit()
        super().closeEvent(event)