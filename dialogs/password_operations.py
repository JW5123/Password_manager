from PyQt6.QtWidgets import QMessageBox
from dialogs.edit_password import EditPasswordDialog

# 編輯資料
def edit_password_entry(parent, db_manager, name):
    account, password, notes, category = db_manager.get_password_entry(name)
    dialog = EditPasswordDialog(parent, name, account, password, notes, category)

    if dialog.exec():
        new_name = dialog.new_name
        new_account = dialog.new_account
        new_password = dialog.new_password
        new_notes = dialog.new_notes
        new_category = dialog.new_category

        db_manager.update_password_entry(name, new_name, new_account, new_password, new_notes, new_category)
        return new_name

    return None


# 刪除資料
def delete_password_entry(parent, db_manager, name):
    reply = QMessageBox(parent)
    reply.setWindowTitle('訊息')
    reply.setText(f'確定要刪除「{name}」嗎？')

    delete_button = reply.addButton("刪除", QMessageBox.ButtonRole.ActionRole)
    cancel_button = reply.addButton("取消", QMessageBox.ButtonRole.RejectRole)

    reply.exec()

    if reply.clickedButton() == delete_button:
        db_manager.delete_password_entry(name)
        return True
    return False
