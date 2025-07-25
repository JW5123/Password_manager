from modules.main import AccountListUI
from modules.main import AccountListHandler

class NameListWidget(AccountListUI):
    
    def __init__(self, parent):
        super().__init__(parent)

        self.handler = AccountListHandler(self)
        self.handler.reload_categories()
    
    def on_ui_ready(self):
        self.handler.load_names()

    def load_names(self):
        return self.handler.load_names()
    
    def reload_categories(self):
        return self.handler.reload_categories()
    
    def export_filtered_data(self):
        return self.handler.export_filtered_data()