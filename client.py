from PySide6.QtWidgets import QGridLayout,QDialog,QPushButton, QLabel,QTextEdit,QLineEdit
from PySide6.QtCore import Qt, Slot
import socket
from threading import Thread 
import threading
import re

MOD = 0.7 #константа масштаблирования, заголовка, формата декодирования и сообщение для отключения
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

class Window(QDialog):
    def __init__(self, ip, port, nick):
        super().__init__()
        self.ip=ip
        self.port=port
        self.nick = nick
        self.tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.tcpClientA.connect((ip, port))
        self.setStyleSheet("background-color: #20d1a6")
        self.chatTextField=QLineEdit()
        self.chatTextField.setStyleSheet("background-color: rgba(0,100,120,100);  font: bold 16px; color: white")
        self.btnSend=QPushButton("Send")
        self.btnSend.setStyleSheet("background-color: #F7CE16; font: bold 16px; color: black")
        self.chatBody=QGridLayout(self)
        self.battleshipGrid = QGridLayout()
        self.chat = QTextEdit()
        self.chat.setStyleSheet("background-color: rgba(0,100,120,100); color: white")
        self.chat.setReadOnly(True)
        self.chat.setFixedSize(600*MOD,400*MOD)
        font=self.chat.font()
        font.setPointSize(13)
        self.chat.setFont(font)
        self.chatBody.addWidget(self.chat, 0, 4, 1, 1)
        self.chatBody.addWidget(self.chatTextField, 3, 3, 2, 2)
        self.chatBody.addWidget(self.btnSend, 4, 4, 2, 2)
        self.setWindowTitle("Client Chat Application")
        self.buttons = [[0]*11 for i in range(11)]
        self.battleshipGrid.setRowMinimumHeight(0,5)
        self.battleshipGrid.setColumnMinimumWidth( 0, 5)
        for i in range(10):
            self.buttons[0][i] = QLabel(chr(i+97))
            self.buttons[0][i].setAlignment(Qt.AlignCenter)
            self.buttons[0][i].setFixedSize(20, 20)
            self.buttons[0][i].setStyleSheet("font: bold 13px; color: white")
            self.battleshipGrid.addWidget(self.buttons[0][i], 0, i+1)
            self.buttons[i][0] = QLabel(str(i))
            self.buttons[i][0].setAlignment(Qt.AlignCenter)
            self.buttons[i][0].setStyleSheet("font: bold 13px; color: white")
            self.battleshipGrid.addWidget(self.buttons[i][0], i+1, 0)
        for i in range(1,11):
            for j in range(1,11):
                self.buttons[i][j] = QPushButton()
                self.buttons[i][j].setStyleSheet("QPushButton { background-color: white; }")
                self.buttons[i][j].setFixedSize(30*MOD,30*MOD)
                self.battleshipGrid.addWidget(self.buttons[i][j], i, j)
        self.chatBody.addLayout(self.battleshipGrid, 0, 0)
        self.battleshipGrid.setVerticalSpacing(5)
        self.battleshipGrid.setHorizontalSpacing(5)
        self.btnSend.clicked.connect(self.send)
        self.gameScore = QTextEdit()
        self.gameScore.setReadOnly(True)
        self.gameScore.setStyleSheet("background-color: rgba(255,0,160,80); "\
             "border-style:outset;border-width: 1px;border-color: " "red;font: bold 14px;min-width: 8em;padding:\
                 6px;border-radius: 10px;color: white")
        self.gameScore.setFixedSize(300*MOD,100*MOD)
        self.chatBody.addWidget(self.gameScore, 4, 0)
        self.shipsLeft = QLabel()
        self.filler = QLabel()
        self.filler.setFixedSize(100*MOD,100*MOD)
        self.shipsLeft.setStyleSheet("font: bold 16px; color: white");
        self.chatBody.addWidget(self.filler, 3, 0)
        self.chatBody.addWidget(self.shipsLeft, 5, 0)
        self.resize(900*MOD, 600*MOD)
        self.gameScore.redoAvailable.connect(self.changeScore)
        self.gameScore.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gameScore.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gameScore.setFixedSize(200*MOD, 200*MOD)
        self.info = None 
        self.btnSend.setDisabled(1)
        self.btnDisc=QPushButton("Disconnect")
        self.btnDiscFont=self.btnDisc.font()
        self.btnDiscFont.setPointSize(15*MOD)
        self.btnDisc.setFont(self.btnDiscFont)
        self.btnDisc.setStyleSheet("background-color: yellow; color: blue")
        self.chatBody.addWidget(self.btnDisc, 5, 2)
        self.btnDisc.hide()
        self.btnDisc.clicked.connect(self.close)

    @Slot()                                                                  
    def changeScore(self):  #слот для изменения счета      
        if (self.info[3]):
            self.chat.append("/SERVER/: "+"Player " +'"'+self.info[0]+'"'+" made a hit on " + self.info[4])
            self.gameScore.setText(self.info[1])                                        
        else:
            self.chat.append("/SERVER/: "+"Player " +'"'+self.info[0]+'"'+" made a miss on " + self.info[4])
        self.shipsLeft.setText("Ships left: "+self.info[2])
        if (int(self.info[2]) == 0): #если игра окончена, парсим таблицу результатов, чтобы вывести победителя
            scoreDict = {}
            users = self.info[1].split("\n")
            print(users)
            best = 0
            for u in users:
                temp = u.split(": ")
                if (len(temp)>1):
                    scoreDict[temp[0]] = int(temp[1])
                    best = (best, int(temp[1]))[int(temp[1]) > best] 
            if (scoreDict[self.nick] >= best): #в зависимости от результата пользователя выводим сообщения 
                self.chatTextField.setText("Game over! You are a WINNER! Your score is: " + str(scoreDict[self.nick]))
                self.chatTextField.setStyleSheet("background-color: white; " "border-style:outset;border-width: 1px;border-color: "\
                     "green;font: bold 16px; min-width: 8em;padding: 6px;border-radius: 10px;color: green");
            else:
                self.chatTextField.setText("Game over! You LOSE! Your score is: " + str(scoreDict[self.nick]))
                self.chatTextField.setStyleSheet("background-color: white; " "border-style:outset;border-width: 1px;border-color: "\
                     "red;font: bold 16px; min-width: 8em;padding: 6px;border-radius: 10px;color: red");
            self.chatTextField.setDisabled(True)
            self.btnSend.hide()
            self.btnDisc.show()

    def send(self, *args):
        text=self.chatTextField.text()
        message = text
        if re.match(r"[a-jA-J][0-9]", text): #если сообщение совпало с регуляркой координаты, считаем это выстрелом, отправляем серверу
            message = ("!hit:"+text).encode(FORMAT)
            self.btnSend.setDisabled(1)
        if (args): #перегрузка для отправки ника при первом соеднинении с сервером
            message = ("!nick:"+args[0]).encode(FORMAT)
        else:
            self.chat.append("/me/: " + text) #иначе это просто сообщение серверу (общение)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        print(f'message cli = {message.decode(FORMAT)}, msg_len cli = {msg_length}, send_len cli = {send_length}')
        self.tcpClientA.send(send_length)
        self.tcpClientA.send(message)
        self.chatTextField.setText("")

    def redrawMap(self, i,j, res, info): #перерисовка карты боя в отдельном потоке
        print(f'i = {i},j = {j}, res = {res}')
        self.info = info.split("!") #разбиваем результат чьего-то выстрела, присланного сервером, на составные части
        self.info.append(res)
        self.info.append(chr(i+97).capitalize()+str(j)) #приводим к числовому виду
        if (res):
            self.buttons[i+1][j+1].setStyleSheet("QPushButton { background-color: red; }") 
            self.buttons[i+1][j+1].setText("V")
        else:
            self.buttons[i+1][j+1].setStyleSheet("QPushButton { background-color: yellow; }")
            self.buttons[i+1][j+1].setText("X")
        self.gameScore.redoAvailable.emit(True) #пуск сигнала для изменения счета из другого треда

class ClientThread(Thread): 
    def __init__(self, conn, ip,port,window): 
        Thread.__init__(self) 
        self.window=window
        self.ip = ip 
        self.port = port 
        self.conn = conn
        self.window.send(self.window.nick)
 
    def run(self): 
        connected = True
        while connected:
            msg_length = self.conn.recv(HEADER).decode(FORMAT) #классчиеские считываение сначала размера, затем тела сообщения
            if msg_length:
                print(f'recv len cli= {msg_length}') 
                msg_length = int(msg_length)
                msg = self.conn.recv(msg_length).decode(FORMAT)
                print(f'recv msg cli= {msg}')
                if msg == DISCONNECT_MESSAGE: #если сигнал на отключение - отключаемся
                    connected = False
                elif str(msg).startswith("!play"): #если это сигнал на разрешение хода, разблокируем кнопку и информируем клиента
                    self.window.btnSend.setEnabled(1)
                    self.window.nick = msg[6:]
                    self.window.chat.append("/SERVER/: "+"your turn! Write coordinate A0 to J9 to hit:")
                elif str(msg).startswith("!map"): #если это обновленная карта и таблица результатов, перерисовываем их в отдельном потоке
                    thread = threading.Thread(target=self.window.redrawMap, \
                    args=(int(msg[5:6]), int(msg[7:8]), int(msg[9:10]),msg[11:],))
                    thread.start()
                else:
                    self.window.chat.append("/SERVER/: "+msg) #иначе просто выводим как сообщение от сервера
        self.conn.close()