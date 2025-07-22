from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal
from utils.path_helper import resource_path
from styles.tray_styles import TrayStyleConfig

class SystemTrayManager(QObject):

    # 定義信號
    show_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    about_requested = pyqtSignal()
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.tray_icon = None
        self.setup_tray_icon()
    
    # 設置系統托盤圖標
    def setup_tray_icon(self):
        # 檢查系統是否支持托盤
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                self.parent_window,
                "系統托盤",
                "此系統不支援系統托盤功能。"
            )
            return False
        
        # 創建托盤圖標
        self.tray_icon = QSystemTrayIcon(self.parent_window)
        
        try:
            icon = QIcon(resource_path('icon/PasswordManager.ico'))
            if icon.isNull():
                print("警告：無法載入托盤圖標")
                # 嘗試創建一個默認圖標
                icon = self.parent_window.style().standardIcon(
                    self.parent_window.style().StandardPixmap.SP_ComputerIcon
                )
            self.tray_icon.setIcon(icon)
        except Exception as e:
            print(f"設置托盤圖標時發生錯誤: {e}")
            return False
        
        self.tray_icon.setToolTip("密碼管理器")
        
        # 創建右鍵選單
        self.create_tray_menu()
        
        # 連接托盤圖標點擊事件
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        return True
    
    def update_tray_theme(self):
        self.create_tray_menu()  # 重新創建選單以應用新主題
    
    # 創建托盤右鍵選單
    def create_tray_menu(self):
        tray_menu = QMenu()
        
        # 應用主題樣式
        if hasattr(self.parent_window, 'settings_manager'):
            is_dark = self.parent_window.settings_manager.is_dark_theme()
        else:
            is_dark = False
            
        tray_menu.setStyleSheet(TrayStyleConfig().get_style(is_dark))
        
        # 顯示主窗口
        show_action = QAction("開啟密碼管理器", self.parent_window)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        # 分隔線
        tray_menu.addSeparator()
        
        # 設定
        settings_action = QAction("設定", self.parent_window)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)
        
        # 檢查更新
        update_action = QAction("檢查更新", self.parent_window)
        update_action.triggered.connect(self.check_updates)
        tray_menu.addAction(update_action)
        
        # 分隔線
        tray_menu.addSeparator()
        
        # 關於
        about_action = QAction("關於", self.parent_window)
        about_action.triggered.connect(self.show_about)
        tray_menu.addAction(about_action)
        
        # 分隔線
        tray_menu.addSeparator()
        
        # 退出程式
        quit_action = QAction("退出密碼管理器", self.parent_window)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
    
    def on_tray_activated(self, reason):
        # 修正：處理左鍵點擊和雙擊事件
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:  # 左鍵單擊
            self.show_main_window()
        # 右鍵點擊會自動顯示選單，不需要特別處理
    
    def show_main_window(self):
        self.show_requested.emit()
    
    def quit_application(self):
        self.quit_requested.emit()
    
    def open_settings(self):
        self.settings_requested.emit()
    
    def check_updates(self):
        QMessageBox.information(
            self.parent_window,
            "檢查更新",
            "目前使用的是最新版本！"
        )
    
    def show_about(self):
        """顯示關於信息"""
        QMessageBox.about(
            self.parent_window,
            "關於密碼管理器",
            "密碼管理器 v1.0\n\n"
            "一個安全、便捷的密碼管理工具\n"
            "© 2024 版權所有"
        )
    
    def show_tray_icon(self):
        if not self.tray_icon:
            # 如果托盤圖標不存在，重新創建
            if not self.setup_tray_icon():
                return False
        
        # 確保圖標已設置
        if self.tray_icon.icon().isNull():
            print("警告：托盤圖標為空，重新設置")
            try:
                icon = QIcon(resource_path('icon/PasswordManager.ico'))
                if icon.isNull():
                    # 如果仍然無法載入，使用系統默認圖標
                    icon = self.parent_window.style().standardIcon(
                        self.parent_window.style().StandardPixmap.SP_ComputerIcon
                    )
                self.tray_icon.setIcon(icon)
            except Exception as e:
                print(f"重新設置托盤圖標時發生錯誤: {e}")
                return False
        
        if self.tray_icon:
            self.tray_icon.show()
            return True
        return False
    
    def hide_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.hide()
    
    # 檢查系統托盤是否可用
    def is_tray_available(self):
        return QSystemTrayIcon.isSystemTrayAvailable()
    
    # 在托盤顯示通知訊息
    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, timeout=5000):
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)