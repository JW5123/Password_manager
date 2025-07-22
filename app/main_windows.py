from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QEvent

from Database.db_manager import DBManager
from app.main_password_widget import MainPasswordWidget
from preferences.settings_widget import SettingsManager
from system.auto_logout_manager import AutoLogoutManager
from utils.path_helper import resource_path

from system.system_tray_manager import SystemTrayManager
from system.close_dialog_manager import CloseDialogManager

# 密碼管理器主視窗設定
class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()

        # 設置視窗圖標
        self.setWindowIcon(QIcon(resource_path('icon/PasswordManager.ico')))

        # 設置視窗標題和大小
        self.setWindowTitle("密碼管理器")
        self.setGeometry(100, 100, 600, 500)

        # 初始化數據庫管理器
        self.db_manager = DBManager()

        # 初始化設定管理器
        self.settings_manager = SettingsManager()

        # 初始化自動登出管理器
        self.auto_logout_manager = AutoLogoutManager(self)
        self.auto_logout_manager.logout_requested.connect(self.handle_auto_logout)
        
        # 初始化系統托盤管理器
        self.tray_manager = SystemTrayManager(self)
        self.tray_manager.show_requested.connect(self.show_from_tray)
        self.tray_manager.quit_requested.connect(self.quit_from_tray)

        # 連接新的信號
        self.tray_manager.settings_requested.connect(self.open_settings_from_tray)
        # self.tray_manager.about_requested.connect(self.show_about_from_tray)
        
        self.close_dialog_manager = CloseDialogManager(self, self.settings_manager)
        
        # 套用已儲存的主題
        self.settings_manager.apply_theme(self)

        # 設置主密碼介面為中央元件
        self.main_password_widget = MainPasswordWidget(self)
        self.setCentralWidget(self.main_password_widget)

        # 在程式啟動時就顯示托盤圖標（如果可用）
        if self.tray_manager.is_tray_available():
            self.tray_manager.show_tray_icon()

        # 視窗置中
        self.center_window()

        QApplication.instance().installEventFilter(self)

    # 視窗置於螢幕中央設定
    def center_window(self):
        screen = self.screen().availableGeometry()
        
        size = self.geometry()
        
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        
        self.move(x, y)

    def handle_auto_logout(self):
        self.setMenuBar(None)

        # 返回主密碼輸入畫面
        self.main_password_widget = MainPasswordWidget(self)
        self.setCentralWidget(self.main_password_widget)
        
        # 停止監控
        self.auto_logout_manager.stop_monitoring()
    
    # 登入成功後開始監控
    def on_login_success(self):
        self.auto_logout_manager.update_settings()
        self.auto_logout_manager.start_monitoring()
        
        # 確保托盤圖標已顯示（如果可用且尚未顯示）
        if self.tray_manager.is_tray_available():
            if not self.tray_manager.tray_icon or not self.tray_manager.tray_icon.isVisible():
                self.tray_manager.show_tray_icon()
    
    # 軟體內有操作時調用此方法
    def on_user_activity(self):
        # print("Activity detected, timer reset")
        self.auto_logout_manager.reset_timer()
    
    # 設定更新時調用
    def on_settings_updated(self):
        self.auto_logout_manager.update_settings()

    # 事件過濾器：監控滑鼠移動、按鍵、滾輪等
    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.MouseMove, 
                            QEvent.Type.MouseButtonPress,
                            QEvent.Type.MouseButtonRelease, 
                            QEvent.Type.KeyPress, 
                            QEvent.Type.Wheel, 
                            QEvent.Type.FocusIn):
            self.on_user_activity()
        return super().eventFilter(obj, event)

    # 從托盤顯示主窗口
    def show_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    # 從托盤退出應用程式
    def quit_from_tray(self):
        # 直接退出，不顯示確認對話框
        self.tray_manager.hide_tray_icon()
        self.db_manager.close()
        QApplication.quit()
    
    # 最小化到托盤
    def minimize_to_tray(self):
        if self.tray_manager.is_tray_available():
            # 確保托盤圖標已顯示
            if not self.tray_manager.tray_icon or not self.tray_manager.tray_icon.isVisible():
                self.tray_manager.show_tray_icon()
            
            self.hide()
            # 顯示托盤通知
            # self.tray_manager.show_message(
            #     "密碼管理器", 
            #     "程式已最小化到系統托盤",
            #     timeout=3000
            # )
        else:
            # 如果托盤不可用，就正常最小化
            self.showMinimized()

    def open_settings_from_tray(self):
        # 先顯示主窗口
        self.show_from_tray()
        
        # 然後開啟設定頁面
        try:
            from preferences.settings_widget import SettingsWidget
            settings_widget = SettingsWidget(self)
            self.setCentralWidget(settings_widget)
        except Exception as e:
            print(f"無法開啟設定頁面: {e}")

    # 視窗關閉事件處理
    def closeEvent(self, event):
        # 檢查系統托盤是否可用
        tray_available = self.tray_manager.is_tray_available()
        
        close_action = self.close_dialog_manager.get_close_action(tray_available)
        
        # 根據動作決定行為
        if close_action == self.close_dialog_manager.CLOSE_TO_TRAY:
            # 最小化到托盤
            event.ignore()
            
            # 確保托盤圖標已創建並顯示
            if not self.tray_manager.show_tray_icon():
                # 如果托盤圖標顯示失敗，改為正常最小化
                self.showMinimized()
            else:
                self.minimize_to_tray()
                
        else:
            # 完全退出
            event.accept()
            if tray_available:
                self.tray_manager.hide_tray_icon()
            self.db_manager.close()

    # 重寫 changeEvent 以處理最小化事件
    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange:
            # 檢查設定是否為最小化到托盤
            if self.isMinimized():
                # 獲取當前關閉動作設定
                close_action = self.settings_manager.get_close_action()
                
                # 如果設定為托盤且托盤可用，則隱藏到托盤
                if (close_action == "tray" and 
                    self.tray_manager.is_tray_available()):
                    event.ignore()
                    self.hide()
                    return
        super().changeEvent(event)
