from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

from modules.main import MainPasswordController
from utils.svg_icon_set import PasswordVisibilityController

class MainPasswordWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = parent.db_manager
        self.controller = MainPasswordController(self, self.db_manager)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.db_manager.has_master_password():
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("請輸入登入密碼")
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.pwd_input_visibility_controller = PasswordVisibilityController(self.password_input, self)
            self.password_input.returnPressed.connect(self.controller.verify_master_password)
            self.password_input.setFixedWidth(300)

            center_layout.addWidget(self.password_input, 0, Qt.AlignmentFlag.AlignCenter)
            center_layout.addSpacing(20)

            button_layout = QHBoxLayout()

            self.submit_button = QPushButton("登入")
            self.submit_button.clicked.connect(self.controller.verify_master_password)
            self.submit_button.setFixedWidth(100)

            self.reset_password_button = QPushButton("重設密碼")
            self.reset_password_button.clicked.connect(self.controller.reset_master_password)
            self.reset_password_button.setFixedWidth(100)

            button_layout.addWidget(self.submit_button)
            button_layout.addWidget(self.reset_password_button)

            center_layout.addLayout(button_layout)
            center_layout.setAlignment(button_layout, Qt.AlignmentFlag.AlignCenter)

        else:
            self.password_label = QLabel("尚未設定登入密碼")
            self.password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.set_password_button = QPushButton("設定登入密碼")
            self.set_password_button.clicked.connect(self.controller.set_master_password)
            self.set_password_button.setFixedWidth(150)

            center_layout.addWidget(self.password_label)
            center_layout.addSpacing(10)
            center_layout.addWidget(self.set_password_button, 0, Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch(1)
        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(30, 30, 30, 30)

    def reload_password_input_page(self):
        self.parent.setCentralWidget(MainPasswordWidget(self.parent))