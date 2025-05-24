from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                            QListWidget, QHBoxLayout, QAbstractItemView, QMessageBox,
                            QListWidgetItem, QMenuBar, QMenu, QComboBox, QStyle)
from PyQt6.QtCore import Qt, QTimer, QThreadPool
from PyQt6.QtGui import QFont, QAction

from dialogs.add_password import AddNameDialog
from dialogs.view_password import ViewPasswordDialog
from dialogs.password_operations import edit_password_entry, delete_password_entry
from utils.import_export_manager import ImportExportManager

# 帳號列表介面
class NameListWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.thread_pool = QThreadPool()

        self.db_manager = parent.db_manager
        self.settings_manager = parent.settings_manager
        self.import_export_manager = ImportExportManager(self, self.db_manager)
        
        self.init_ui()
        self.setup_menu()

        QTimer.singleShot(0, self.load_names)

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

    # 匯入檔案功能（橋接方法）
    def import_from_file(self):
        self.import_export_manager.import_from_file()

    # 匯出資料功能（橋接方法）
    def export_to_csv(self):
        self.import_export_manager.export_to_csv()

    # 匯出當前篩選的資料
    def export_filtered_data(self):
        current_category = self.category_combo.currentText()
        self.import_export_manager.export_filtered_data(current_category)

    # 開啟設定頁面
    def open_settings(self):
        from preferences.settings_widget import SettingsWidget
        self.parent.setCentralWidget(SettingsWidget(self.parent))

    def init_ui(self):
        layout = QVBoxLayout()

        # 搜尋區域
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜尋")
        self.search_box.textChanged.connect(self.filter_names)
        
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
        self.clear_action = QAction(icon, "清除", self.search_box)
        self.clear_action.triggered.connect(self.clear_search_box)
        self.search_box.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)
        self.clear_action.setVisible(False)  # 預設不顯示
        
        self.search_box.setFont(QFont("Arial", 12))
        search_layout.addWidget(self.search_box)

        # 分類下拉選單
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(120)
        self.category_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.category_combo.addItem("全部")
        for category in self.settings_manager.get_categories():
            self.category_combo.addItem(category)
        self.category_combo.currentTextChanged.connect(self.load_names_by_category)
        search_layout.addWidget(self.category_combo)

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

        context_menu = QMenu(self)

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
            from app.main_password_widget import MainPasswordWidget
            self.parent.setCentralWidget(MainPasswordWidget(self.parent))
        

    def load_names(self):
        self.load_names_by_category(self.category_combo.currentText())

    def load_names_by_category(self, category):
        self.name_list.clear()
        if category == "全部":
            names = self.db_manager.get_all_names()
        else:
            names = self.db_manager.get_names_by_category(category)

        for name in names:
            item = QListWidgetItem(name)
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
            name = dialog.name
            account = dialog.account
            password = dialog.password
            notes = dialog.notes
            category = dialog.category
            self.db_manager.add_password_entry(name, account, password, notes, category)
            self.load_names_by_category(self.category_combo.currentText())

    # 查看帳號密碼詳情
    def view_account_password(self, item):
        name = item.text()
        account, password, notes, category = self.db_manager.get_password_entry(name)

        dialog = ViewPasswordDialog(self, name, account, password, notes, category)
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