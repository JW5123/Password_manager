from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                            QListWidget, QHBoxLayout, QAbstractItemView, QFileDialog, QMessageBox,
                            QListWidgetItem, QMenuBar, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction, QIcon

import pandas as pd
from dialogs.add_password import AddNameDialog
from dialogs.view_password import ViewPasswordDialog
from dialogs.password_operations import edit_password_entry, delete_password_entry
from utils.style_loader import load_qss

# 帳號列表介面
class NameListWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = parent.db_manager
        self.settings_manager = parent.settings_manager
        
        self.init_ui()
        self.setup_menu()

    def setup_menu(self):
        # 建立選單列
        menu_bar = QMenuBar()
        self.parent.setMenuBar(menu_bar)
        
        file_menu = menu_bar.addMenu("檔案")
        
        import_action = QAction("匯入", self)
        import_action.triggered.connect(self.import_from_file)
        file_menu.addAction(import_action)
        
        export_action = QAction("匯出", self)
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)
        
        settings_menu = menu_bar.addMenu("設定")
        settings_action = QAction("設定", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

    # 開啟設定頁面
    def open_settings(self):
        from settings_widget import SettingsWidget
        self.parent.setCentralWidget(SettingsWidget(self.parent))

    def init_ui(self):
        layout = QVBoxLayout()

        # 搜尋區域
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜尋")
        self.search_box.textChanged.connect(self.filter_names)
        
        self.clear_action = QAction(QIcon("icon/remove.svg"), "清除", self.search_box)
        self.clear_action.triggered.connect(self.clear_search_box)
        self.search_box.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)
        self.clear_action.setVisible(False)  # 預設不顯示
        
        self.search_box.setFont(QFont("Arial", 12))
        search_layout.addWidget(self.search_box)

        self.logout_button = QPushButton("登出")
        self.logout_button.clicked.connect(self.logout)
        search_layout.addWidget(self.logout_button)

        layout.addLayout(search_layout)

        # 名稱列表
        self.name_list = QListWidget()
        self.name_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.name_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.name_list.itemDoubleClicked.connect(self.view_account_password)

        # 右鍵選單
        self.name_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.name_list.customContextMenuRequested.connect(self.show_context_menu)

        # 行移動信號連接
        self.name_list.model().rowsMoved.connect(self.update_order_in_database)
        layout.addWidget(self.name_list)

        button_layout = QHBoxLayout()

        # 新增資料按鈕
        self.add_button = QPushButton("新增資料")
        self.add_button.clicked.connect(self.add_name)
        button_layout.addWidget(self.add_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.load_names()

    def show_context_menu(self, position):
        item = self.name_list.itemAt(position)
        if item is None:
            return

        context_menu = QMenu()

        menu_style = load_qss("CSS/styles.qss")
        context_menu.setStyleSheet(menu_style)

        view_action = QAction("查看", self)
        view_action.triggered.connect(lambda: self.view_account_password(item))
        context_menu.addAction(view_action)

        edit_action = QAction("編輯", self)
        edit_action.triggered.connect(lambda: self.handle_edit(item))
        context_menu.addAction(edit_action)

        delete_action = QAction("刪除", self)
        delete_action.triggered.connect(lambda: self.handle_delete(item))
        context_menu.addAction(delete_action)

        context_menu.exec(self.name_list.mapToGlobal(position))


    # 匯入檔案功能
    def import_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇檔案", "", 
            "Excel Files CSV Files (*.csv);;(*.xlsx *.xls);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            else:
                df = pd.read_excel(file_path)
                
            # 檢查必要欄位是否存在
            required_columns = ['名稱', '帳號', '密碼']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                QMessageBox.warning(self, "匯入錯誤", 
                                f"檔案缺少必要欄位：{', '.join(missing_columns)}\n"
                                f"請確保檔案包含以下欄位：{', '.join(required_columns)}")
                return
                
            # 確保備註欄位存在，若不存在則添加空值
            if '備註' not in df.columns:
                df['備註'] = ''
            
            # 計數成功和失敗的項目
            success_count = 0
            duplicate_count = 0
            fail_count = 0
            
            # 取得所有現有的項目（用於檢查重複）
            existing_entries = self.db_manager.get_all_entries()
            # 建立一個集合，包含(名稱, 帳號, 密碼)的元組，方便快速查找
            existing_set = {(entry[0], entry[1], entry[2]) for entry in existing_entries}
            
            # 處理每一行資料
            for _, row in df.iterrows():
                name = str(row['名稱']).strip()
                account = str(row['帳號']).strip()
                password = str(row['密碼']).strip()
                notes = str(row['備註']) if not pd.isna(row['備註']) else ''
                
                # 檢查名稱是否為空
                if not name:
                    fail_count += 1
                    continue
                    
                # 檢查是否有重複項目（名稱、帳號、密碼都相同）
                if (name, account, password) in existing_set:
                    duplicate_count += 1
                    continue
                    
                # 添加到資料庫
                try:
                    self.db_manager.add_password_entry(name, account, password, notes)
                    success_count += 1
                    existing_set.add((name, account, password))
                except Exception:
                    fail_count += 1
            
            # 重新載入名稱列表
            self.load_names()
            
            # 顯示結果
            message = f"匯入結果：\n成功添加：{success_count} 項\n"
            if duplicate_count > 0:
                message += f"已跳過（重複項目）：{duplicate_count} 項\n"
            if fail_count > 0:
                message += f"匯入失敗：{fail_count} 項\n"
            
            QMessageBox.information(self, "匯入完成", message)
            
        except Exception as e:
            QMessageBox.critical(self, "匯入錯誤", f"檔案匯入過程中發生錯誤：\n{str(e)}")

    # 匯出資料為CSV檔案
    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "儲存檔案", "密碼儲存簿.xlsx", 
            "Excel Files CSV Files (*.csv);;(*.xlsx);;All Files (*)"
        )

        if not file_path:
            return
            
        try:
            entries = self.db_manager.get_all_entries()

            df = pd.DataFrame(entries, columns=['名稱', '帳號', '密碼', '備註'])
            
            # 根據檔案擴展名決定匯出格式
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                df.to_excel(file_path, index=False)

            QMessageBox.information(self, "訊息", f"資料成功匯出至 {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "匯出錯誤", f"檔案匯出過程中發生錯誤：\n{str(e)}")

    # 登出帳戶
    def logout(self):
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要登出嗎？')

        reply.setIcon(QMessageBox.Icon.Question)
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply.button(QMessageBox.StandardButton.Yes).setText("登出")
        reply.button(QMessageBox.StandardButton.No).setText("取消")

        reply.exec()

        if reply.clickedButton() == reply.button(QMessageBox.StandardButton.Yes):
            self.parent.setMenuBar(None)
            from main_password_widget import MainPasswordWidget
            self.parent.setCentralWidget(MainPasswordWidget(self.parent))
        

    # 載入名稱列表
    def load_names(self):
        self.name_list.clear()
        names = self.db_manager.get_all_names()
        for name in names:
            item = QListWidgetItem(name[0])
            self.name_list.addItem(item)

    # 清除搜尋框
    def clear_search_box(self):
        self.search_box.clear()

    # 根據搜尋文字過濾名稱列表
    def filter_names(self):
        search_text = self.search_box.text().lower()
        self.clear_action.setVisible(bool(search_text))

        for index in range(self.name_list.count()):
            item = self.name_list.item(index)
            item.setHidden(search_text not in item.text().lower())

    # 添加新名稱項目
    def add_name(self):
        dialog = AddNameDialog(self)
        if dialog.exec():
            name, account, password, notes = dialog.name, dialog.account, dialog.password, dialog.notes
            self.db_manager.add_password_entry(name, account, password, notes)
            self.load_names()

    # 查看帳號密碼詳情
    def view_account_password(self, item):
        name = item.text()
        account, password, notes = self.db_manager.get_password_entry(name)

        dialog = ViewPasswordDialog(self, name, account, password, notes)
        dialog.exec()

    # 更新資料庫中的項目順序
    def update_order_in_database(self):
        name_order_dict = {}
        for i in range(self.name_list.count()):
            name = self.name_list.item(i).text()
            name_order_dict[name] = i
        
        self.db_manager.update_order_indices(name_order_dict)

    def handle_edit(self, item):
        name = item.text()
        if edit_password_entry(self, self.db_manager, name):
            self.load_names()

    def handle_delete(self, item):
        name = item.text()
        if delete_password_entry(self, self.db_manager, name):
            self.load_names()
