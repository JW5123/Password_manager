from PyQt6.QtWidgets import QMessageBox
from dialogs.set_password import SetPasswordDialog
from dialogs.reset_password import ResetPasswordDialog
from app.account_list_widget import NameListWidget
from utils.password_encryption import hash_password, verify_password
import os

class MainPasswordController:
    def __init__(self, widget, db_manager):
        self.widget = widget
        self.db_manager = db_manager

    def set_master_password(self):
        dialog = SetPasswordDialog(self.widget)
        if dialog.exec():
            new_password = dialog.new_password
            salt = os.urandom(16)
            hashed_password = hash_password(new_password)
            self.db_manager.set_master_password(hashed_password, salt)
            self.db_manager.set_current_master_password(new_password)
            QMessageBox.information(self.widget, "訊息", "登入密碼已設定")
            self.widget.reload_password_input_page()

    def verify_master_password(self):
        entered_password = self.widget.password_input.text()

        if not entered_password:
            QMessageBox.warning(self.widget, "訊息", "請輸入密碼")
            return

        stored_password, _ = self.db_manager.get_master_password()

        if verify_password(entered_password, stored_password):
            self.db_manager.set_current_master_password(entered_password)
            QMessageBox.information(self.widget, "訊息", "登入成功")
            self.widget.parent.setCentralWidget(NameListWidget(self.widget.parent))
            self.widget.parent.name_list_widget = self.widget.parent.centralWidget()
        else:
            QMessageBox.warning(self.widget, "訊息", "密碼錯誤")

    def reset_master_password(self):
        dialog = ResetPasswordDialog(self.widget)
        if dialog.exec():
            current_password = dialog.current_password
            new_password = dialog.new_password

            stored_password, _ = self.db_manager.get_master_password()

            if not current_password:
                QMessageBox.warning(self.widget, "訊息", "請輸入密碼")
                return

            if verify_password(current_password, stored_password):
                self.db_manager.set_current_master_password(current_password)
                all_entries = self.db_manager.get_all_entries()

                hashed_new_password = hash_password(new_password)
                new_salt = os.urandom(16)
                self.db_manager.update_master_password(hashed_new_password, new_salt)
                self.db_manager.set_current_master_password(new_password)

                for name, account, password, notes, category in all_entries:
                    self.db_manager.update_password_entry(name, name, account, password, notes, category)

                QMessageBox.information(self.widget, "訊息", "登入密碼已重設")
            else:
                QMessageBox.warning(self.widget, "訊息", "當前密碼錯誤")
