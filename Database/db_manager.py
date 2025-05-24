import sqlite3
import os
from utils.password_encryption import encrypt_password, decrypt_password
from utils.path_helper import get_database_path

class DBManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.master_password = None
        self._cached_salt = None  # 緩存 salt 避免重複查詢
        self.setup_connection()
        
    # 設置資料庫連接並初始化資料庫
    def setup_connection(self):
        # 放在使用者家目錄的隱藏資料夾
        # base_path = os.path.dirname(os.path.abspath(__file__))
        db_path = get_database_path()

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_db()
    
    # 設置資料庫表結構
    def setup_db(self):
        # 建立主密碼表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS master_password (
                            id INTEGER PRIMARY KEY, 
                            password TEXT NOT NULL,
                            salt BLOB NOT NULL)''')
        # 建立密碼存儲表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                            id INTEGER NOT NULL UNIQUE, 
                            name TEXT NOT NULL, 
                            account TEXT, 
                            password TEXT, 
                            notes TEXT,
                            order_index INTEGER,
                            category TEXT)''')
        
        self.conn.commit()
    
    def has_master_password(self):
        self.cursor.execute("SELECT 1 FROM master_password LIMIT 1")
        return self.cursor.fetchone() is not None
    
    def set_master_password(self, hashed_password, salt):
        self.cursor.execute("INSERT INTO master_password (password, salt) VALUES (?, ?)", 
                            (hashed_password, salt))
        self.conn.commit()
        self._cached_salt = salt
    
    def get_master_password(self):
        self.cursor.execute("SELECT password, salt FROM master_password LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            self._cached_salt = result[1]
            return result[0], result[1]
        return None, None
    
    def update_master_password(self, hashed_password, salt):
        self.cursor.execute("UPDATE master_password SET password = ?, salt = ? WHERE id = 1", 
                            (hashed_password, salt))
        self.conn.commit()
        self._cached_salt = salt
    
    def set_current_master_password(self, password):
        self.master_password = password
        if self._cached_salt is None:
            self.get_master_password()
    
    def get_master_salt(self):
        if self._cached_salt is not None:
            return self._cached_salt
        
        self.cursor.execute("SELECT salt FROM master_password LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            self._cached_salt = result[0]
            return result[0]
        return None
    
    # 將資料庫撈出的條目列表批次解密
    def _decrypt_entry_rows(self, rows):
        decrypted_entries = []
        for name, account, password, notes, category in rows:
            decrypted_account, decrypted_password, decrypted_notes = self._decrypt_entry_fields(
                account, password, notes)
            decrypted_entries.append((name, decrypted_account, decrypted_password, decrypted_notes, category))
        return decrypted_entries

    
    # 統一的解密方法
    def _decrypt_entry_fields(self, encrypted_account, encrypted_password, encrypted_notes):
        if not self.master_password:
            return encrypted_account, encrypted_password, encrypted_notes
        
        salt = self.get_master_salt()
        if not salt:
            return encrypted_account, encrypted_password, encrypted_notes
        
        try:
            decrypted_account = decrypt_password(encrypted_account, self.master_password, salt)
            decrypted_password = decrypt_password(encrypted_password, self.master_password, salt)
            decrypted_notes = decrypt_password(encrypted_notes, self.master_password, salt)
            return decrypted_account, decrypted_password, decrypted_notes
        except Exception:
            return encrypted_account, encrypted_password, encrypted_notes
    
    # 統一的加密方法
    def _encrypt_entry_fields(self, account, password, notes):
        if not self.master_password:
            return account, password, notes
        
        salt = self.get_master_salt()
        if not salt:
            return account, password, notes
        
        encrypted_account = encrypt_password(account, self.master_password, salt)
        encrypted_password = encrypt_password(password, self.master_password, salt)
        encrypted_notes = encrypt_password(notes, self.master_password, salt)
        return encrypted_account, encrypted_password, encrypted_notes
    
    def get_all_names(self):
        self.cursor.execute("SELECT name FROM passwords ORDER BY order_index ASC")
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_password_entry(self, name):
        self.cursor.execute("SELECT account, password, notes, category FROM passwords WHERE name = ?", (name,))
        entry = self.cursor.fetchone()
        
        if not entry:
            return None
        
        encrypted_account, encrypted_password, encrypted_notes, category = entry
        decrypted_account, decrypted_password, decrypted_notes = self._decrypt_entry_fields(
            encrypted_account, encrypted_password, encrypted_notes)
        
        return (decrypted_account, decrypted_password, decrypted_notes, category)
    
    # 獲取所有密碼條目，按順序排列
    def get_all_entries(self):
        self.cursor.execute("SELECT name, account, password, notes, category FROM passwords ORDER BY order_index ASC")
        rows = self.cursor.fetchall()
        return self._decrypt_entry_rows(rows) if self.master_password else rows
    
    def get_entries_by_category(self, category):
        if category == "全部" or not category:
            return self.get_all_entries()
        
        self.cursor.execute("""SELECT name, account, password, notes, category FROM passwords WHERE category = ? ORDER BY order_index ASC""", 
                            (category,))
        rows = self.cursor.fetchall()
        return self._decrypt_entry_rows(rows) if self.master_password else rows

    # 獲取所有不為空的分類
    def get_all_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM passwords WHERE category IS NOT NULL AND category != ''")
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_entry_category(self, name):
        self.cursor.execute("SELECT category FROM passwords WHERE name = ? LIMIT 1", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def add_password_entry(self, name, account, password, notes, category=None):
        encrypted_account, encrypted_password, encrypted_notes = self._encrypt_entry_fields(account, password, notes)
        
        # 獲取新的 ID 和順序索引
        self.cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM passwords")
        new_id = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COALESCE(MAX(order_index), -1) + 1 FROM passwords")
        new_order_index = self.cursor.fetchone()[0]
        
        self.cursor.execute("""INSERT INTO passwords (id, name, account, password, notes, order_index, category) VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                            (new_id, name, encrypted_account, encrypted_password, encrypted_notes, new_order_index, category))
        self.conn.commit()
    
    def update_password_entry(self, old_name, new_name, account, password, notes, category=None):
        encrypted_account, encrypted_password, encrypted_notes = self._encrypt_entry_fields(
            account, password, notes)
        
        self.cursor.execute("""UPDATE passwords SET name = ?, account = ?, password = ?, notes = ?, category = ? WHERE name = ?""", 
                            (new_name, encrypted_account, encrypted_password, encrypted_notes, category, old_name))
        self.conn.commit()
    
    def delete_password_entry(self, name):
        self.cursor.execute("DELETE FROM passwords WHERE name = ?", (name,))
        self.conn.commit()
        self.reorder_password_ids()
    
    # 重新排序 ID
    def reorder_password_ids(self):
        self.cursor.execute("SELECT rowid, name FROM passwords ORDER BY order_index ASC")
        rows = self.cursor.fetchall()
        for new_id, (rowid, name) in enumerate(rows, start=1):
            self.cursor.execute("UPDATE passwords SET id = ? WHERE rowid = ?", (new_id, rowid))
        self.conn.commit()
    
    # 批次更新順序索引
    def update_order_indices(self, name_order_dict):
        for name, order_index in name_order_dict.items():
            self.cursor.execute("UPDATE passwords SET order_index = ? WHERE name = ?", 
                                (order_index, name))
        self.conn.commit()
    
    # 更新單個條目的順序索引
    def update_order_index(self, name, order_index):
        self.cursor.execute("UPDATE passwords SET order_index = ? WHERE name = ?", 
                            (order_index, name))
        self.conn.commit()

    # 根據分類回傳名稱清單
    def get_names_by_category(self, category):
        if category == "全部" or not category:
            self.cursor.execute("SELECT name FROM passwords ORDER BY order_index ASC")
        else:
            self.cursor.execute("SELECT name FROM passwords WHERE category = ? ORDER BY order_index ASC", (category,))
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        if self.conn:
            self.conn.close()