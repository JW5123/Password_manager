from PyQt6.QtCore import QTimer, QObject, pyqtSignal

class AutoLogoutManager(QObject):
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings_manager = parent.settings_manager if parent else None
        
        self.logout_timer = QTimer(self)
        self.logout_timer.timeout.connect(self.auto_logout)
        self.logout_timer.setSingleShot(True)  # 只觸發一次
        
        self.logout_timeout = 0
        self.is_enabled = False
        
        self.load_settings()
    
    def load_settings(self):
        if self.settings_manager:
            self.logout_timeout = self.settings_manager.get_auto_logout_timeout()
            self.is_enabled = self.logout_timeout > 0
    
    def start_monitoring(self):
        if self.is_enabled and self.logout_timeout > 0:
            # 先停止現有的計時器，避免重複
            self.logout_timer.stop()
            # 設定計時器，時間到就自動登出
            self.logout_timer.start(int(self.logout_timeout * 60 * 1000)) # 轉換為毫秒
    
    def stop_monitoring(self):
        self.logout_timer.stop()
    
    def reset_timer(self):
        if self.is_enabled and self.logout_timeout > 0:
            # 先停止計時器
            self.logout_timer.stop()
            # 重新載入最新的設定，確保使用正確的時間
            self.load_settings()

            self.logout_timer.start(int(self.logout_timeout * 60 * 1000))
    
    def auto_logout(self):
        self.logout_requested.emit()
    
    def update_settings(self):
        self.load_settings()
        if self.logout_timer.isActive():
            self.start_monitoring()