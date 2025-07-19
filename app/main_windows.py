from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QEvent

from Database.db_manager import DBManager
from app.main_password_widget import MainPasswordWidget
from preferences.settings_widget import SettingsManager
from preferences.auto_logout_manager import AutoLogoutManager
from utils.path_helper import resource_path

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
        
        # 套用已儲存的主題
        self.settings_manager.apply_theme(self)

        # 設置主密碼介面為中央元件
        self.main_password_widget = MainPasswordWidget(self)
        self.setCentralWidget(self.main_password_widget)

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
        # 顯示自動登出訊息
        # QMessageBox.information(self, "自動登出", "由於長時間無操作，系統已自動登出。")
        
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


    # 視窗關閉確認對話框
    def closeEvent(self, event):
        reply = QMessageBox(self)
        reply.setWindowTitle('訊息')
        reply.setText('確定要退出嗎？')

        reply.setIcon(QMessageBox.Icon.Question)

        confirm_button = reply.addButton("確定", QMessageBox.ButtonRole.ActionRole)
        cancel_button = reply.addButton("取消", QMessageBox.ButtonRole.RejectRole)

        reply.exec()

        if reply.clickedButton() == confirm_button:
            event.accept()
            self.db_manager.close()
        else:
            event.ignore()