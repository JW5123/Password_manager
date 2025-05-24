import sys
import os

def resource_path(relative_path: str) -> str:
    # 回傳正確的資源路徑，支援打包後 (_MEIPASS) 或原始碼執行
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_user_settings_path():
    if os.name == 'nt':  # Windows
        home = os.path.expanduser("~")
        app_dir = os.path.join(home, ".password_manager")
        os.makedirs(app_dir, exist_ok=True)
        return app_dir
    else:  # Linux/macOS
        return os.path.join(os.path.expanduser("~/.password_manager"), "settings.json")
    
def get_database_path():
    return os.path.join(get_user_settings_path(), "passwords.db")

def get_settings_path():
    return os.path.join(get_user_settings_path(), "settings.json")