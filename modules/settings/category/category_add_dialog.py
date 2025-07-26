from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLineEdit, QLabel, QMessageBox)

class CategoryAddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增分類")
        self.setFixedSize(300, 150)
        self.category_name = ""
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()

        self.add_button = QPushButton("新增")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        
        # 連接按鈕事件
        self.add_button.clicked.connect(self.confirm_add)
        self.cancel_button.clicked.connect(self.reject)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 設置焦點到輸入框
        self.input_field.setFocus()
    
    def confirm_add(self):
        self.category_name = self.input_field.text().strip()
        if not self.category_name:
            QMessageBox.warning(self, "錯誤", "分類名稱不能為空白")
            return
        self.accept()
    
    def get_category_name(self):
        return self.category_name