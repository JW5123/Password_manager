class TrayStyleConfig:
    def __init__(self):
        # 亮色主題配置
        self.light_theme = {
            'background': '#ffffff',
            'border': '#e3e5e8',
            'text': '#2e3338',
            'hover_bg': '#5865f2',
            'hover_text': '#ffffff',
            'pressed_bg': '#4752c4',
            'separator': '#e3e5e8'
        }
        
        # 暗色主題配置
        self.dark_theme = {
            'background': '#2f3136',
            'border': '#202225',
            'text': '#dcddde',
            'hover_bg': '#5865f2',
            'hover_text': '#ffffff',
            'pressed_bg': '#4752c4',
            'separator': '#4f545c'
        }
    
    def get_style(self, is_dark_theme=False):
        """根據主題生成樣式"""
        theme = self.dark_theme if is_dark_theme else self.light_theme
        
        return f"""
            QMenu {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 6px 0px;
                color: {theme['text']};
                font-family: "Microsoft YaHei UI", "微軟雅黑", "Segoe UI", sans-serif;
                font-size: 14px;
            }}
            
            QMenu::item {{
                background-color: transparent;
                padding: 8px 16px;
                margin: 1px 6px;
                border-radius: 4px;
                min-width: 140px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme['hover_bg']};
                color: {theme['hover_text']};
            }}
            
            QMenu::item:pressed {{
                background-color: {theme['pressed_bg']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {theme['separator']};
                margin: 4px 12px;
            }}
        """