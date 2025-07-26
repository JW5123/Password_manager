import sys
import subprocess

def detect_system_theme():
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

    return "Light Blue"
