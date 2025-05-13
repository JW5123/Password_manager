from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                             QListWidget, QHBoxLayout, QAbstractItemView, QFileDialog, QMessageBox,
                             QListWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction, QIcon

import csv
from dialogs.add_password import AddNameDialog
from dialogs.view_password import ViewPasswordDialog

class NameListWidget(QWidget):
    """名稱列表界面"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = parent.db_manager
        self.init_ui()

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

        # 行移動信號連接 (在PyQt6中略微不同)
        self.name_list.model().rowsMoved.connect(self.update_order_in_database)
        layout.addWidget(self.name_list)

        button_layout = QHBoxLayout()

        # 匯出按鈕
        self.export_button = QPushButton("匯出")
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.export_button)

        # 新增資料按鈕
        self.add_button = QPushButton("新增資料")
        self.add_button.clicked.connect(self.add_name)
        button_layout.addWidget(self.add_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.load_names()

    def export_to_csv(self):
        """匯出資料為CSV檔案"""
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "儲存 CSV 檔案", "密碼儲存簿.csv", 
            "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_path:
            if not file_path.endswith('.csv'):
                file_path += '.csv'

            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(['名稱', '帳號', '密碼', '備註'])

                # 取得所有項目
                entries = self.db_manager.get_all_entries()
                for row in entries:
                    writer.writerow(row)

            QMessageBox.information(self, "訊息", "資料成功匯出至 CSV 檔案")

    def logout(self):
        """登出帳戶"""
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要登出嗎？')

        reply.setIcon(QMessageBox.Icon.Question)
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply.button(QMessageBox.StandardButton.Yes).setText("登出")
        reply.button(QMessageBox.StandardButton.No).setText("取消")

        reply.exec()

        if reply.clickedButton() == reply.button(QMessageBox.StandardButton.Yes):
            from main_password_widget import MainPasswordWidget
            self.parent.setCentralWidget(MainPasswordWidget(self.parent))

    def load_names(self):
        """載入名稱列表"""
        self.name_list.clear()
        names = self.db_manager.get_all_names()
        for name in names:
            item = QListWidgetItem(name[0])
            self.name_list.addItem(item)

    def clear_search_box(self):
        """清除搜尋框"""
        self.search_box.clear()

    def filter_names(self):
        """根據搜尋文字過濾名稱列表"""
        search_text = self.search_box.text().lower()
        self.clear_action.setVisible(bool(search_text))

        for index in range(self.name_list.count()):
            item = self.name_list.item(index)
            item.setHidden(search_text not in item.text().lower())

    def add_name(self):
        """添加新名稱項目"""
        dialog = AddNameDialog(self)
        if dialog.exec():
            name, account, password, notes = dialog.name, dialog.account, dialog.password, dialog.notes
            self.db_manager.add_password_entry(name, account, password, notes)
            self.load_names()

    def view_account_password(self, item):
        """查看帳號密碼詳情"""
        name = item.text()
        account, password, notes = self.db_manager.get_password_entry(name)

        dialog = ViewPasswordDialog(self, name, account, password, notes)
        dialog.exec()

    def update_order_in_database(self):
        """更新資料庫中的項目順序"""
        name_order_dict = {}
        for i in range(self.name_list.count()):
            name = self.name_list.item(i).text()
            name_order_dict[name] = i
        
        self.db_manager.update_order_indices(name_order_dict)