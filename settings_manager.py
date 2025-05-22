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
    
    # 初始化設定管理器
    def __init__(self):
        self.settings = self.load_settings()
    
    # 取得設定檔案路徑
    def get_settings_path(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'settings.json')
    
    # 從檔案載入設定
    def load_settings(self):
        settings_path = self.get_settings_path()
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入設定時發生錯誤: {str(e)}")
                return {'theme': 'Light Blue'}
        return {'theme': 'Light Blue'}
    
    # 儲存設定到檔案
    def save_settings(self, settings):
        settings_path = self.get_settings_path()
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"儲存設定時發生錯誤: {str(e)}")
            return False
    
    # 取得目前設定的主題名稱
    def get_theme(self):
        return self.settings.get('theme', 'Light Blue')
    
    # 取得目前主題對應的檔案名稱
    def get_theme_file(self):
        theme_name = self.get_theme()
        return self.THEMES.get(theme_name, 'light_blue.xml')
    
    # 套用目前的主題到指定的部件
    def apply_theme(self, widget):
        try:
            theme_file = self.get_theme_file()
            apply_stylesheet(widget, theme=theme_file)
            return True
        except Exception as e:
            print(f"套用主題時發生錯誤: {str(e)}")
            return False
    
    # 設定主題並選擇性地套用到部件
    def set_theme(self, theme_name, widget=None):
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
    
    def get_categories(self):
        return self.settings.get('categories', [])

    def set_categories(self, category_list):
        self.settings['categories'] = category_list
