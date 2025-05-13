from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from db_manager import DBManager
from main_password_widget import MainPasswordWidget

class PasswordManager(QMainWindow):
    # 密碼管理器主視窗設定
    def __init__(self):
        super().__init__()

        # 設置視窗圖標
        self.setWindowIcon(QIcon('password-manager.png'))

        # 設置視窗標題和大小
        self.setWindowTitle("密碼管理系統")
        self.setGeometry(100, 100, 400, 300)

        # 初始化數據庫管理器
        self.db_manager = DBManager()

        # 設置主密碼介面為中央元件
        self.main_password_widget = MainPasswordWidget(self)
        self.setCentralWidget(self.main_password_widget)

        # 視窗置中
        self.center_window()

    # 視窗置於螢幕中央設定
    def center_window(self):
        screen = self.screen().availableGeometry()
        
        size = self.geometry()
        
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        
        self.move(x, y)

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