import sys
import os
from dotenv import load_dotenv

load_dotenv()

def resource_path(relative_path: str) -> str:
    # 回傳正確的資源路徑，支援打包後 (_MEIPASS) 或原始碼執行
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_user_settings_path():
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, ".password_manager")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir
    
def get_database_path():
    custom_path = os.getenv("PASSWORD_MANAGER_DB")
    if custom_path:
        return os.path.abspath(custom_path)
    return os.path.join(get_user_settings_path(), "passwords.db")

def get_settings_path():
    custom_settings = os.getenv("PASSWORD_MANAGER_SETTINGS")
    if custom_settings:
        return os.path.abspath(custom_settings)
    return os.path.join(get_user_settings_path(), "settings.json")