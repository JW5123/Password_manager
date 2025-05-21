import sqlite3
import os
import shutil
from password_encryption import encrypt_password, decrypt_password

class DBManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.master_password = None
        self.setup_connection()
        
    # 設置資料庫連接並初始化資料庫
    def setup_connection(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_path, 'passwords.db')

        # 資料庫不存在，複製初始資料庫
        if not os.path.exists(db_path):
            original_db_path = os.path.join(base_path, 'original_passwords.db')
            if os.path.exists(original_db_path):
                shutil.copy(original_db_path, db_path)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_db()
    
    # 設置資料庫表結構
    def setup_db(self):
        # 建立密碼存儲表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                            id INTEGER NOT NULL UNIQUE, 
                            name TEXT NOT NULL, 
                            account TEXT, 
                            password TEXT, 
                            notes TEXT,
                            order_index INTEGER)''')
        
        # 建立主密碼表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS master_password (
                            id INTEGER PRIMARY KEY, 
                            password TEXT NOT NULL,
                            salt BLOB NOT NULL)''')
        
        # 檢查是否需要添加 order_index 欄位
        self.cursor.execute("PRAGMA table_info(passwords)")
        columns = [column[1] for column in self.cursor.fetchall()]

        # 檢查是否需要添加 category 欄位
        self.cursor.execute("PRAGMA table_info(passwords)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'category' not in columns:
            self.cursor.execute("ALTER TABLE passwords ADD COLUMN category TEXT")

        
        if 'order_index' not in columns:
            self.cursor.execute("ALTER TABLE passwords ADD COLUMN order_index INTEGER")
            
            # 為現有記錄添加順序
            self.cursor.execute("SELECT rowid, name FROM passwords ORDER BY name ASC")
            rows = self.cursor.fetchall()
            for order_index, (rowid, name) in enumerate(rows):
                self.cursor.execute("UPDATE passwords SET order_index = ? WHERE rowid = ?", (order_index, rowid))
            
        self.conn.commit()
    
    # 檢查是否已設置主密碼
    def has_master_password(self):
        self.cursor.execute("SELECT * FROM master_password")
        return self.cursor.fetchone() is not None
    
    # 設置主密碼
    def set_master_password(self, hashed_password, salt):
        self.cursor.execute("INSERT INTO master_password (password, salt) VALUES (?, ?)", (hashed_password, salt))
        self.conn.commit()
    
    # 獲取主密碼
    def get_master_password(self):
        self.cursor.execute("SELECT password, salt FROM master_password")
        result = self.cursor.fetchone()
        if result:
            return result[0], result[1]
        return None, None
    
    # 更新主密碼
    def update_master_password(self, hashed_password, salt):
        self.cursor.execute("UPDATE master_password SET password = ?, salt = ? WHERE id = 1", (hashed_password, salt))
        self.conn.commit()
    
    # 設置當前登入的主密碼（用於加密/解密)
    def set_current_master_password(self, password):
        self.master_password = password
    
    # 獲取所有名稱
    def get_all_names(self):
        self.cursor.execute("SELECT name FROM passwords ORDER BY order_index ASC")
        return self.cursor.fetchall()
    
    def get_master_salt(self):
        self.cursor.execute("SELECT salt FROM master_password")
        result = self.cursor.fetchone()
        return result[0] if result else None

    # 獲取特定名稱的密碼條目
    def get_password_entry(self, name):
        self.cursor.execute("SELECT account, password, notes FROM passwords WHERE name = ?", (name,))
        entry = self.cursor.fetchone()
        
        if entry and self.master_password:
            encrypted_account, encrypted_password, encrypted_notes = entry
            salt = self.get_master_salt()
            # 解密所有欄位
            decrypted_account = decrypt_password(encrypted_account, self.master_password, salt)
            decrypted_password = decrypt_password(encrypted_password, self.master_password, salt)
            decrypted_notes = decrypt_password(encrypted_notes, self.master_password, salt)
            return (decrypted_account, decrypted_password, decrypted_notes)
        return entry
    
    # 添加新的密碼條目
    def add_password_entry(self, name, account, password, notes, category=None):
        # 加密所有欄位
        salt = self.get_master_salt()
        encrypted_account = encrypt_password(account, self.master_password, salt)
        encrypted_password = encrypt_password(password, self.master_password, salt)
        encrypted_notes = encrypt_password(notes, self.master_password, salt)

        self.cursor.execute("SELECT MAX(id) FROM passwords")
        max_id = self.cursor.fetchone()[0]
        new_id = (max_id + 1) if max_id is not None else 1

        self.cursor.execute("SELECT MAX(order_index) FROM passwords")
        max_order = self.cursor.fetchone()[0]
        new_order_index = (max_order + 1) if max_order is not None else 0

        self.cursor.execute("INSERT INTO passwords (id, name, account, password, notes, order_index, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (new_id, name, encrypted_account, encrypted_password, encrypted_notes, new_order_index, category))
        self.conn.commit()
    
    # 更新密碼條目
    def update_password_entry(self, old_name, new_name, account, password, notes, category=None):
        if self.master_password:
            salt = self.get_master_salt()
            encrypted_account = encrypt_password(account, self.master_password, salt)
            encrypted_password = encrypt_password(password, self.master_password, salt)
            encrypted_notes = encrypt_password(notes, self.master_password, salt)
        else:
            encrypted_account = account
            encrypted_password = password
            encrypted_notes = notes

        self.cursor.execute(
            "UPDATE passwords SET name = ?, account = ?, password = ?, notes = ?, category = ? WHERE name = ?",
            (new_name, encrypted_account, encrypted_password, encrypted_notes, category, old_name)
        )
        self.conn.commit()
    
    # 刪除密碼條目
    def delete_password_entry(self, name):
        self.cursor.execute("DELETE FROM passwords WHERE name = ?", (name,))
        self.conn.commit()
        self.reorder_password_ids()

    def reorder_password_ids(self):
        self.cursor.execute("SELECT rowid, name FROM passwords ORDER BY order_index ASC")
        rows = self.cursor.fetchall()
        for new_id, (rowid, name) in enumerate(rows, start=1):
            self.cursor.execute("UPDATE passwords SET id = ? WHERE rowid = ?", (new_id, rowid))
        self.conn.commit()
    
    # 更新多個條目的順序索引
    def update_order_indices(self, name_order_dict):
        for name, order_index in name_order_dict.items():
            self.cursor.execute("UPDATE passwords SET order_index = ? WHERE name = ?", (order_index, name))
        self.conn.commit()
    
    # 更新單個條目的順序索引
    def update_order_index(self, name, order_index):
        self.cursor.execute("UPDATE passwords SET order_index = ? WHERE name = ?", (order_index, name))
        self.conn.commit()
    
    # 獲取所有密碼條目
    def get_all_entries(self):
        self.cursor.execute("SELECT name, account, password, notes, category FROM passwords")
        entries = self.cursor.fetchall()
        
        # 如果有主密碼，解密所有密碼
        if self.master_password:
            salt = self.get_master_salt()
            decrypted_entries = []
            for name, encrypted_account, encrypted_password, encrypted_notes, category in entries:
                decrypted_account = decrypt_password(encrypted_account, self.master_password, salt)
                decrypted_password = decrypt_password(encrypted_password, self.master_password, salt)
                decrypted_notes = decrypt_password(encrypted_notes, self.master_password, salt)
                decrypted_entries.append((name, decrypted_account, decrypted_password, decrypted_notes, category))
            return decrypted_entries
        return entries
    
    def get_all_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM passwords WHERE category IS NOT NULL")
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def get_entries_by_category(self, category):
        if category == "全部":
            return self.get_all_entries()

        self.cursor.execute("SELECT name, account, password, notes FROM passwords WHERE category = ?", (category,))
        entries = self.cursor.fetchall()

        if self.master_password:
            salt = self.get_master_salt()
            decrypted_entries = []
            for name, encrypted_account, encrypted_password, encrypted_notes in entries:
                decrypted_account = decrypt_password(encrypted_account, self.master_password, salt)
                decrypted_password = decrypt_password(encrypted_password, self.master_password, salt)
                decrypted_notes = decrypt_password(encrypted_notes, self.master_password, salt)
                decrypted_entries.append((name, decrypted_account, decrypted_password, decrypted_notes, category))
            return decrypted_entries
        return entries
    
    def get_entry_category(self, name):
        self.cursor.execute("SELECT category FROM passwords WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    
    def close(self):
        if self.conn:
            self.conn.close()