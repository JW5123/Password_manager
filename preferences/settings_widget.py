from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QGroupBox, QMessageBox, QListWidget,
                            QListWidgetItem, QScrollArea, QDialog, QLineEdit, QFormLayout, 
                            QDialogButtonBox, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from preferences.settings_manager import SettingsManager

class SettingsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # 使用設定管理器
        self.settings_manager = parent.settings_manager
        
        # 取得設定
        self.settings = self.settings_manager.load_settings()

        self.temp_theme = self.settings.get('theme', 'System')

        self.temp_categories = self.settings.get('categories', []).copy()
        
        self.init_ui()
        
    def init_ui(self):
        # 建立主佈局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 建立標題
        title_label = QLabel("設定")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 外觀設定組
        appearance_group = QGroupBox("外觀設定")
        appearance_layout = QVBoxLayout()
        
        # 主題選擇
        theme_layout = QHBoxLayout()
        theme_label = QLabel("主題:")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        for theme_name in SettingsManager.THEMES.keys():
            self.theme_combo.addItem(theme_name)
        
        # 設置當前主題
        current_theme = self.settings.get('theme', 'System')
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.theme_combo.currentTextChanged.connect(self.theme_changed)
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_layout)
        
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)
        
        category_group = QGroupBox("分類設定")
        category_outer_layout = QHBoxLayout()

        # 新增分類按鈕
        self.add_category_button = QPushButton("新增分類")
        self.add_category_button.clicked.connect(self.add_category_dialog)
        category_outer_layout.addWidget(self.add_category_button)

        # 分類列表（可滾動）
        self.category_list_widget = QListWidget()
        self.category_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.category_list_widget.customContextMenuRequested.connect(self.show_category_menu)
        for cat in self.temp_categories:
            self.category_list_widget.addItem(cat)
        category_outer_layout.addWidget(self.category_list_widget)

        category_group.setLayout(category_outer_layout)
        main_layout.addWidget(category_group)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(main_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        full_layout = QVBoxLayout()
        full_layout.addWidget(scroll_area)

        # 底部按鈕區固定
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("儲存設定")
        self.save_button.clicked.connect(lambda: self.save_settings(show_message=True))
        self.cancel_button = QPushButton("返回")
        self.cancel_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        full_layout.addLayout(button_layout)
        self.setLayout(full_layout)

    # 主題選擇變更時觸發
    def theme_changed(self, theme_name):
        self.temp_theme = theme_name

    def add_category_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("新增分類")
        dialog.setFixedSize(300, 150)  # 可調整視窗大小

        layout = QVBoxLayout()

        # 標籤
        label = QLabel("分類名稱")
        layout.addWidget(label)

        # 輸入欄位
        input_field = QLineEdit()
        layout.addWidget(input_field)

        # 按鈕區域（水平排列）
        button_layout = QHBoxLayout()
        add_button = QPushButton("新增")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        # 連接按鈕事件
        add_button.clicked.connect(lambda: self.confirm_add_category(dialog, input_field.text()))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

    def confirm_add_category(self, dialog, category_name):
        category_name = category_name.strip()
        if not category_name.strip():
            QMessageBox.warning(self, "錯誤", "分類名稱不能為空白")
            return

        if not category_name or category_name in self.temp_categories:
            QMessageBox.warning(self, "錯誤", "分類名稱無效或已存在")
            return
        self.temp_categories.append(category_name)
        self.category_list_widget.addItem(category_name)
        dialog.accept()

    def show_category_menu(self, pos):
        item = self.category_list_widget.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        delete_action = menu.addAction("刪除分類")
        action = menu.exec(self.category_list_widget.mapToGlobal(pos))
        if action == delete_action:
            category_name = item.text()
            # 從臨時列表中移除
            if category_name in self.temp_categories:
                self.temp_categories.remove(category_name)
            # 從列表widget中移除
            row = self.category_list_widget.row(item)
            self.category_list_widget.takeItem(row)

    def has_unsaved_changes(self):
        current_theme = self.settings.get('theme', 'System')
        current_categories = self.settings.get('categories', [])
        
        # 檢查主題是否有變更
        if self.temp_theme != current_theme:
            return True
        
        # 檢查分類是否有變更（比較長度和內容）
        if len(self.temp_categories) != len(current_categories):
            return True
        
        # 檢查分類內容是否相同（保持順序）
        if self.temp_categories != current_categories:
            return True
        
        return False
    
    # 儲存設定
    def save_settings(self, show_message=True):
        self.settings['theme'] = self.temp_theme
        self.settings['categories'] = self.temp_categories

        if self.settings_manager.save_settings(self.settings):
            self.settings_manager.settings = self.settings_manager.load_settings()
            self.settings_manager.set_theme(self.temp_theme, self.parent)
            if show_message:
                QMessageBox.information(self, "訊息", "設定已儲存")
            return True
        else:
            if show_message:
                QMessageBox.warning(self, "錯誤", "無法儲存設定")
            return False

    # 返回主畫面
    def go_back(self):
        if self.has_unsaved_changes():
            reply = QMessageBox(self)
            reply.setWindowTitle("未儲存的變更")
            reply.setText('您有未儲存的變更。要儲存嗎？')
            reply.setIcon(QMessageBox.Icon.Question)  
                            
            yes_button = reply.addButton("是", QMessageBox.ButtonRole.YesRole)                                         
            no_button = reply.addButton("否",  QMessageBox.ButtonRole.NoRole)

            reply.exec()                                                  

            if reply.clickedButton() == yes_button:                                
                if not self.save_settings(show_message=False):              
                    return
        
        # 返回帳號列表頁面
        from app.account_list_widget import NameListWidget
        self.parent.setCentralWidget(NameListWidget(self.parent))