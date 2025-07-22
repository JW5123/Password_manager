import json
import os
from qt_material import apply_stylesheet
from utils.path_helper import get_settings_path
from system.system_theme_detector import detect_system_theme
from .constants import THEMES, AUTO_LOGOUT_OPTIONS, CLOSE_ACTION_OPTIONS

class SettingsManager:
    
    def __init__(self):
        self.settings_path = get_settings_path()
        self.settings = self.load_settings()
        self.THEMES = THEMES
        self.AUTO_LOGOUT_OPTIONS = AUTO_LOGOUT_OPTIONS
        self.CLOSE_ACTION_OPTIONS = CLOSE_ACTION_OPTIONS


    def get_effective_theme(self, theme_name):
        if theme_name == "System":
            return detect_system_theme()
        return theme_name

    def is_dark_theme(self, theme_name=None):
        if theme_name is None:
            theme_name = self.get_theme()
        
        effective_theme = self.get_effective_theme(theme_name)
        return effective_theme == "Dark Blue"

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 確保設定包含必要的鍵值
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

    # 自動登出設定
    def get_auto_logout_timeout(self):
        try:
            return float(self.settings.get('auto_logout_timeout', 0))
        except (ValueError, TypeError):
            return 0

    def set_auto_logout_timeout(self, timeout):
        self.settings['auto_logout_timeout'] = timeout
        return self.save_settings()

    def get_close_action(self):
        action = self.settings.get('close_action', 'tray')
            
        self.set_close_action(action)

        return action

    def set_close_action(self, action):
        if action in ["tray", "quit"]:
            self.settings['close_action'] = action
            return self.save_settings()
        return False

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

    # 主題設定
    def get_theme(self):
        return self.settings.get('theme', 'System')

    def get_theme_file(self):
        theme_name = self.get_theme()
        effective_theme = self.get_effective_theme(theme_name)
        return self.THEMES.get(effective_theme, 'light_blue.xml')

    def apply_theme(self, widget):
        try:
            theme_file = self.get_theme_file()
            apply_stylesheet(widget, theme=theme_file)
            return True
        except Exception as e:
            print(f"套用主題錯誤 {e}")
            return False

    def set_theme(self, theme_name, widget=None):
        if theme_name in self.THEMES:
            self.settings['theme'] = theme_name
            if widget:
                try:
                    if theme_name == "System":
                        effective_theme = self.get_effective_theme(theme_name)
                        theme_file = self.THEMES.get(effective_theme, 'light_blue.xml')
                    else:
                        theme_file = self.THEMES[theme_name]
                    
                    apply_stylesheet(widget, theme=theme_file)
                except Exception as e:
                    print(f"套用主題錯誤 {e}")
                    return False
            return self.save_settings()
        return False

    # 分類設定
    def get_categories(self):
        return self.settings.get('categories', [])

    def set_categories(self, category_list):
        self.settings['categories'] = category_list
        return self.save_settings()

    # 通用設定方法 (為了兼容 close_dialog_manager)
    def get_setting(self, key, default_value=None):
        return self.settings.get(key, default_value)

    def set_setting(self, key, value):
        self.settings[key] = value
        return self.save_settings()