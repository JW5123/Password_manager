import json
import os
import sys
from qt_material import apply_stylesheet
from utils.path_helper import get_settings_path

class SettingsManager:
    THEMES = {
        "System": None,
        "Dark Blue": 'dark_blue.xml',
        "Light Blue": 'light_blue.xml'
    }

    def __init__(self):
        self.settings_path = get_settings_path()
        self.settings = self.load_settings()

    def detect_system_theme(self):
        try:
            # Windows 10/11
            if sys.platform == "win32":
                import winreg
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
                import subprocess
                try:
                    result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                        capture_output=True, text=True)
                    return "Dark Blue" if result.returncode == 0 and "Dark" in result.stdout else "Light Blue"
                except:
                    pass
            
            # Linux - GNOME/KDE 
            elif sys.platform.startswith("linux"):
                import subprocess
                
                # 首先嘗試檢測 KDE
                kde_theme = self._detect_kde_theme()
                if kde_theme:
                    return kde_theme
                
                # 如果 KDE 檢測失敗，嘗試 GNOME
                try:
                    result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                                        capture_output=True, text=True)
                    if result.returncode == 0:
                        theme = result.stdout.strip().lower()
                        if 'dark' in theme:
                            return "Dark Blue"
                        else:
                            return "Light Blue"
                except:
                    pass

        except Exception as e:
            print(f"檢測系統主題時發生錯誤: {e}")
        
        # 如果無法檢測，返回預設的淺色主題
        return "Light Blue"
    
    def _detect_kde_theme(self):
        """檢測 KDE 主題"""
        import subprocess
        
        # 嘗試多種 KDE 主題檢測方法
        methods = [
            # 方法1: 檢測 KDE 配色方案
            ['kreadconfig5', '--group', 'General', '--key', 'ColorScheme'],
            ['kreadconfig6', '--group', 'General', '--key', 'ColorScheme'],
            
            # 方法2: 檢測 Plasma 主題
            ['kreadconfig5', '--group', 'Theme', '--key', 'name'],
            ['kreadconfig6', '--group', 'Theme', '--key', 'name'],
            
            # 方法3: 檢測 Breeze 主題變體
            ['kreadconfig5', '--group', 'KDE', '--key', 'LookAndFeelPackage'],
            ['kreadconfig6', '--group', 'KDE', '--key', 'LookAndFeelPackage'],
        ]
        
        for method in methods:
            try:
                result = subprocess.run(method, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    output = result.stdout.strip().lower()
                    print(f"KDE 檢測方法 {' '.join(method)}: {output}")
                    
                    # 檢測深色主題關鍵字
                    dark_keywords = ['dark', 'breeze-dark', 'breezedark', 'plasma-dark', 'plasmadark']
                    if any(keyword in output for keyword in dark_keywords):
                        return "Dark Blue"
                    
                    # 檢測淺色主題關鍵字
                    light_keywords = ['light', 'breeze', 'plasma', 'default']
                    if any(keyword in output for keyword in light_keywords):
                        return "Light Blue"
                        
            except Exception as e:
                print(f"KDE 檢測方法 {' '.join(method)} 失敗: {e}")
                continue
        
        # 如果以上方法都失敗，嘗試檢測環境變數
        try:
            kde_session = os.environ.get('KDE_SESSION_VERSION')
            desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
            
            if kde_session or 'kde' in desktop_session or 'plasma' in desktop_session:
                print("檢測到 KDE 環境，但無法確定主題，使用預設淺色主題")
                return "Light Blue"
        except:
            pass
        
        return None

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
                        settings['theme'] = "System"  # 預設改為跟隨系統
                    if 'categories' not in settings:
                        settings['categories'] = []
                    return settings
            except Exception as e:
                print(f"載入設定錯誤 {e}")
        
        # 若不存在則建立預設設定
        default = {"theme": "System", "categories": []}  # 預設改為跟隨系統
        self.save_settings(default)
        return default

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