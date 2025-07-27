from preferences.constants import AUTO_LOGOUT_OPTIONS, CLOSE_ACTION_OPTIONS

class SystemSettings:
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.AUTO_LOGOUT_OPTIONS = AUTO_LOGOUT_OPTIONS
        self.CLOSE_ACTION_OPTIONS = CLOSE_ACTION_OPTIONS
    
    # 取得自動登出時間設定
    def get_auto_logout_timeout(self):
        try:
            return float(self.settings_manager.settings.get('auto_logout_timeout', 0))
        except (ValueError, TypeError):
            return 0

    # 設定自動登出時間
    def set_auto_logout_timeout(self, timeout):
        self.settings_manager.settings['auto_logout_timeout'] = timeout
        return self.settings_manager.save_settings()

    # 根據時間值取得對應的顯示文字
    def get_auto_logout_display_text(self, timeout_value=None):
        if timeout_value is None:
            timeout_value = self.get_auto_logout_timeout()
        
        for display_text, value in self.AUTO_LOGOUT_OPTIONS.items():
            if value == timeout_value:
                return display_text
        
        return "持續登入"  # 預設值

    # 根據顯示文字取得對應的時間值
    def get_auto_logout_value_from_text(self, display_text):
        return self.AUTO_LOGOUT_OPTIONS.get(display_text, 0)

    # 取得所有可用的自動登出選項
    def get_available_auto_logout_options(self):
        return list(self.AUTO_LOGOUT_OPTIONS.keys())
    
    # 關閉動作相關方法
    def get_close_action(self):
        action = self.settings_manager.settings.get('close_action', 'tray')
        
        # 確保設定值有效，如果無效則設為預設值
        if action not in ["tray", "quit"]:
            action = "tray"
            self.set_close_action(action)
        
        return action

    # 設定關閉動作
    def set_close_action(self, action):
        if action in ["tray", "quit"]:
            self.settings_manager.settings['close_action'] = action
            return self.settings_manager.save_settings()
        return False

    # 根據動作值取得對應的顯示文字
    def get_close_action_display_text(self, action_value=None):
        if action_value is None:
            action_value = self.get_close_action()
        
        for display_text, value in self.CLOSE_ACTION_OPTIONS.items():
            if value == action_value:
                return display_text
        
        return "最小化到托盤"  # 預設值

    # 根據顯示文字取得對應的動作值
    def get_close_action_value_from_text(self, display_text):
        return self.CLOSE_ACTION_OPTIONS.get(display_text, 'tray')

    # 取得所有可用的關閉動作選項
    def get_available_close_action_options(self):
        return list(self.CLOSE_ACTION_OPTIONS.keys())
    
    # 取得所有系統設定
    def get_system_settings(self):
        return {
            'auto_logout_timeout': self.get_auto_logout_timeout(),
            'close_action': self.get_close_action()
        }
    
    # 批量設定系統設定
    def set_system_settings(self, auto_logout_timeout=None, close_action=None):
        success = True
        
        if auto_logout_timeout is not None:
            self.settings_manager.settings['auto_logout_timeout'] = auto_logout_timeout
        
        if close_action is not None and close_action in ["tray", "quit"]:
            self.settings_manager.settings['close_action'] = close_action
        elif close_action is not None:
            success = False
        
        if success:
            return self.settings_manager.save_settings()
        
        return False