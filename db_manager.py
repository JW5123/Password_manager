import sqlite3
import os
import shutil
from password_encryption import encrypt_password, decrypt_password

class DBManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.master_password = None  # 存儲當前登入的主密碼
        self.setup_connection()
        
    def setup_connection(self):
        """設置資料庫連接並初始化資料庫"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_path, 'passwords.db')  # 改為統一檔名

        # 如果資料庫不存在，複製初始資料庫（若你有初始模板）
        if not os.path.exists(db_path):
            original_db_path = os.path.join(base_path, 'original_passwords.db')
            if os.path.exists(original_db_path):
                shutil.copy(original_db_path, db_path)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_db()
    
    def setup_db(self):
        """設置資料庫表結構"""
        # 建立密碼存儲表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                            id INTEGER PRIMARY KEY, 
                            name TEXT NOT NULL, 
                            account TEXT, 
                            password TEXT, 
                            notes TEXT,
                            order_index INTEGER)''')
        
        # 建立主密碼表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS master_password (
                            id INTEGER PRIMARY KEY, 
                            password TEXT NOT NULL)''')
        
        # 檢查是否需要添加 order_index 欄位
        self.cursor.execute("PRAGMA table_info(passwords)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'order_index' not in columns:
            self.cursor.execute("ALTER TABLE passwords ADD COLUMN order_index INTEGER")
            
            # 為現有記錄添加順序
            self.cursor.execute("SELECT rowid, name FROM passwords ORDER BY name ASC")
            rows = self.cursor.fetchall()
            for order_index, (rowid, name) in enumerate(rows):
                self.cursor.execute("UPDATE passwords SET order_index = ? WHERE rowid = ?", (order_index, rowid))
            
        self.conn.commit()
    
    def has_master_password(self):
        """檢查是否已設置主密碼"""
        self.cursor.execute("SELECT * FROM master_password")
        return self.cursor.fetchone() is not None
    
    def set_master_password(self, hashed_password):
        """設置主密碼"""
        self.cursor.execute("INSERT INTO master_password (password) VALUES (?)", (hashed_password,))
        self.conn.commit()
    
    def get_master_password(self):
        """獲取主密碼"""
        self.cursor.execute("SELECT password FROM master_password")
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def update_master_password(self, hashed_password):
        """更新主密碼"""
        self.cursor.execute("UPDATE master_password SET password = ? WHERE id = 1", (hashed_password,))
        self.conn.commit()
    
    def set_current_master_password(self, password):
        """設置當前登入的主密碼（用於加密/解密）"""
        self.master_password = password
    
    def get_all_names(self):
        """獲取所有名稱"""
        self.cursor.execute("SELECT name FROM passwords ORDER BY order_index ASC")
        return self.cursor.fetchall()
    
    def get_password_entry(self, name):
        """獲取特定名稱的密碼條目"""
        self.cursor.execute("SELECT account, password, notes FROM passwords WHERE name = ?", (name,))
        entry = self.cursor.fetchone()
        
        if entry and self.master_password:
            encrypted_account, encrypted_password, encrypted_notes = entry
            # 解密所有欄位
            decrypted_account = decrypt_password(encrypted_account, self.master_password)
            decrypted_password = decrypt_password(encrypted_password, self.master_password)
            decrypted_notes = decrypt_password(encrypted_notes, self.master_password)
            return (decrypted_account, decrypted_password, decrypted_notes)
        return entry
    
    def add_password_entry(self, name, account, password, notes):
        """添加新的密碼條目"""
        # 加密所有欄位
        if self.master_password:
            encrypted_account = encrypt_password(account, self.master_password)
            encrypted_password = encrypt_password(password, self.master_password)
            encrypted_notes = encrypt_password(notes, self.master_password)
        else:
            encrypted_account = account
            encrypted_password = password
            encrypted_notes = notes

        self.cursor.execute("SELECT MAX(order_index) FROM passwords")
        max_order = self.cursor.fetchone()[0]
        new_order_index = (max_order + 1) if max_order is not None else 0
        self.cursor.execute("INSERT INTO passwords (name, account, password, notes, order_index) VALUES (?, ?, ?, ?, ?)", 
                           (name, encrypted_account, encrypted_password, encrypted_notes, new_order_index))
        self.conn.commit()
    
    def update_password_entry(self, old_name, new_name, account, password, notes):
        """更新密碼條目"""
        # 加密所有欄位
        if self.master_password:
            encrypted_account = encrypt_password(account, self.master_password)
            encrypted_password = encrypt_password(password, self.master_password)
            encrypted_notes = encrypt_password(notes, self.master_password)
        else:
            encrypted_account = account
            encrypted_password = password
            encrypted_notes = notes

        self.cursor.execute("UPDATE passwords SET name = ?, account = ?, password = ?, notes = ? WHERE name = ?",
                           (new_name, encrypted_account, encrypted_password, encrypted_notes, old_name))
        self.conn.commit()
    
    def delete_password_entry(self, name):
        """刪除密碼條目"""
        self.cursor.execute("DELETE FROM passwords WHERE name = ?", (name,))
        self.conn.commit()
    
    def update_order_indices(self, name_order_dict):
        """更新多個條目的順序索引"""
        for name, order_index in name_order_dict.items():
            self.cursor.execute("UPDATE passwords SET order_index = ? WHERE name = ?", (order_index, name))
        self.conn.commit()
    
    def update_order_index(self, name, order_index):
        """更新單個條目的順序索引"""
        self.cursor.execute("UPDATE passwords SET order_index = ? WHERE name = ?", (order_index, name))
        self.conn.commit()
    
    def get_all_entries(self):
        """獲取所有密碼條目"""
        self.cursor.execute("SELECT name, account, password, notes FROM passwords")
        entries = self.cursor.fetchall()
        
        # 如果有主密碼，解密所有密碼
        if self.master_password:
            decrypted_entries = []
            for name, encrypted_account, encrypted_password, encrypted_notes in entries:
                decrypted_account = decrypt_password(encrypted_account, self.master_password)
                decrypted_password = decrypt_password(encrypted_password, self.master_password)
                decrypted_notes = decrypt_password(encrypted_notes, self.master_password)
                decrypted_entries.append((name, decrypted_account, decrypted_password, decrypted_notes))
            return decrypted_entries
        return entries
    
    def close(self):
        """關閉資料庫連接"""
        if self.conn:
            self.conn.close()