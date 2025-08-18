#!/usr/bin/env python
"""
測試自動登出功能的簡單腳本
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtCore import QTimer, QObject, pyqtSignal, QCoreApplication
from system.auto_logout_manager import AutoLogoutManager
from preferences.settings_manager import SettingsManager

class MockWindow(QObject):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        
class TestAutoLogout:
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        self.window = MockWindow()
        self.auto_logout_manager = AutoLogoutManager(self.window)
        self.auto_logout_manager.logout_requested.connect(self.on_logout)
        
        # 設定測試用的超時時間（1分鐘轉為測試用5秒）
        self.auto_logout_manager.logout_timeout = 5 / 60  # 5秒
        self.auto_logout_manager.is_enabled = True
        
        self.logout_triggered = False
        
    def on_logout(self):
        print("自動登出觸發!")
        self.logout_triggered = True
        self.app.quit()
        
    def test_basic_timeout(self):
        print("測試基本超時功能...")
        self.auto_logout_manager.start_monitoring()
        
        # 設定測試計時器
        test_timer = QTimer()
        test_timer.timeout.connect(lambda: self.check_test_result("基本超時測試"))
        test_timer.setSingleShot(True)
        test_timer.start(6000)  # 6秒後檢查結果
        
        self.app.exec()
        
    def test_reset_timer(self):
        print("測試重置計時器功能...")
        self.logout_triggered = False
        self.auto_logout_manager.start_monitoring()
        
        # 3秒後模擬用戶活動
        activity_timer = QTimer()
        activity_timer.timeout.connect(self.simulate_user_activity)
        activity_timer.setSingleShot(True)
        activity_timer.start(3000)
        
        # 8秒後檢查結果（應該還沒登出）
        test_timer = QTimer()
        test_timer.timeout.connect(lambda: self.check_test_result("重置計時器測試", should_logout=False))
        test_timer.setSingleShot(True)
        test_timer.start(8000)
        
        self.app.exec()
        
    def simulate_user_activity(self):
        print("模擬用戶活動 - 重置計時器")
        self.auto_logout_manager.reset_timer()
        
    def check_test_result(self, test_name, should_logout=True):
        if should_logout:
            if self.logout_triggered:
                print(f"✓ {test_name} 通過：自動登出正常觸發")
            else:
                print(f"✗ {test_name} 失敗：自動登出未觸發")
        else:
            if not self.logout_triggered:
                print(f"✓ {test_name} 通過：重置後未觸發登出")
            else:
                print(f"✗ {test_name} 失敗：不應該觸發登出")
        self.app.quit()

if __name__ == "__main__":
    # 測試1：基本超時功能
    print("=== 測試1：基本超時功能 ===")
    tester1 = TestAutoLogout()
    tester1.test_basic_timeout()
    
    print("\n=== 測試2：重置計時器功能 ===")
    # 測試2：重置計時器功能
    tester2 = TestAutoLogout()
    tester2.test_reset_timer()
