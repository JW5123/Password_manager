import json
import os
from qt_material import apply_stylesheet

# 設定管理
class SettingsManager:
    
    # 定義可用的主題
    THEMES = {
        "Dark Blue": 'dark_blue.xml', 
        "Dark Cyan": 'dark_cyan.xml', 
        "Dark Teal": 'dark_teal.xml', 
        "Light Blue": 'light_blue.xml', 
        "Light Cyan": 'light_cyan_500.xml'
    }
    
    def __init__(self):
        """初始化設定管理器"""
        self.settings = self.load_settings()
    
    def get_settings_path(self):
        """取得設定檔案路徑"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'settings.json')
    
    def load_settings(self):
        """從檔案載入設定"""
        settings_path = self.get_settings_path()
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入設定時發生錯誤: {str(e)}")
                return {'theme': 'Light Blue'}
        return {'theme': 'Light Blue'}
    
    def save_settings(self, settings):
        """儲存設定到檔案"""
        settings_path = self.get_settings_path()
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"儲存設定時發生錯誤: {str(e)}")
            return False
    
    def get_theme(self):
        """取得目前設定的主題名稱"""
        return self.settings.get('theme', 'Light Blue')
    
    def get_theme_file(self):
        """取得目前主題對應的檔案名稱"""
        theme_name = self.get_theme()
        return self.THEMES.get(theme_name, 'light_blue.xml')
    
    def apply_theme(self, widget):
        """套用目前的主題到指定的部件"""
        try:
            theme_file = self.get_theme_file()
            apply_stylesheet(widget, theme=theme_file)
            return True
        except Exception as e:
            print(f"套用主題時發生錯誤: {str(e)}")
            return False
    
    def set_theme(self, theme_name, widget=None):
        """設定主題並選擇性地套用到部件"""
        if theme_name in self.THEMES:
            self.settings['theme'] = theme_name
            if widget:
                try:
                    apply_stylesheet(widget, theme=self.THEMES[theme_name])
                except Exception as e:
                    print(f"套用主題時發生錯誤: {str(e)}")
                    return False
            return True
        return False