class CategorySettings:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def get_categories(self):
        return self.settings_manager.settings.get('categories', [])

    def set_categories(self, categories):
        self.settings_manager.settings['categories'] = categories
        return self.settings_manager.save_settings()

    def is_valid_category_name(self, name):
        return bool(name and name.strip())

    def category_exists(self, name):
        return name in self.get_categories()

    def add_category(self, name):
        name = name.strip()
        if not self.is_valid_category_name(name):
            return False, "分類名稱不能為空白"
        if self.category_exists(name):
            return False, "分類名稱已存在"
        categories = self.get_categories() + [name]
        return (True, "分類新增成功") if self.set_categories(categories) else (False, "無法儲存分類設定")

    def remove_category(self, name):
        categories = self.get_categories()
        if name not in categories:
            return False, "分類不存在"
        categories.remove(name)
        return (True, "分類移除成功") if self.set_categories(categories) else (False, "無法儲存分類設定")

    def update_category(self, old, new):
        new = new.strip()
        if not self.is_valid_category_name(new):
            return False, "分類名稱不能為空白"
        if old == new:
            return True, "分類名稱未變更"
        categories = self.get_categories()
        if old not in categories:
            return False, "原分類不存在"
        if self.category_exists(new):
            return False, "分類名稱已存在"
        categories[categories.index(old)] = new
        return (True, "分類更新成功") if self.set_categories(categories) else (False, "無法儲存分類設定")

    def move_category(self, name, new_index):
        categories = self.get_categories()
        if name not in categories:
            return False, "分類不存在"
        if not (0 <= new_index < len(categories)):
            return False, "索引超出範圍"
        categories.insert(new_index, categories.pop(categories.index(name)))
        return (True, "分類位置更新成功") if self.set_categories(categories) else (False, "無法儲存分類設定")

    def get_category_count(self):
        return len(self.get_categories())

    def clear_all_categories(self):
        return (True, "所有分類已清空") if self.set_categories([]) else (False, "無法清空分類")

    def import_categories(self, category_list, merge=True):
        if not isinstance(category_list, list):
            return False, "匯入資料格式錯誤"
        valid = [c.strip() for c in category_list if self.is_valid_category_name(c)]
        if merge:
            categories = self.get_categories()
            categories += [c for c in valid if c not in categories]
        else:
            categories = valid
        return (True, f"成功匯入 {len(valid)} 個分類") if self.set_categories(categories) else (False, "無法儲存匯入的分類")

    def export_categories(self):
        return self.get_categories().copy()
