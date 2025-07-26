from dialogs.add_password import AddNameDialog
from dialogs.view_password import ViewPasswordDialog
from dialogs.password_operations import edit_password_entry, delete_password_entry
from utils.import_export_manager import ImportExportManager

class AccountListHandler:
    def __init__(self, ui_widget):
        self.ui = ui_widget
        self.parent = ui_widget.parent
        self.db_manager = self.parent.db_manager
        self.settings_manager = self.parent.settings_manager
        self.import_export_manager = ImportExportManager(self.parent, self.db_manager, self.settings_manager)
        self.connect_signals()

    def connect_signals(self):
        self.ui.search_box.textChanged.connect(self.filter_names)
        self.ui.clear_action.triggered.connect(self.ui.search_box.clear)
        self.ui.category_combo.currentTextChanged.connect(self.load_names_by_category)
        self.ui.add_button.clicked.connect(self.add_name)
        self.ui.name_list.itemDoubleClicked.connect(self.view_account_password)
        self.ui.name_list.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.name_list.model().rowsMoved.connect(self.update_order_in_database)
        self.ui.logout_action.triggered.connect(self.logout)
        self.ui.import_action.triggered.connect(self.import_from_file)
        self.ui.export_action.triggered.connect(self.export_to_csv)
        self.ui.settings_action.triggered.connect(self.open_settings)
        self.ui.about_action.triggered.connect(self.ui.show_about_dialog)

    def load_names(self):
        self.load_names_by_category(self.ui.category_combo.currentText())

    def load_names_by_category(self, category):
        self.ui.clear_list()
        names = self.db_manager.get_all_names() if category == "全部" else self.db_manager.get_names_by_category(category)
        for name in names:
            self.ui.add_list_item(name)

    def reload_categories(self):
        self.ui.update_category_combo(self.settings_manager.get_categories(), self.ui.category_combo.currentText())

    def filter_names(self):
        self.ui.filter_list_items(self.ui.search_box.text())

    def add_name(self):
        dialog = AddNameDialog(self.parent)
        if dialog.exec():
            self.db_manager.add_password_entry(dialog.name, dialog.account, dialog.password, dialog.notes, dialog.category)
            self.load_names_by_category(self.ui.category_combo.currentText())

    def view_account_password(self, item):
        name = item.text()
        account, password, notes, category = self.db_manager.get_password_entry(name)
        dialog = ViewPasswordDialog(self.parent, name, account, password, notes, category)
        dialog.password_updated.connect(self.load_names)
        dialog.exec()

    def show_context_menu(self, position):
        result = self.ui.create_context_menu(position)
        if not result:
            return
        context_menu, view_action, edit_action, delete_action, item = result
        view_action.triggered.connect(lambda: self.view_account_password(item))
        edit_action.triggered.connect(lambda: self.handle_edit(item))
        delete_action.triggered.connect(lambda: self.handle_delete(item))
        context_menu.exec(self.ui.name_list.mapToGlobal(position))

    def handle_edit(self, item):
        if edit_password_entry(self.parent, self.db_manager, item.text()):
            self.load_names()

    def handle_delete(self, item):
        if delete_password_entry(self.parent, self.db_manager, item.text()):
            self.load_names()

    def update_order_in_database(self):
        self.db_manager.update_order_indices(self.ui.get_item_order())

    def logout(self):
        if self.ui.show_logout_confirmation():
            self.parent.setMenuBar(None)
            from app.main_password_widget import MainPasswordWidget
            self.parent.setCentralWidget(MainPasswordWidget(self.parent))

    def import_from_file(self):
        self.import_export_manager.import_from_file()
        self.load_names()

    def export_to_csv(self):
        self.import_export_manager.export_to_csv()

    def export_filtered_data(self):
        self.import_export_manager.export_filtered_data(self.ui.category_combo.currentText())

    def open_settings(self):
        from preferences.settings_widget import SettingsWidget
        self.parent.setCentralWidget(SettingsWidget(self.parent))