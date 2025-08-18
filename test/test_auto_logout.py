import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from system.auto_logout_manager import AutoLogoutManager
from preferences.settings_manager import SettingsManager

class MockWindow(QObject):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

@pytest.fixture
def auto_logout_manager(qtbot):
    window = MockWindow()
    manager = AutoLogoutManager(window)
    manager.logout_timeout = 5 / 60  # 5秒
    manager.is_enabled = True
    return manager

def test_basic_timeout(qtbot, auto_logout_manager):
    triggered = []
    def on_logout():
        triggered.append(True)
    auto_logout_manager.logout_requested.connect(on_logout)
    auto_logout_manager.start_monitoring()
    qtbot.wait(6000)  # 等待6秒
    assert triggered, "自動登出未觸發"

def test_reset_timer(qtbot, auto_logout_manager):
    triggered = []
    def on_logout():
        triggered.append(True)
    auto_logout_manager.logout_requested.connect(on_logout)
    auto_logout_manager.start_monitoring()
    # 3秒後重置計時器
    qtbot.wait(3000)
    auto_logout_manager.reset_timer()
    # 再等5秒（總共8秒）
    qtbot.wait(5000)
    assert not triggered, "重置後不應該觸發登出"
    # 再等2秒（總共10秒）
    qtbot.wait(2000)
    assert triggered, "重置後計時器應該觸發登出"
