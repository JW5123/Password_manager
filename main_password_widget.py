from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction

from dialogs.set_password import SetPasswordDialog
from dialogs.reset_password import ResetPasswordDialog
from password_encryption import hash_password, verify_password
from name_list_widget import NameListWidget

class MainPasswordWidget(QWidget):
    # 主密碼設定頁面
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = parent.db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 檢查是否已經設置了主密碼
        if self.db_manager.has_master_password():
            self.password_label = QLabel("請輸入登入密碼")
            
            input_layout = QHBoxLayout()
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.returnPressed.connect(self.verify_master_password)

            input_layout.addWidget(self.password_label)
            input_layout.addWidget(self.password_input)

            layout.addLayout(input_layout)

            button_layout = QHBoxLayout()

            self.submit_button = QPushButton("登入")
            self.submit_button.clicked.connect(self.verify_master_password)
            button_layout.addWidget(self.submit_button)

            self.reset_password_button = QPushButton("重設密碼")
            self.reset_password_button.clicked.connect(self.reset_master_password)
            button_layout.addWidget(self.reset_password_button)

            layout.addLayout(button_layout)
        else:
            self.password_label = QLabel("尚未設定登入密碼")
            self.password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout.addWidget(self.password_label)

            self.set_password_button = QPushButton("設定登入密碼")
            self.set_password_button.clicked.connect(self.set_master_password)

            # 將按鈕添加到佈局中，並置中
            layout.addWidget(self.set_password_button)
            layout.setAlignment(self.set_password_button, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    # 設定主密碼
    def set_master_password(self):
        dialog = SetPasswordDialog(self)
        if dialog.exec():
            new_password = dialog.new_password
            hashed_password = hash_password(new_password)
            self.db_manager.set_master_password(hashed_password)
            # 儲存明文主密碼用於加密/解密
            self.db_manager.set_current_master_password(new_password)
            QMessageBox.information(self, "訊息", "登入密碼已設定")
            self.reload_password_input_page()

    # 驗證主密碼
    def verify_master_password(self):
        entered_password = self.password_input.text()

        if not entered_password:
            QMessageBox.warning(self, "訊息", "請輸入密碼")
            return

        stored_password = self.db_manager.get_master_password()

        if verify_password(entered_password, stored_password):
            # 儲存明文主密碼用於加密/解密
            self.db_manager.set_current_master_password(entered_password)
            QMessageBox.information(self, "訊息", "登入成功")
            self.parent.setCentralWidget(NameListWidget(self.parent))
        else:
            QMessageBox.warning(self, "訊息", "密碼錯誤")

    # 重設主密碼
    def reset_master_password(self):
        dialog = ResetPasswordDialog(self)
        if dialog.exec():
            current_password = dialog.current_password
            new_password = dialog.new_password

            stored_password = self.db_manager.get_master_password()

            if verify_password(current_password, stored_password):
                # 使用舊密碼解密所有密碼，然後用新密碼重新加密
                self.db_manager.set_current_master_password(current_password)
                all_entries = self.db_manager.get_all_entries()  # 獲取所有解密的條目
                
                # 更新主密碼
                hashed_new_password = hash_password(new_password)
                self.db_manager.update_master_password(hashed_new_password)
                
                # 設置新的主密碼用於加密
                self.db_manager.set_current_master_password(new_password)
                
                # 重新加密所有欄位
                for name, account, password, notes in all_entries:
                    self.db_manager.update_password_entry(name, name, account, password, notes)
                
                QMessageBox.information(self, "訊息", "登入密碼已重設，所有敏感資料已重新加密")
            else:
                QMessageBox.warning(self, "訊息", "當前密碼錯誤")
                
    def reload_password_input_page(self):
        """重新載入密碼輸入頁面"""
        self.parent.setCentralWidget(MainPasswordWidget(self.parent))