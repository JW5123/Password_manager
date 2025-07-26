from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal
from utils.path_helper import resource_path
from styles.tray_styles import TrayStyleConfig

class SystemTrayManager(QObject):
    show_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    about_requested = pyqtSignal()

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.tray_icon = None
        self.setup_tray_icon()

    def setup_tray_icon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(self.parent_window, "系統托盤", "此系統不支援系統托盤功能。")
            return False

        self.tray_icon = QSystemTrayIcon(self.parent_window)
        icon = QIcon(resource_path('icon/PasswordManager.ico'))
        if icon.isNull():
            icon = self.parent_window.style().standardIcon(
                self.parent_window.style().StandardPixmap.SP_ComputerIcon
            )
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("密碼管理器")
        self.create_tray_menu()
        self.tray_icon.activated.connect(self.on_tray_activated)
        return True

    def create_tray_menu(self):
        tray_menu = QMenu()
        is_dark = getattr(getattr(self.parent_window, 'settings_manager', None), 'is_dark_theme', lambda: False)()
        tray_menu.setStyleSheet(TrayStyleConfig().get_style(is_dark))

        actions = [
            ("設定", self.settings_requested.emit),
            ("檢查更新", lambda: QMessageBox.information(self.parent_window, "檢查更新", "目前使用的是最新版本！")),
            (None, None),  # Separator
            ("關於", lambda: QMessageBox.about(self.parent_window, "關於", "密碼管理器 v2.0.0\n\n© 2024 版權所有")),
            (None, None),  # Separator
            ("退出密碼管理器", self.quit_requested.emit)
        ]
        for text, slot in actions:
            if text:
                action = QAction(text, self.parent_window)
                action.triggered.connect(slot)
                tray_menu.addAction(action)
            else:
                tray_menu.addSeparator()
        self.tray_icon.setContextMenu(tray_menu)

    def update_tray_theme(self):
        if self.tray_icon and self.tray_icon.contextMenu():
            # 重新創建選單以應用新的主題樣式
            self.create_tray_menu()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_requested.emit()

    def show_tray_icon(self):
        if not self.tray_icon and not self.setup_tray_icon():
            return False
        if self.tray_icon.icon().isNull():
            icon = QIcon(resource_path('icon/PasswordManager.ico'))
            if icon.isNull():
                icon = self.parent_window.style().standardIcon(
                    self.parent_window.style().StandardPixmap.SP_ComputerIcon
                )
            self.tray_icon.setIcon(icon)
        self.tray_icon.show()
        return True

    def hide_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.hide()

    def is_tray_available(self):
        return QSystemTrayIcon.isSystemTrayAvailable()

    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, timeout=5000):
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)