from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QScrollArea, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from modules.settings import SystemDialog, CategoryDialog

class SettingsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.settings_manager = parent.settings_manager
        
        self.category_dialog = CategoryDialog(self.settings_manager, self)
        self.system_dialog = SystemDialog(self.settings_manager, self)
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("設定")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        self.tab_widget = QTabWidget()
        
        # 使用輔助方法建立可滾動的分頁
        self._add_scrollable_tab(self.category_dialog, "分類設定")
        self._add_scrollable_tab(self.system_dialog, "系統設定")
        
        main_layout.addWidget(self.tab_widget)

        # 底部按鈕區固定
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("儲存設定")
        self.cancel_button = QPushButton("返回")

        self.save_button.clicked.connect(lambda: self.save_settings(show_message=True))
        self.cancel_button.clicked.connect(self.go_back)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    # 建立可滾動的分頁
    def _add_scrollable_tab(self, widget, title):
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tab_widget.addTab(scroll_area, title)

    # 檢查是否有未儲存的變更
    def has_unsaved_changes(self):
        return (self.category_dialog.has_changes() or self.system_dialog.has_changes())
    
    # 儲存所有設定
    def save_settings(self, show_message=True):
        success = True
        error_messages = []

        # 儲存所有設定前，先套用所有變更
        dialogs = [
            (self.category_dialog, "分類設定儲存失敗"),
            (self.system_dialog, "系統設定儲存失敗"),
        ]
        for dialog, error_msg in dialogs:
            if dialog.has_changes():
                if not dialog.apply_changes():
                    success = False
                    error_messages.append(error_msg)

        if success:
            # 直接從 settings_manager 取得最新主題並套用
            if hasattr(self.parent, 'apply_theme') and callable(self.parent.apply_theme):
                self.parent.apply_theme()
            elif hasattr(self.settings_manager, 'apply_theme'):
                self.settings_manager.apply_theme(self.parent)

            if hasattr(self.parent, 'tray_manager'):
                self.parent.tray_manager.update_tray_theme()
            if show_message:
                QMessageBox.information(self, "訊息", "設定已儲存")
            return True
        else:
            if show_message:
                QMessageBox.warning(self, "錯誤", "儲存設定時發生錯誤:\n" + "\n".join(error_messages))
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
            elif reply.clickedButton() == no_button:
                # 如果選擇不儲存，重置所有變更
                self.reset_all_changes()
        
        # 返回帳號列表頁面
        from app.account_list_widget import NameListWidget
        self.parent.setCentralWidget(NameListWidget(self.parent))
    
    # 重置所有變更
    def reset_all_changes(self):
        self.category_dialog.reset_changes()
        self.system_dialog.reset_changes()