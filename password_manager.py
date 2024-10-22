import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QListWidget, QInputDialog, QMessageBox, QHBoxLayout, QDialog, 
                             QFormLayout, QDialogButtonBox, QAbstractItemView, QListWidgetItem, QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sqlite3
import csv
import os
import shutil
from hashlib import sha256

class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('password-manager.png'))

        self.setWindowTitle("密碼管理系統")
        self.setGeometry(100, 100, 400, 300)  

        base_path = os.path.expanduser("~")
        db_path = os.path.join(base_path, 'passwords.db')

        if not os.path.exists(db_path):
            original_db_path = os.path.join(os.path.dirname(__file__), 'original_passwords.db')
            if os.path.exists(original_db_path):
                shutil.copy(original_db_path, db_path)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_db()

        
        self.main_password_widget = MainPasswordWidget(self)
        self.setCentralWidget(self.main_password_widget)

        self.center_window()

    def setup_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                            id INTEGER PRIMARY KEY, 
                            name TEXT NOT NULL, 
                            account TEXT, 
                            password TEXT, 
                            notes TEXT,
                            order_index INTEGER)''')
        
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS master_password (
                            id INTEGER PRIMARY KEY, 
                            password TEXT NOT NULL)''')
        
        
        self.cursor.execute("PRAGMA table_info(passwords)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'order_index' not in columns:
            self.cursor.execute("ALTER TABLE passwords ADD COLUMN order_index INTEGER")
            
            
            self.cursor.execute("SELECT rowid, name FROM passwords ORDER BY name ASC")
            rows = self.cursor.fetchall()
            for order_index, (rowid, name) in enumerate(rows):
                self.cursor.execute("UPDATE passwords SET order_index = ? WHERE rowid = ?", (order_index, rowid))
            
        self.conn.commit()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        
        size = self.geometry()
        
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        
        self.move(x, y)

    def closeEvent(self, event):
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要退出嗎？')

        reply.setIcon(QMessageBox.Question)

        
        confirm_button = reply.addButton("確定", QMessageBox.ActionRole)
        cancel_button = reply.addButton("取消", QMessageBox.RejectRole)

        reply.exec_()

        if reply.clickedButton() == confirm_button:
            event.accept()
            self.conn.close()
        else:
            event.ignore()


class MainPasswordWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.parent.cursor.execute("SELECT * FROM master_password")
        master_password = self.parent.cursor.fetchone()

        if master_password:
            self.password_label = QLabel("請輸入登入密碼")
            
            input_layout = QHBoxLayout()
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)

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
            self.password_label.setAlignment(Qt.AlignCenter)  

            layout.addWidget(self.password_label)  

            
            self.set_password_button = QPushButton("設定登入密碼")
            self.set_password_button.clicked.connect(self.set_master_password)

            
            layout.addWidget(self.set_password_button)
            layout.setAlignment(self.set_password_button, Qt.AlignCenter)  

        self.setLayout(layout)

    
    def set_master_password(self):
        dialog = SetPasswordDialog(self)
        if dialog.exec_():
            new_password = dialog.new_password
            hashed_password = sha256(new_password.encode()).hexdigest()
            self.parent.cursor.execute("INSERT INTO master_password (password) VALUES (?)", (hashed_password,))
            self.parent.conn.commit()
            QMessageBox.information(self, "訊息", "登入密碼已設定")
            self.reload_password_input_page()  

    
    def verify_master_password(self):
        entered_password = self.password_input.text()

        if not entered_password:
            QMessageBox.warning(self, "訊息", "請輸入密碼")
            return  

        hashed_entered_password = sha256(entered_password.encode()).hexdigest()

        self.parent.cursor.execute("SELECT password FROM master_password")
        stored_password = self.parent.cursor.fetchone()[0]

        if hashed_entered_password == stored_password:
            QMessageBox.information(self, "訊息", "登入成功")
            self.parent.setCentralWidget(NameListWidget(self.parent))  
        else:
            QMessageBox.warning(self, "訊息", "密碼錯誤")

    
    def reset_master_password(self):
        dialog = ResetPasswordDialog(self)
        if dialog.exec_():
            current_password = dialog.current_password
            new_password = dialog.new_password

            
            hashed_current_password = sha256(current_password.encode()).hexdigest()
            self.parent.cursor.execute("SELECT password FROM master_password")
            stored_password = self.parent.cursor.fetchone()[0]

            if hashed_current_password == stored_password:
                hashed_new_password = sha256(new_password.encode()).hexdigest()
                self.parent.cursor.execute("UPDATE master_password SET password = ? WHERE id = 1", (hashed_new_password,))
                self.parent.conn.commit()
                QMessageBox.information(self, "訊息", "登入密碼已重設")
            else:
                QMessageBox.warning(self, "訊息", "當前密碼錯誤")
                
    
    def reload_password_input_page(self):
        self.parent.setCentralWidget(MainPasswordWidget(self.parent))

class ResetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("重設登入密碼")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        
        self.current_password_label = QLabel("當前密碼")
        layout.addWidget(self.current_password_label)

        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.current_password_input)

        
        self.new_password_label = QLabel("新密碼")
        layout.addWidget(self.new_password_label)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_input)

        
        self.confirm_password_label = QLabel("確認新密碼")
        layout.addWidget(self.confirm_password_label)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_input)

        button_layout = QHBoxLayout()

        
        self.submit_button = QPushButton("更改")
        self.submit_button.clicked.connect(self.check_passwords)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)  
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout) 

        self.setLayout(layout)

    def check_passwords(self):
        if self.new_password_input.text() == self.confirm_password_input.text():
            self.current_password = self.current_password_input.text()
            self.new_password = self.new_password_input.text()
            self.accept()
        else:
            QMessageBox.warning(self, "訊息", "新密碼不一致")


class SetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定登入密碼")
        self.new_password = None
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("輸入密碼:", self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("確認密碼:", self.confirm_password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.check_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    
    def check_password(self):
        if self.password_input.text() == self.confirm_password_input.text():
            self.new_password = self.password_input.text()
            self.accept()
        else:
            QMessageBox.warning(self, "訊息", "密碼不一致")


class NameListWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜尋")
        self.search_box.textChanged.connect(self.filter_names)
        search_layout.addWidget(self.search_box)

        self.logout_button = QPushButton("登出")
        self.logout_button.clicked.connect(self.logout)
        search_layout.addWidget(self.logout_button)

        layout.addLayout(search_layout)

        
        self.name_list = QListWidget()
        self.name_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.name_list.setDragDropMode(QAbstractItemView.InternalMove)  
        self.name_list.itemDoubleClicked.connect(self.view_account_password)

        self.name_list.model().rowsMoved.connect(self.update_order_in_database)  
        layout.addWidget(self.name_list)

        button_layout = QHBoxLayout()

        
        self.export_button = QPushButton("匯出")
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.export_button)

        
        self.add_button = QPushButton("新增資料")
        self.add_button.clicked.connect(self.add_name)
        button_layout.addWidget(self.add_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.load_names()

    def export_to_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存 CSV 檔案", "密碼儲存簿.csv", "CSV Files (*.csv);;All Files (*)", options=options)

        if file_path:
            if not file_path.endswith('.csv'):
                file_path += '.csv'

            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(['名稱', '帳號', '密碼', '備註'])

                self.parent.cursor.execute("SELECT name, account, password, notes FROM passwords")
                for row in self.parent.cursor.fetchall():
                    writer.writerow(row)

            QMessageBox.information(self, "訊息", "資料成功匯出至 CSV 檔案")

    def logout(self):
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要登出嗎？')

        reply.setIcon(QMessageBox.Question)
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply.button(QMessageBox.Yes).setText("登出")
        reply.button(QMessageBox.No).setText("取消")

        reply.exec_()

        if reply.clickedButton() == reply.button(QMessageBox.Yes):
            self.parent.setCentralWidget(MainPasswordWidget(self.parent))

    def load_names(self):
        self.name_list.clear()
        self.parent.cursor.execute("SELECT name FROM passwords ORDER BY order_index ASC")
        names = self.parent.cursor.fetchall()
        for name in names:
            item = QListWidgetItem(name[0])
            self.name_list.addItem(item)

    def filter_names(self):
        search_text = self.search_box.text().lower()
        for index in range(self.name_list.count()):
            item = self.name_list.item(index)
            item.setHidden(search_text not in item.text().lower())

    def add_name(self):
        dialog = AddNameDialog(self)
        if dialog.exec_():
            name, account, password, notes = dialog.name, dialog.account, dialog.password, dialog.notes
            self.parent.cursor.execute("SELECT MAX(order_index) FROM passwords")
            max_order = self.parent.cursor.fetchone()[0]
            new_order_index = (max_order + 1) if max_order is not None else 0
            self.parent.cursor.execute("INSERT INTO passwords (name, account, password, notes, order_index) VALUES (?, ?, ?, ?, ?)", 
                                       (name, account, password, notes, new_order_index))
            self.parent.conn.commit()
            self.load_names()

    def view_account_password(self, item):
        name = item.text()
        self.parent.cursor.execute("SELECT account, password, notes FROM passwords WHERE name = ?", (name,))
        account, password, notes = self.parent.cursor.fetchone()

        dialog = ViewPasswordDialog(self, name, account, password, notes)
        dialog.exec_()

    def update_order_in_database(self):
        for i in range(self.name_list.count()):
            name = self.name_list.item(i).text()
            self.parent.cursor.execute("UPDATE passwords SET order_index = ? WHERE name = ?", (i, name))
        self.parent.conn.commit()


class ViewPasswordDialog(QDialog):
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
        dialog = EditPasswordDialog(self, self.name, self.account, self.password, self.notes)
        if dialog.exec_():
            new_name, new_account, new_password, new_notes = dialog.new_name, dialog.new_account, dialog.new_password, dialog.new_notes
            self.parent_widget.parent.cursor.execute("UPDATE passwords SET name = ?, account = ?, password = ?, notes = ? WHERE name = ?",
                                                     (new_name, new_account, new_password, new_notes, self.name))
            self.parent_widget.parent.conn.commit()

            self.name_label.setText(f"名稱: {new_name}")
            self.account_label.setText(f"帳號: {new_account}")
            self.password_label.setText(f"密碼: {new_password}")
            self.notes_input.setPlainText(new_notes)

            self.name = new_name
            self.account = new_account
            self.password = new_password
            self.notes = new_notes
            
            self.data_changed = True  

        self.close()

    def delete_password(self):
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要刪除此資料嗎？')

        delete_button = reply.addButton("刪除", QMessageBox.ActionRole)
        cancel_button = reply.addButton("取消", QMessageBox.RejectRole)
        
        reply.exec_()

        if reply.clickedButton() == delete_button:
            self.parent_widget.parent.cursor.execute("DELETE FROM passwords WHERE name = ?", (self.name,))
            self.parent_widget.parent.conn.commit()
            self.data_changed = True  
            self.close()

    def closeEvent(self, event):
        if self.data_changed:
            self.parent_widget.load_names()  
        super().closeEvent(event)


class EditPasswordDialog(QDialog):
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

        
        self.name_input = QLineEdit(self.new_name)
        layout.addRow("名稱:", self.name_input)  

        
        self.account_input = QLineEdit(self.new_account)
        layout.addRow("帳號:", self.account_input)

        
        self.password_input = QLineEdit(self.new_password)
        self.password_input.setEchoMode(QLineEdit.Normal)
        layout.addRow("密碼:", self.password_input)

        
        self.notes_input = QTextEdit(self.new_notes)  
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

    def on_submit(self):
        self.new_name = self.name_input.text().strip()
        self.new_account = self.account_input.text().strip()
        self.new_password = self.password_input.text().strip()
        self.new_notes = self.notes_input.toPlainText().strip()  

        if not self.new_name:
                QMessageBox.warning(self, "訊息", "名稱不能為空")
                return  

        self.accept()

    def on_cancel(self):
        self.reject()
        self.parent().close()  



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

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("新增")  
        buttons.button(QDialogButtonBox.Cancel).setText("取消")  

        buttons.accepted.connect(self.save_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save_data(self):
        self.name = self.name_input.text().strip()
        self.account = self.account_input.text().strip()
        self.password = self.password_input.text().strip()
        self.notes = self.notes_input.toPlainText().strip()  

        if not self.name:
            QMessageBox.warning(self, "訊息", "名稱不能為空")
            return  

        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManager()
    window.show()
    sys.exit(app.exec_())
