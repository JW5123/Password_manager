from app import main_password_widget
from preferences.settings_widget import SettingsWidget
from system.single_instance_manager import SingleInstanceManager
import sys

class MainWindowController:
    def __init__(self, window):
        self.window = window
        self.is_loging_in = False
        
        # 單實例檢查 - 使用唯一的名稱
        self.single_instance_manager = SingleInstanceManager("PasswordManager_UniqueInstance_2024")
        if self.single_instance_manager.is_already_running():
            # 如果已有實例在運行，發送顯示信號後立即退出
            sys.exit(0)
        
        # 連接顯示窗口訊號
        self.single_instance_manager.show_window_requested.connect(self.show_from_second_instance)

    def login_success(self):
        self.is_loging_in = True

        self.window.auto_logout_manager.update_settings()
        self.window.auto_logout_manager.start_monitoring()

        if self.window.tray_manager.is_tray_available():
            if not self.window.tray_manager.tray_icon or not self.window.tray_manager.tray_icon.isVisible():
                self.window.tray_manager.show_tray_icon()

    def handle_auto_logout(self):
        self.is_loging_in = False

        self.window.setMenuBar(None)
        self.window.main_password_widget = main_password_widget.MainPasswordWidget(self.window)
        self.window.setCentralWidget(self.window.main_password_widget)
        self.window.auto_logout_manager.stop_monitoring()

    def open_settings(self):
        # 首先檢查主密碼是否已設定
        if not self.window.db_manager.has_master_password():
            # 主密碼尚未設定，顯示窗口但保持在主密碼設定畫面
            self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
            return

        # 檢查是否已登入
        if not self.is_loging_in:
            # 尚未登入，顯示窗口但保持在登入畫面
            self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
            return

        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()
        try:
            settings_widget = SettingsWidget(self.window)
            self.window.setCentralWidget(settings_widget)
        except Exception as e:
            print(f"無法開啟設定頁面: {e}")

    # 當有第二個實例嘗試啟動時顯示窗口
    def show_from_second_instance(self):
        if self.window.isMinimized() or self.window.isHidden():
            self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    # 清理單實例管理器資源
    def cleanup_single_instance(self):
        if hasattr(self, 'single_instance_manager') and self.single_instance_manager:
            self.single_instance_manager.cleanup()