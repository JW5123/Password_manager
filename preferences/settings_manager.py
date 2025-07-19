import json
import os
import sys
import subprocess
import winreg
from qt_material import apply_stylesheet
from utils.path_helper import get_settings_path

class SettingsManager:
    THEMES = {
        "System": None,
        "Dark Blue": 'dark_blue.xml',
        "Light Blue": 'light_blue.xml'
    }

    # 自動登出時間設定
    AUTO_LOGOUT_OPTIONS = {
        "持續登入": 0,
        "5分": 5,
        "10分": 10,
        "20分": 20,
        "30分": 30
    }

    def __init__(self):
        self.settings_path = get_settings_path()
        self.settings = self.load_settings()

    def detect_system_theme(self):
        try:
            # Windows 10/11
            if sys.platform == "win32":
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    return "Light Blue" if value == 1 else "Dark Blue"
                except:
                    pass
            
            # macOS
            elif sys.platform == "darwin":
                try:
                    result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                        capture_output=True, text=True)
                    return "Dark Blue" if result.returncode == 0 and "Dark" in result.stdout else "Light Blue"
                except:
                    pass
            
            # Linux - GNOME/KDE 
            elif sys.platform == "linux":

                # KDE
                try:
                    result = subprocess.run(['kreadconfig5', '--group', 'General', '--key', 'ColorScheme'], 
                                        capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        theme = result.stdout.strip().lower()
                        return "Dark Blue" if 'dark' in theme else "Light Blue"
                except:
                    pass
                
                # GNOME
                try:
                    result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                                        capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        theme = result.stdout.strip().lower()
                        return "Dark Blue" if 'dark' in theme else "Light Blue"
                except:
                    pass

        except Exception as e:
            print(f"檢測系統主題時發生錯誤: {e}")
        
        # 如果無法檢測，返回預設的淺色主題
        return "Light Blue"

    def get_effective_theme(self, theme_name):
        if theme_name == "System":
            return self.detect_system_theme()
        return theme_name

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
                        settings['auto_logout_timeout'] = 0 # 0 means disabled
                    return settings
            except Exception as e:
                print(f"載入設定錯誤 {e}")
        
        # 若不存在則建立預設設定
        default = {"theme": "System", "categories": [], "auto_logout_timeout": 0}
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