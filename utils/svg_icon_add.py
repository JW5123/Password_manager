from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget
from .svg_icon_set import SvgIconManager

class IconHelper:
    @staticmethod
    def get_user_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取用戶圖標
        return SvgIconManager.create_icon("account.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_clear_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取清除圖標
        return SvgIconManager.create_icon("clear.svg", color=None, size=size, widget=widget)

    @staticmethod
    def get_settings_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取設置圖標
        return SvgIconManager.create_icon("settings.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_import_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取匯入圖標
        return SvgIconManager.create_icon("import.svg", color=None, size=size, widget=widget)

    @staticmethod
    def get_export_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取匯出圖標
        return SvgIconManager.create_icon("export.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_logout_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取登出圖標
        return SvgIconManager.create_icon("logout.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_about_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取關於圖標
        return SvgIconManager.create_icon("about.svg", color=None, size=size, widget=widget)

    @staticmethod
    def get_add_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取添加圖標
        return SvgIconManager.create_icon("add.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_edit_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取編輯圖標
        return SvgIconManager.create_icon("edit.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_delete_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取刪除圖標
        return SvgIconManager.create_icon("delete.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_eye_show_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取顯示密碼圖標（眼睛開啟）
        return SvgIconManager.create_icon("show_eye.svg", color=None, size=size, widget=widget)
    
    @staticmethod
    def get_eye_hide_icon(widget: QWidget, size: QSize) -> QIcon:
        # 獲取隱藏密碼圖標（眼睛關閉）
        return SvgIconManager.create_icon("hide_eye.svg", color=None, size=size, widget=widget)