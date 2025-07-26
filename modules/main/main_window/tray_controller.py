from PyQt6.QtWidgets import QApplication

class TrayController:
    def __init__(self, window):
        self.window = window
        self.tray_manager = window.tray_manager

        self.tray_manager.show_requested.connect(self.show_from_tray)
        self.tray_manager.quit_requested.connect(self.quit_from_tray)

    def show_from_tray(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def minimize_to_tray(self):
        if self.tray_manager.is_tray_available():
            self.tray_manager.show_tray_icon()
            self.window.hide()
        else:
            self.window.showMinimized()

    def quit_from_tray(self):
        self.tray_manager.hide_tray_icon()
        self.window.db_manager.close()
        QApplication.quit()
