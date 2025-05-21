from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QGroupBox, QMessageBox, QListWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from settings_manager import SettingsManager

class SettingsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # 使用設定管理器
        self.settings_manager = parent.settings_manager
        
        # 取得設定
        self.settings = self.settings_manager.load_settings()

        self.temp_theme = self.settings.get('theme', 'Light Blue')
        
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
        current_theme = self.settings.get('theme', 'Light Blue')
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.theme_combo.currentTextChanged.connect(self.theme_changed)
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_layout)
        
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)
        
        # 分類設定
        category_group = QGroupBox("分類設定")
        category_layout = QVBoxLayout()

        

        category_group.setLayout(category_layout)
        main_layout.addWidget(category_group)


        # 按鈕區域
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("儲存設定")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("返回")
        self.cancel_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
    
    # 主題選擇變更時觸發
    def theme_changed(self, theme_name):
        self.temp_theme = theme_name
    
    # 儲存設定
    def save_settings(self):
        # 更新設定
        self.settings['theme'] = self.temp_theme

        if self.settings_manager.save_settings(self.settings):
            # 套用主題
            self.settings_manager.set_theme(self.temp_theme, self.parent)
            # QMessageBox.information(self, "訊息", "設定已儲存")
        else:
            QMessageBox.warning(self, "錯誤", "無法儲存設定")
    
    # 返回主畫面
    def go_back(self):
        from name_list_widget import NameListWidget
        self.parent.setCentralWidget(NameListWidget(self.parent))