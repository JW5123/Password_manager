from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from .system_settings import SystemSettings
from .theme_settings import ThemeSettings

class SystemDialog(QWidget):
    auto_logout_changed = pyqtSignal(float)
    close_action_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.system_settings = SystemSettings(settings_manager)
        self.theme_settings = ThemeSettings(settings_manager)
        self._load_temp_settings()
        self._init_ui()

    def _load_temp_settings(self):
        self.temp_auto_logout_time = self.system_settings.get_auto_logout_timeout()
        self.temp_close_action = self.system_settings.get_close_action()
        self.temp_theme = self.theme_settings.get_theme()

    def _init_ui(self):
        layout = QVBoxLayout()
        behavior_group = QFrame()
        behavior_group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        behavior_layout = QVBoxLayout()
        behavior_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        behavior_layout.addLayout(self._create_theme_layout())
        behavior_layout.addSpacing(20)
        behavior_layout.addLayout(self._create_auto_logout_layout())
        behavior_layout.addSpacing(20)
        behavior_layout.addLayout(self._create_close_action_layout())

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        self.setLayout(layout)

    def _create_theme_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(QLabel("主題:"))
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        self.theme_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        for theme in self.theme_settings.get_available_themes():
            self.theme_combo.addItem(theme)
        self.theme_combo.setCurrentText(self.temp_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)
        return layout

    def _create_auto_logout_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(QLabel("自動登出時間:"))
        self.auto_logout_combo = QComboBox()
        self.auto_logout_combo.setMinimumWidth(200)
        self.auto_logout_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        for text in self.system_settings.get_available_auto_logout_options():
            self.auto_logout_combo.addItem(text)
        self.set_current_auto_logout_display()
        self.auto_logout_combo.currentTextChanged.connect(self.on_auto_logout_time_changed)
        layout.addWidget(self.auto_logout_combo)
        return layout

    def _create_close_action_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(QLabel("關閉動作:"))
        self.close_action_combo = QComboBox()
        self.close_action_combo.setMinimumWidth(200)
        self.close_action_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        for text in self.system_settings.get_available_close_action_options():
            self.close_action_combo.addItem(text)
        self.set_current_close_action_display()
        self.close_action_combo.currentTextChanged.connect(self.on_close_action_changed)
        layout.addWidget(self.close_action_combo)
        return layout

    def on_theme_changed(self, theme_name):
        self.temp_theme = theme_name
        self.theme_changed.emit(theme_name)

    def set_current_auto_logout_display(self):
        text = self.system_settings.get_auto_logout_display_text(self.temp_auto_logout_time)
        idx = self.auto_logout_combo.findText(text)
        if idx >= 0:
            self.auto_logout_combo.setCurrentIndex(idx)

    def on_auto_logout_time_changed(self, display_text):
        self.temp_auto_logout_time = self.system_settings.get_auto_logout_value_from_text(display_text)
        self.auto_logout_changed.emit(self.temp_auto_logout_time)

    def set_current_close_action_display(self):
        text = self.system_settings.get_close_action_display_text(self.temp_close_action)
        idx = self.close_action_combo.findText(text)
        if idx >= 0:
            self.close_action_combo.setCurrentIndex(idx)

    def set_current_theme_display(self):
        idx = self.theme_combo.findText(self.temp_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

    def on_close_action_changed(self, display_text):
        self.temp_close_action = self.system_settings.get_close_action_value_from_text(display_text)
        self.close_action_changed.emit(self.temp_close_action)

    def get_temp_settings(self):
        return {
            'auto_logout_timeout': self.temp_auto_logout_time,
            'close_action': self.temp_close_action,
            'theme': self.temp_theme
        }

    def has_changes(self):
        return (
            self.temp_auto_logout_time != self.system_settings.get_auto_logout_timeout() or
            self.temp_close_action != self.system_settings.get_close_action() or
            self.temp_theme != self.theme_settings.get_theme()
        )

    def apply_changes(self):
        success = self.system_settings.set_system_settings(
            auto_logout_timeout=self.temp_auto_logout_time,
            close_action=self.temp_close_action
        )
        if self.temp_theme != self.theme_settings.get_theme():
            success = success and self.theme_settings.set_theme(self.temp_theme)
        return success

    def reset_changes(self):
        self._load_temp_settings()
        self.set_current_auto_logout_display()
        self.set_current_close_action_display()
        self.set_current_theme_display()
