import sys
from PySide6.QtWidgets import QGridLayout,QDialog,QWidget, QPushButton, QApplication, QLabel,QLineEdit
from PySide6.QtCore import Qt
import socket
import server
import client
import threading

class startWindow(QDialog): #стартовое окно
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #AA01F2")
        self.startLabel=QLabel("Whom you wish to play?",self)
        self.startLabel.setAlignment(Qt.AlignCenter)
        self.startLabel.setFixedSize(300, 20)
        self.startLabel.setStyleSheet("font: bold 12px; color: yellow");
        self.btnClient=QPushButton("Client",self)
        self.btnClient.resize(480,30)
        self.btnServer=QPushButton("Server",self)
        self.btnServer.resize(480,30) 
        self.btnClient.setStyleSheet("background-color: rgba(200,255,0,255); \
            " "border-style:outset;border-width: 1px;border-color: " "red;font: 11px;min-width: \
                8em;padding: 6px;border-radius: 10px;");
        self.btnServer.setStyleSheet("background-color: rgba(200,255,0,255); \
            " "border-style:outset;border-width: 1px;border-color: " "red;font: 11px;min-width: \
                8em;padding: 6px;border-radius: 10px;");
        self.btnClient.clicked.connect(self.client_side)
        self.btnServer.clicked.connect(self.server_side)
        self.chatBody=QGridLayout(self)
        self.chatBody.addWidget(self.btnClient, 0, 0)
        self.chatBody.addWidget(self.btnServer, 1, 0)
        self.setWindowTitle("Chat Application")
        self.resize(300, 150)

    def server_side(self):
        newwindow = ServerWindow()
        window.hide()
        newwindow.exec()

    def client_side(self):
        newwindow = ClientWindow()
        window.hide()
        newwindow.exec()

class ClientWindow(QDialog): #окно настройки клиента
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #AA01F2")
        self.NickLabel=QLabel("Nickname",self)
        self.Nick=QLineEdit(self)
        self.Nick.setText("user")
        self.IpLabel=QLabel("Ip",self)
        self.Ip=QLineEdit(self)
        self.Ip.setText(socket.gethostbyname(socket.gethostname()))
        self.PortLabel=QLabel("Port",self)
        self.Port=QLineEdit(self)
        self.IpLabel.setStyleSheet("font: bold 12px; color: yellow");
        self.PortLabel.setStyleSheet("font: bold 12px; color: yellow");
        self.NickLabel.setStyleSheet("font: bold 12px; color: yellow");
        self.btnConnect=QPushButton("Connect",self)
        self.btnBack=QPushButton("<< Back",self)
        self.btnBack.setStyleSheet("background-color: rgba(200,255,0,255); \
            " "border-style:outset;border-width: 1px;border-color: " "red;font: 11px;min-width: \
                8em;padding: 6px;border-radius: 10px;");
        self.btnConnect.setStyleSheet("background-color: rgba(200,255,0,255); \
            " "border-style:outset;border-width: 1px;border-color: " "red;font: 11px;min-width: \
                8em;padding: 6px;border-radius: 10px;");
        self.Port.setStyleSheet("font: bold 15px; color: white");
        self.Ip.setStyleSheet("font: bold 15px; color: white");
        self.Nick.setStyleSheet("font: bold 15px; color: white");
        self.chatBody=QGridLayout(self)
        self.chatBody.addWidget(self.NickLabel, 0, 0)
        self.chatBody.addWidget(self.Nick, 1, 0)
        self.chatBody.addWidget(self.IpLabel, 2, 0)
        self.chatBody.addWidget(self.Ip, 3, 0)
        self.chatBody.addWidget(self.PortLabel, 4, 0)
        self.chatBody.addWidget(self.Port, 5, 0)
        self.chatBody.addWidget(self.btnConnect, 6, 0)
        self.chatBody.addWidget(self.btnBack, 7, 0)
        self.setWindowTitle("Client configuration")
        self.btnConnect.clicked.connect(self.start_client)
        self.btnBack.clicked.connect(self.return_back)
        self.resize(300, 150)

    def start_client(self): #инициализация клиента и создание треда для приема сообщений от сервера
        newwindow = client.Window(self.Ip.text(), int(self.Port.text()), self.Nick.text())
        clientThread=client.ClientThread(newwindow.tcpClientA, newwindow.ip,newwindow.port,newwindow)
        clientThread.start()
        self.hide()
        newwindow.exec()

    def return_back(self):
        window.show()
        self.hide()


class ServerWindow(QDialog): #окно настройки серверка
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #AA01F2")
        self.IpLabel=QLabel("Ip",self)
        self.IpLabel.setStyleSheet("font: bold 12px; color: yellow");
        self.Ip=QLineEdit(self)
        self.Ip.setText(socket.gethostbyname(socket.gethostname()))
        self.PortLabel=QLabel("Port",self)
        self.PortLabel.setStyleSheet("font: bold 12px; color: yellow");
        self.Port=QLineEdit(self)
        self.Port.setStyleSheet("font: bold 15px; color: white");
        self.Ip.setStyleSheet("font: bold 15px; color: white");
        self.btnHost=QPushButton("Host",self)
        self.btnBack=QPushButton("<< Back",self)
        self.btnBack.setStyleSheet("background-color: rgba(200,255,0,255); \
            " "border-style:outset;border-width: 1px;border-color: " "red;font: 11px;min-width: \
                8em;padding: 6px;border-radius: 10px;");
        self.btnHost.setStyleSheet("background-color: rgba(200,255,0,255); \
            " "border-style:outset;border-width: 1px;border-color: " "red;font: 11px;min-width: \
                8em;padding: 6px;border-radius: 10px;");
        self.chatBody=QGridLayout(self)
        self.chatBody.addWidget(self.IpLabel, 0, 0)
        self.chatBody.addWidget(self.Ip, 1, 0)
        self.chatBody.addWidget(self.PortLabel, 2, 0)
        self.chatBody.addWidget(self.Port, 3, 0)
        self.chatBody.addWidget(self.btnHost, 4, 0)
        self.chatBody.addWidget(self.btnBack, 5, 0)
        self.setWindowTitle("Server configuration")
        self.btnHost.clicked.connect(self.start_server)
        self.btnBack.clicked.connect(self.return_back)
        self.resize(300, 150)

    def start_server(self): #инициализация серверка и создание треда для приема новых поключений
        newwindow = server.Window(self.Ip.text(), int(self.Port.text()))
        thread = threading.Thread(target=newwindow.start_host)
        thread.start()
        self.hide()
        newwindow.exec()
        
    def return_back(self):
        window.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = startWindow()
    window.exec()
    sys.exit(app.exec_())
