import base64
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 主程式密碼加密
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(entered_password, stored_hashed_password):
    # 驗證主程式密碼是否正確
    try:
        return bcrypt.checkpw(entered_password.encode(), stored_hashed_password.encode())
    except ValueError:
        return False

# 從主密碼生成對稱加密金鑰
def generate_key_from_password(master_password, salt):
    # 使用PBKDF2將主密碼轉換為一個適合Fernet的金鑰
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

# 使用主密碼加密用戶密碼
def encrypt_password(password, master_password, salt):
    if not password:  # 處理空密碼的情況
        return ""
    
    key = generate_key_from_password(master_password, salt)
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode())
    # 返回加密後的密碼(轉為字符串存儲)
    return base64.urlsafe_b64encode(encrypted_password).decode()

# 使用主密碼解密用戶密碼
def decrypt_password(encrypted_password, master_password, salt):
    if not encrypted_password:  # 處理空加密密碼的情況
        return ""
    
    try:
        key = generate_key_from_password(master_password, salt)
        cipher = Fernet(key)
        # 先將字符串轉回二進制格式
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
        decrypted_password = cipher.decrypt(encrypted_bytes).decode()
        return decrypted_password
    except Exception as e:
        # 解密失敗的情況
        return "Decryption failed"