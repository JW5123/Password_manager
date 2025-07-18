import json
import os
from qt_material import apply_stylesheet
from utils.path_helper import get_settings_path

class SettingsManager:
    THEMES = {
        "Dark Blue": 'dark_blue.xml',
        "Light Blue": 'light_blue.xml'
    }

    def __init__(self):
        self.settings_path = get_settings_path()
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入設定錯誤 {e}")
        
        # 若不存在則建立預設設定
        default = {"theme": "Light Blue", "categories": []}
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
        return self.settings.get('theme', 'Light Blue')

    def get_theme_file(self):
        return self.THEMES.get(self.get_theme(), 'light_blue.xml')

    def apply_theme(self, widget):
        try:
            apply_stylesheet(widget, theme=self.get_theme_file())
            return True
        except Exception as e:
            print(f"套用主題錯誤 {e}")
            return False

    def set_theme(self, theme_name, widget=None):
        if theme_name in self.THEMES:
            self.settings['theme'] = theme_name
            if widget:
                try:
                    apply_stylesheet(widget, theme=self.THEMES[theme_name])
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
