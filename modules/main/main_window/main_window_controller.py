from app import main_password_widget
from preferences.settings_widget import SettingsWidget

class MainWindowController:
    def __init__(self, window):
        self.window = window

    def login_success(self):
        self.window.auto_logout_manager.update_settings()
        self.window.auto_logout_manager.start_monitoring()

        if self.window.tray_manager.is_tray_available():
            if not self.window.tray_manager.tray_icon or not self.window.tray_manager.tray_icon.isVisible():
                self.window.tray_manager.show_tray_icon()

    def handle_auto_logout(self):
        self.window.setMenuBar(None)
        self.window.main_password_widget = main_password_widget.MainPasswordWidget(self.window)
        self.window.setCentralWidget(self.window.main_password_widget)
        self.window.auto_logout_manager.stop_monitoring()

    def open_settings(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()
        try:
            settings_widget = SettingsWidget(self.window)
            self.window.setCentralWidget(settings_widget)
        except Exception as e:
            print(f"無法開啟設定頁面: {e}")
