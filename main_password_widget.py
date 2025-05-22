from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt

from dialogs.set_password import SetPasswordDialog
from dialogs.reset_password import ResetPasswordDialog
from password_encryption import hash_password, verify_password
from name_list_widget import NameListWidget
from utils.svg_icon_set import PasswordVisibilityController
import os

# 主密碼設定頁面
class MainPasswordWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = parent.db_manager
        self.init_ui()

    def init_ui(self):
        # 創建主垂直佈局
        main_layout = QVBoxLayout(self)
        
        # 創建一個垂直佈局用於包含所有內容並使其居中
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 檢查是否已經設置了主密碼
        if self.db_manager.has_master_password():
            # 創建密碼輸入框並設置提示文字
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("請輸入登入密碼")
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.pwd_input_visibility_controller = PasswordVisibilityController(self.password_input, self)
            self.password_input.returnPressed.connect(self.verify_master_password)
            self.password_input.setFixedWidth(300)
            
            # 將輸入框添加到中央佈局並居中對齊
            center_layout.addWidget(self.password_input, 0, Qt.AlignmentFlag.AlignCenter)
            center_layout.addSpacing(20)
            
            # 創建按鈕佈局
            button_layout = QHBoxLayout()
            
            # 創建按鈕
            self.submit_button = QPushButton("登入")
            self.submit_button.clicked.connect(self.verify_master_password)
            self.submit_button.setFixedWidth(100)
            
            self.reset_password_button = QPushButton("重設密碼")
            self.reset_password_button.clicked.connect(self.reset_master_password)
            self.reset_password_button.setFixedWidth(100)
            
            # 將按鈕添加到按鈕佈局
            button_layout.addWidget(self.submit_button)
            button_layout.addWidget(self.reset_password_button)
            
            # 將按鈕佈局添加到中央佈局
            center_layout.addLayout(button_layout)
            center_layout.setAlignment(button_layout, Qt.AlignmentFlag.AlignCenter)
            
        else:
            self.password_label = QLabel("尚未設定登入密碼")
            self.password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.set_password_button = QPushButton("設定登入密碼")
            self.set_password_button.clicked.connect(self.set_master_password)
            self.set_password_button.setFixedWidth(150)
            
            # 將標籤和按鈕添加到中央佈局
            center_layout.addWidget(self.password_label)
            center_layout.addSpacing(10)
            center_layout.addWidget(self.set_password_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 將中央佈局添加到主佈局，並設置垂直居中
        main_layout.addStretch(1)  # 上方添加彈性空間
        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)  # 下方添加彈性空間
        
        # 設置頁面主佈局並添加左右間距
        self.setLayout(main_layout)
        main_layout.setContentsMargins(30, 30, 30, 30)

    # 設定主密碼
    def set_master_password(self):
        dialog = SetPasswordDialog(self)
        if dialog.exec():
            new_password = dialog.new_password
            salt = os.urandom(16)
            hashed_password = hash_password(new_password)
            self.db_manager.set_master_password(hashed_password, salt)
            self.db_manager.set_current_master_password(new_password)
            QMessageBox.information(self, "訊息", "登入密碼已設定")
            self.reload_password_input_page()

    # 驗證主密碼
    def verify_master_password(self):
        entered_password = self.password_input.text()

        if not entered_password:
            QMessageBox.warning(self, "訊息", "請輸入密碼")
            return

        stored_password, _ = self.db_manager.get_master_password()

        if verify_password(entered_password, stored_password):
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

            stored_password, _ = self.db_manager.get_master_password()

            if not current_password:
                QMessageBox.warning(self, "訊息", "請輸入密碼")
                return

            if verify_password(current_password, stored_password):
                # 使用舊密碼解密所有密碼，然後用新密碼重新加密
                self.db_manager.set_current_master_password(current_password)
                all_entries = self.db_manager.get_all_entries()  # 獲取所有解密的條目
                
                # 更新主密碼
                hashed_new_password = hash_password(new_password)
                new_salt = os.urandom(16)
                self.db_manager.update_master_password(hashed_new_password, new_salt)
                
                # 設置新的主密碼用於加密
                self.db_manager.set_current_master_password(new_password)
                
                # 重新加密所有欄位
                for name, account, password, notes in all_entries:
                    self.db_manager.update_password_entry(name, name, account, password, notes)
                
                QMessageBox.information(self, "訊息", "登入密碼已重設")
            else:
                QMessageBox.warning(self, "訊息", "當前密碼錯誤")
                
    # 重新載入密碼輸入頁面
    def reload_password_input_page(self):
        self.parent.setCentralWidget(MainPasswordWidget(self.parent))