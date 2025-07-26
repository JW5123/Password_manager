from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                            QListWidget, QHBoxLayout, QAbstractItemView, QMessageBox,
                            QListWidgetItem, QMenuBar, QMenu, QComboBox, QStyle)
from PyQt6.QtCore import Qt, QTimer, QThreadPool, QSize
from PyQt6.QtGui import QFont, QAction

from utils.svg_icon_add import IconHelper

class AccountListUI(QWidget):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.thread_pool = QThreadPool()
        
        # 初始化UI元件
        self.init_ui_components()
        self.setup_layout()
        self.setup_menu()
        
        # 延遲初始化
        QTimer.singleShot(0, self.on_ui_ready)
    
    def init_ui_components(self):
        # 搜尋框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜尋")
        self.search_box.setFont(QFont("Arial", 16))
        
        # 清除按鈕
        clear_icon = IconHelper.get_clear_icon(self.parent, QSize(20, 20))
        self.clear_action = QAction(clear_icon, "清除", self.search_box)
        self.search_box.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)
        self.clear_action.setVisible(False)
        
        # 分類下拉選單
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(120)
        self.category_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        
        # 新增按鈕
        self.add_button = QPushButton("新增資料")
        # 設定外框邊距
        self.setContentsMargins(10, 0, 10, 10)
        # 名稱列表
        self.name_list = QListWidget()
        self.name_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.name_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.name_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    
    def setup_layout(self):
        layout = QVBoxLayout()
        
        # 搜尋區域
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.category_combo)
        search_layout.addWidget(self.add_button)
        
        layout.addLayout(search_layout)
        layout.addWidget(self.name_list)
        
        self.setLayout(layout)
    
    def setup_menu(self):
        menu_bar = QMenuBar()
        self.parent.setMenuBar(menu_bar)
        
        # 帳戶選單
        self.account_menu = menu_bar.addMenu("帳戶")
        self.account_menu.setIcon(IconHelper.get_user_icon(self.parent, QSize(60, 60)))
        
        logout_icon = IconHelper.get_logout_icon(self.parent, QSize(60, 60))
        self.logout_action = QAction(logout_icon, "登出", self)
        self.account_menu.addAction(self.logout_action)
        
        # 檔案選單
        self.file_menu = menu_bar.addMenu("檔案")
        import_icon = IconHelper.get_import_icon(self.parent, QSize(60, 60))
        self.import_action = QAction(import_icon, "匯入", self)
        self.file_menu.addAction(self.import_action)
        export_icon = IconHelper.get_export_icon(self.parent, QSize(60, 60))
        self.export_action = QAction(export_icon, "匯出", self)
        self.file_menu.addAction(self.export_action)
        
        # 設定選單
        self.settings_menu = menu_bar.addMenu("設定")
        settings_icon = IconHelper.get_settings_icon(self.parent, QSize(60, 60))
        self.settings_action = QAction(settings_icon, "設定", self)
        self.settings_menu.addAction(self.settings_action)
        
        # 說明選單
        self.help_menu = menu_bar.addMenu("說明")
        about_icon = IconHelper.get_about_icon(self.parent, QSize(60, 60))
        self.about_action = QAction(about_icon, "關於", self)
        self.help_menu.addAction(self.about_action)
    
    def create_context_menu(self, position):
        item = self.name_list.itemAt(position)
        if item is None:
            return None
            
        context_menu = QMenu(self)
        
        view_action = QAction("查看", self)
        edit_action = QAction("編輯", self)
        delete_action = QAction("刪除", self)
        
        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)
        
        return context_menu, view_action, edit_action, delete_action, item
    
    def show_logout_confirmation(self):
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要登出嗎？')
        reply.setIcon(QMessageBox.Icon.Question)
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply.button(QMessageBox.StandardButton.Yes).setText("登出")
        reply.button(QMessageBox.StandardButton.No).setText("取消")
        
        reply.exec()
        return reply.clickedButton() == reply.button(QMessageBox.StandardButton.Yes)
    
    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "關於",
            "密碼管理器 v2.0.0\n\n"
            "© 2024 版權所有"
        )
    
    def clear_list(self):
        self.name_list.clear()
    
    def add_list_item(self, name):
        item = QListWidgetItem(name)
        self.name_list.addItem(item)
        return item
    
    def update_category_combo(self, categories, current_text=None):
        self.category_combo.clear()
        self.category_combo.addItem("全部")
        for category in categories:
            self.category_combo.addItem(category)
        
        if current_text:
            index = self.category_combo.findText(current_text)
            if index != -1:
                self.category_combo.setCurrentIndex(index)
    
    def filter_list_items(self, search_text):
        self.clear_action.setVisible(bool(search_text))
        search_text = search_text.lower()
        
        for index in range(self.name_list.count()):
            item = self.name_list.item(index)
            item.setHidden(search_text not in item.text().lower())
    
    def get_item_order(self):
        name_order_dict = {}
        for i in range(self.name_list.count()):
            name = self.name_list.item(i).text()
            name_order_dict[name] = i
        return name_order_dict
    
    def on_ui_ready(self):
        pass