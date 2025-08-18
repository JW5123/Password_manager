from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class SingleInstanceManager(QObject):
    show_window_requested = pyqtSignal()

    def __init__(self, app_name="PasswordManager"):
        super().__init__()
        self.app_name = app_name
        self.server = None

    # 檢查應用程式是否已經在運行
    def is_already_running(self):
        # 嘗試連接到現有服務器
        test_socket = QLocalSocket()
        test_socket.connectToServer(self.app_name)
        
        if test_socket.waitForConnected(200):
            # 找到現有實例，發送顯示訊號
            test_socket.write(b"show")
            # 減少寫入等待時間到 100ms
            test_socket.waitForBytesWritten(100)
            test_socket.disconnectFromServer()
            return True
        
        # 沒有現有實例，嘗試建立服務器
        self.server = QLocalServer()
        QLocalServer.removeServer(self.app_name)
        
        if self.server.listen(self.app_name):
            self.server.newConnection.connect(self.handle_new_connection)
            return False
        else:
            return False

    # 處理新的連接請求
    def handle_new_connection(self):
        client = self.server.nextPendingConnection()
        if client:
            if client.waitForReadyRead(500):
                data = client.readAll()
                if data == b"show":
                    # 立即發送信號
                    self.show_window_requested.emit()
            client.disconnectFromServer()

    # 清理資源
    def cleanup(self):
        if self.server:
            self.server.close()
            QLocalServer.removeServer(self.app_name)
            self.server = None