from PyQt6.QtGui import QPainter, QPixmap, QColor, QIcon, QAction, QPalette
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QLineEdit, QWidget
from utils.path_helper import resource_path
from typing import Optional

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

    def on_text_changed(self, text: str):
        """文字變化時的處理"""
        self.eye_action.setVisible(bool(text))  

    def toggle(self):
        """切換密碼顯示/隱藏狀態"""
        self.show_password = not self.show_password
        self.line_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self.show_password else QLineEdit.EchoMode.Password
        )
        self.update_icon()

    def update_icon(self):
        """更新圖標"""
        if self.show_password:
            icon = IconHelper.get_eye_show_icon(self.parent, QSize(20, 20))
        else:
            icon = IconHelper.get_eye_hide_icon(self.parent, QSize(20, 20))
        self.eye_action.setIcon(icon)


class IconHelper:
    @staticmethod
    def get_user_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取用戶圖標"""
        return SvgIconManager.create_icon("account.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_clear_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取清除圖標"""
        return SvgIconManager.create_icon("clear.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_search_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取搜索圖標"""
        return SvgIconManager.create_icon("search.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_add_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取添加圖標"""
        return SvgIconManager.create_icon("add.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_edit_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取編輯圖標"""
        return SvgIconManager.create_icon("edit.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_delete_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取刪除圖標"""
        return SvgIconManager.create_icon("delete.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_eye_show_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取顯示密碼圖標（眼睛開啟）"""
        return SvgIconManager.create_icon("show_eye.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_eye_hide_icon(widget: QWidget, size: QSize) -> QIcon:
        """獲取隱藏密碼圖標（眼睛關閉）"""
        return SvgIconManager.create_icon("hide_eye.svg", color=None, size=size, widget=widget)