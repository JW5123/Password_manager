from PyQt6.QtGui import QPainter, QPixmap, QColor, QIcon, QAction, QPalette
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QLineEdit, QWidget
from utils.path_helper import resource_path

class SvgIconManager:
    @staticmethod
    def create_icon(icon_name: str, size: QSize, color: str = None, widget: QWidget = None) -> QIcon:
        icon_path = resource_path(f"icon/{icon_name}")
        
        color = SvgIconManager.get_theme_color(widget)

        return SvgIconManager._colored_svg_icon(icon_path, color, size)
    
    @staticmethod  
    def get_theme_color(widget: QWidget) -> str:
        palette = widget.palette()
        bg_color = palette.color(QPalette.ColorRole.Window)
        is_dark = bg_color.lightness() < 128
        icon_color = "#ffffff" if is_dark else "#000000"
        
        return icon_color
    
    @staticmethod
    def _colored_svg_icon(svg_path: str, color: str, size: QSize) -> QIcon:
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            renderer.render(painter)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))
        finally:
            painter.end()

        return QIcon(pixmap)


class PasswordVisibilityController:
    def __init__(self, line_edit: QLineEdit, parent_widget: QWidget):
        self.line_edit = line_edit
        self.parent = parent_widget
        self.show_password = False
        self.eye_action = QAction(parent_widget)
        self.line_edit.addAction(self.eye_action, QLineEdit.ActionPosition.TrailingPosition)
        self.eye_action.triggered.connect(self.toggle)
        # 初始先隱藏 icon
        self.eye_action.setVisible(False)
        # 文字變動時顯示/隱藏 icon
        self.line_edit.textChanged.connect(self.on_text_changed)

        QTimer.singleShot(0, self.update_icon)

    # 文字變化時的處理
    def on_text_changed(self, text: str):
        self.eye_action.setVisible(bool(text))  

    # 切換密碼顯示/隱藏狀態
    def toggle(self):
        self.show_password = not self.show_password
        self.line_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self.show_password else QLineEdit.EchoMode.Password
        )
        self.update_icon()

    # 更新圖標
    def update_icon(self):
        from .svg_icon_add import IconHelper
        if self.show_password:
            icon = IconHelper.get_eye_show_icon(self.parent, QSize(20, 20))
        else:
            icon = IconHelper.get_eye_hide_icon(self.parent, QSize(20, 20))
        self.eye_action.setIcon(icon)