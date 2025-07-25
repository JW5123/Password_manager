from qt_material import apply_stylesheet
from system.system_theme_detector import detect_system_theme
from preferences.constants import THEMES

class ThemeSettings:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.THEMES = THEMES
    
    def get_theme(self):
        return self.settings_manager.settings.get('theme', 'System')
    
    def get_effective_theme(self, theme_name=None):
        if theme_name is None:
            theme_name = self.get_theme()
        
        if theme_name == "System":
            return detect_system_theme()
        return theme_name
    
    def get_theme_file(self, theme_name=None):
        if theme_name is None:
            theme_name = self.get_theme()
        
        effective_theme = self.get_effective_theme(theme_name)
        return self.THEMES.get(effective_theme, 'light_blue.xml')
    
    def is_dark_theme(self, theme_name=None):
        if theme_name is None:
            theme_name = self.get_theme()
        
        effective_theme = self.get_effective_theme(theme_name)
        return effective_theme == "Dark Blue"
    
    def apply_theme(self, widget, theme_name=None):
        try:
            theme_file = self.get_theme_file(theme_name)
            apply_stylesheet(widget, theme=theme_file)
            return True
        except Exception as e:
            print(f"套用主題錯誤 {e}")
            return False
    
    def set_theme(self, theme_name, widget=None):
        if theme_name not in self.THEMES and theme_name != "System":
            print(f"無效的主題名稱: {theme_name}")
            return False
        
        # 更新設定
        self.settings_manager.settings['theme'] = theme_name
        
        # 如果提供了 widget，立即套用主題
        if widget:
            if not self.apply_theme(widget, theme_name):
                return False
        
        # 儲存設定
        return self.settings_manager.save_settings()
    
    def get_available_themes(self):
        themes = list(self.THEMES.keys())
        # 確保 System 主題在清單中
        if "System" not in themes:
            themes.insert(0, "System")
        return themes