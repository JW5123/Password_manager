from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QIcon

from Database.db_manager import DBManager
from utils.path_helper import resource_path
from app.main_password_widget import MainPasswordWidget
from preferences.settings_manager import SettingsManager
from system.auto_logout_manager import AutoLogoutManager
from system.system_tray_manager import SystemTrayManager
from system.close_dialog_manager import CloseDialogManager

from modules.main import MainWindowController
from modules.main import ActivityEventFilter
from modules.main import TrayController

class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(resource_path('icon/PasswordManager.ico')))
        self.setWindowTitle("密碼管理器")
        self.setGeometry(100, 100, 600, 500)

        self.db_manager = DBManager()
        self.settings_manager = SettingsManager()
        self.auto_logout_manager = AutoLogoutManager(self)
        self.tray_manager = SystemTrayManager(self)
        self.close_dialog_manager = CloseDialogManager(self, self.settings_manager)

        self.controller = MainWindowController(self)
        self.tray_controller = TrayController(self)

        self.auto_logout_manager.logout_requested.connect(self.controller.handle_auto_logout)
        self.tray_manager.settings_requested.connect(self.controller.open_settings)

        self.settings_manager.apply_theme(self)
        self.main_password_widget = MainPasswordWidget(self)
        self.setCentralWidget(self.main_password_widget)

        if self.tray_manager.is_tray_available():
            self.tray_manager.show_tray_icon()

        self.center_window()

        self.event_filter = ActivityEventFilter(self.on_user_activity)
        QApplication.instance().installEventFilter(self.event_filter)

    def center_window(self):
        screen = self.screen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def on_user_activity(self):
        self.auto_logout_manager.reset_timer()

    def on_settings_updated(self):
        self.auto_logout_manager.update_settings()

    def closeEvent(self, event):
        is_tray_available = self.tray_manager.is_tray_available()
        close_action = self.close_dialog_manager.get_close_action(is_tray_available)

        if close_action == self.close_dialog_manager.CLOSE_TO_TRAY:
            event.ignore()
            self.tray_controller.minimize_to_tray()
        else:
            event.accept()
            if is_tray_available:
                self.tray_manager.hide_tray_icon()
            try:
                self.db_manager.close()
            except Exception as e:
                print(f"資料庫關閉失敗: {e}")

    def changeEvent(self, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                if self.settings_manager.get_close_action() == "tray" and self.tray_manager.is_tray_available():
                    event.ignore()
                    self.hide()
        super().changeEvent(event)
