import random
import string
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSlider, QLineEdit, QCheckBox)
from PyQt6.QtCore import Qt

class PasswordGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("密碼生成器")
        self.setFixedSize(400, 300)
        self.generated_password = ""
        self.init_ui()
        self.generate_password()

    def init_ui(self):
        layout = QVBoxLayout()

        # 字符類型選擇區域
        char_type_layout = QVBoxLayout()
        char_type_label = QLabel("選擇字符類型:")
        char_type_layout.addWidget(char_type_label)

        # 字符類型按鈕區域
        button_layout = QHBoxLayout()
        
        self.lowercase_btn = QPushButton("a-z")
        self.lowercase_btn.setStyleSheet("text-transform: none;")
        self.lowercase_btn.setCheckable(True)
        self.lowercase_btn.setChecked(True)
        self.lowercase_btn.clicked.connect(self.generate_password)
        button_layout.addWidget(self.lowercase_btn)

        self.uppercase_btn = QPushButton("A-Z")
        self.uppercase_btn.setCheckable(True)
        self.uppercase_btn.setChecked(True)
        self.uppercase_btn.clicked.connect(self.generate_password)
        button_layout.addWidget(self.uppercase_btn)

        self.numbers_btn = QPushButton("0-9")
        self.numbers_btn.setCheckable(True)
        self.numbers_btn.setChecked(True)
        self.numbers_btn.clicked.connect(self.generate_password)
        button_layout.addWidget(self.numbers_btn)

        self.symbols_btn = QPushButton("#$%")
        self.symbols_btn.setCheckable(True)
        self.symbols_btn.setChecked(False)
        self.symbols_btn.clicked.connect(self.generate_password)
        button_layout.addWidget(self.symbols_btn)

        char_type_layout.addLayout(button_layout)
        layout.addLayout(char_type_layout)

        # 密碼長度控制區域
        length_layout = QVBoxLayout()
        length_label = QLabel("密碼長度:")
        length_layout.addWidget(length_label)

        # 滑桿和數值顯示
        slider_layout = QHBoxLayout()
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(6)
        self.length_slider.setMaximum(50)
        self.length_slider.setValue(12)
        self.length_slider.valueChanged.connect(self.on_length_changed)
        slider_layout.addWidget(self.length_slider)

        self.length_display = QLabel("12")
        self.length_display.setMinimumWidth(30)
        slider_layout.addWidget(self.length_display)

        length_layout.addLayout(slider_layout)
        layout.addLayout(length_layout)

        # 密碼顯示區域
        password_layout = QVBoxLayout()
        password_label = QLabel("生成的密碼:")
        password_layout.addWidget(password_label)

        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        password_layout.addWidget(self.password_display)

        # 重新生成按鈕
        self.regenerate_btn = QPushButton("重新生成")
        self.regenerate_btn.clicked.connect(self.generate_password)
        password_layout.addWidget(self.regenerate_btn)

        layout.addLayout(password_layout)

        # 底部按鈕區域
        bottom_layout = QHBoxLayout()
        
        self.confirm_btn = QPushButton("確認")
        self.confirm_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.confirm_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(self.cancel_btn)

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    # 滑桿數值改變時更新顯示並重新生成密碼
    def on_length_changed(self, value):
        self.length_display.setText(str(value))
        self.generate_password()

    # 根據選擇的條件生成密碼
    def generate_password(self):
        characters = ""
        
        if self.lowercase_btn.isChecked():
            characters += string.ascii_lowercase
        if self.uppercase_btn.isChecked():
            characters += string.ascii_uppercase
        if self.numbers_btn.isChecked():
            characters += string.digits
        if self.symbols_btn.isChecked():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not characters:
            # 如果沒有選擇任何字符類型，默認使用小寫字母
            characters = string.ascii_lowercase
            self.lowercase_btn.setChecked(True)

        length = self.length_slider.value()
        self.generated_password = ''.join(random.choice(characters) for _ in range(length))
        self.password_display.setText(self.generated_password)

    # 返回生成的密碼
    def get_password(self):
        return self.generated_password