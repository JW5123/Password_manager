from PyQt6.QtCore import QObject

class CloseDialogManager(QObject):
    
    CLOSE_TO_TRAY = "tray"
    QUIT_APPLICATION = "quit"
    
    def __init__(self, parent_window, settings_manager=None):
        super().__init__()
        self.parent_window = parent_window
        self.settings_manager = settings_manager
    
    def get_close_action(self, tray_available=True):
        if not self.settings_manager:
            # 如果沒有設定管理器，根據托盤可用性決定
            return self.CLOSE_TO_TRAY if tray_available else self.QUIT_APPLICATION
        
        # 獲取設定的關閉動作
        close_action = self.settings_manager.get_close_action()
        
        if close_action == "tray":
            # 如果設定為托盤但托盤不可用，則退出
            return self.CLOSE_TO_TRAY if tray_available else self.QUIT_APPLICATION
        elif close_action == "quit":
            return self.QUIT_APPLICATION
        else:
            # 預設行為：如果有未預期的值，根據托盤可用性決定
            return self.CLOSE_TO_TRAY if tray_available else self.QUIT_APPLICATION
    
    def should_minimize_to_tray(self, tray_available=True):
        action = self.get_close_action(tray_available)
        return action == self.CLOSE_TO_TRAY
    
    def should_quit_application(self, tray_available=True):
        action = self.get_close_action(tray_available)
        return action == self.QUIT_APPLICATION
    
    def should_cancel_close(self, tray_available=True):
        return False
    
    # 重置關閉選擇設定為預設值（最小化到托盤）
    def reset_close_choice(self):
        if self.settings_manager:
            self.settings_manager.set_close_action("tray")