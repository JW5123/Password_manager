import json
import os
from utils.path_helper import get_settings_path
from .constants import THEMES, AUTO_LOGOUT_OPTIONS, CLOSE_ACTION_OPTIONS
from modules.settings import ThemeSettings, SystemSettings, CategorySettings

class SettingsManager:
    
    def __init__(self):
        self.settings_path = get_settings_path()
        self.settings = self.load_settings()
        
        # 初始化各個設定模組
        self.theme_settings = ThemeSettings(self)
        self.category_settings = CategorySettings(self)
        self.system_settings = SystemSettings(self)

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                    if 'theme' not in settings:
                        settings['theme'] = "System"
                    if 'categories' not in settings:
                        settings['categories'] = []
                    if 'auto_logout_timeout' not in settings:
                        settings['auto_logout_timeout'] = 0
                    if 'close_action' not in settings:
                        settings['close_action'] = "tray"
                    return settings
            except Exception as e:
                print(f"載入設定錯誤 {e}")
        
        # 若不存在則建立預設設定
        default = {
            "theme": "System", 
            "categories": [], 
            "auto_logout_timeout": 0,
            "close_action": "tray"
        }
        self.save_settings(default)
        return default
    
    # === 主題相關方法 ===
    def get_effective_theme(self, theme_name):
        return self.theme_settings.get_effective_theme(theme_name)

    def is_dark_theme(self, theme_name=None):
        return self.theme_settings.is_dark_theme(theme_name)

    def get_theme(self):
        return self.theme_settings.get_theme()

    def get_theme_file(self):
        return self.theme_settings.get_theme_file()

    def apply_theme(self, widget):
        return self.theme_settings.apply_theme(widget)

    def set_theme(self, theme_name, widget=None):
        return self.theme_settings.set_theme(theme_name, widget)
    
    # === 分類相關方法 ===
    def get_categories(self):
        return self.category_settings.get_categories()

    def set_categories(self, category_list):
        return self.category_settings.set_categories(category_list)
    
    # === 系統設定相關方法 ===
    def get_auto_logout_timeout(self):
        return self.system_settings.get_auto_logout_timeout()

    def set_auto_logout_timeout(self, timeout):
        return self.system_settings.set_auto_logout_timeout(timeout)

    def get_close_action(self):
        return self.system_settings.get_close_action()

    def set_close_action(self, action):
        return self.system_settings.set_close_action(action)

    # === 通用設定方法 ===
    def get_setting(self, key, default_value=None):
        return self.settings.get(key, default_value)

    def set_setting(self, key, value):
        self.settings[key] = value
        return self.save_settings()
    
    def save_settings(self, settings=None):
        if settings is not None:
            self.settings = settings

        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            print(f"設定已儲存 {self.settings_path}")
            return True
        except Exception as e:
            print(f"儲存設定錯誤 {e}")
            return False