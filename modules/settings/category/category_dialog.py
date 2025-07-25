from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QDialog,
    QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from .category_settings import CategorySettings
from .category_add_dialog import CategoryAddDialog

class CategoryDialog(QWidget):
    categories_changed = pyqtSignal(list)
    category_added = pyqtSignal(str)
    category_removed = pyqtSignal(str)

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.category_settings = CategorySettings(settings_manager)
        self.temp_categories = self.category_settings.get_categories().copy()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("新增分類")
        self.add_btn.clicked.connect(self.show_add_category_dialog)
        btn_layout.addWidget(self.add_btn)
        self.clear_btn = QPushButton("清空所有分類")
        self.clear_btn.clicked.connect(self.clear_all_categories)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.category_list = QListWidget()
        self.category_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.category_list.customContextMenuRequested.connect(self.show_context_menu)

        layout.addLayout(btn_layout)
        layout.addWidget(self.category_list)
        self.refresh_category_list()

    def refresh_category_list(self):
        self.category_list.clear()
        self.category_list.addItems(self.temp_categories)
        self.clear_btn.setEnabled(bool(self.temp_categories))

    def show_add_category_dialog(self):
        dialog = CategoryAddDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_category_name()
            if not name or name in self.temp_categories:
                QMessageBox.warning(self, "錯誤", "分類名稱無效或已存在")
                return
            self.temp_categories.append(name)
            self.refresh_category_list()
            self.category_added.emit(name)
            self.categories_changed.emit(self.temp_categories.copy())

    def show_context_menu(self, pos):
        item = self.category_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        delete_action = menu.addAction("刪除分類")
        if menu.exec(self.category_list.mapToGlobal(pos)) == delete_action:
            self.remove_category(item.text())

    def remove_category(self, name):
        if name in self.temp_categories:
            self.temp_categories.remove(name)
            self.refresh_category_list()
            self.category_removed.emit(name)
            self.categories_changed.emit(self.temp_categories.copy())

    def clear_all_categories(self):
        reply = QMessageBox(self)
        reply.setWindowTitle("確認清空")
        reply.setText("確定要清空所有分類嗎？\n此操作將移除所有現有分類。")
        reply.setIcon(QMessageBox.Icon.Question)
        
        yes_button = reply.addButton("是", QMessageBox.ButtonRole.YesRole)
        no_button = reply.addButton("否", QMessageBox.ButtonRole.NoRole)
        reply.setDefaultButton(no_button)
        
        reply.exec()
        
        if reply.clickedButton() == yes_button:
            self.temp_categories.clear()
            self.refresh_category_list()

            self.categories_changed.emit(self.temp_categories.copy())
            
            QMessageBox.information(self, "完成", "所有分類已清空")

    def get_temp_categories(self):
        return self.temp_categories.copy()

    def has_changes(self):
        return self.temp_categories != self.category_settings.get_categories()

    def apply_changes(self):
        return self.category_settings.set_categories(self.temp_categories)

    def reset_changes(self):
        self.temp_categories = self.category_settings.get_categories().copy()
        self.refresh_category_list()
        self.categories_changed.emit(self.temp_categories.copy())

    def get_category_count(self):
        return len(self.temp_categories)
