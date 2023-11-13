
from PySide6.QtWidgets import QGridLayout,QDialog,QPushButton,QLabel,QTextEdit,QLineEdit
from PySide6.QtCore import Qt, Signal, Slot
import socket
from threading import Thread 
import threading
from queue import Queue

MOD = 0.7 #константа масштаблирования, заголовка, формата декодирования и сообщение для отключения
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

class Window(QDialog): 
    speak = Signal(str)
    def __init__(self, ip, port):
        super().__init__()
        self.ip=ip
        self.window = self
        self.port=port
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.tcpServer.bind((ip, port)) #создание серверного сокета
        self.setStyleSheet("background-color: #AA01F2")
        self.chatTextField=QLineEdit()
        self.chatTextField.setStyleSheet("background-color: rgba(0,100,120,100); font: bold 16px; color: white")
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
        self.setWindowTitle("Server Chat Application")
        self.buttons = [[0]*11 for i in range(11)]
        self.battleshipGrid.setRowMinimumHeight(0,5)
        self.battleshipGrid.setColumnMinimumWidth( 0, 5)
        for i in range(10):
            self.buttons[0][i] = QLabel(chr(i+97)) #создание заголовков со сдвигами по ascii
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
                self.buttons[i][j].clicked.connect(self.makeBattleship)
                self.buttons[i][j].setStyleSheet("QPushButton { background-color: white; }")
                self.buttons[i][j].setFixedSize(30*MOD,30*MOD)
                self.battleshipGrid.addWidget(self.buttons[i][j], i, j)
        self.chatBody.addLayout(self.battleshipGrid, 0, 0)
        self.battleshipGrid.setVerticalSpacing(5*MOD)
        self.battleshipGrid.setHorizontalSpacing(5*MOD)
        self.btnStartGame = QPushButton("Start Game!")
        self.btnStartGame.setStyleSheet("background-color: #F7CE16; font: bold 16px; color: black")
        self.activePlayersLbl = QLabel("Players joined: 0")
        self.activePlayersLbl.setStyleSheet("font: bold 16px; color: white");
        self.gameScore = QTextEdit()
        self.gameScore.setReadOnly(True)
        self.gameScore.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gameScore.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gameScore.setStyleSheet("background-color: rgba(255,0,160,80); "\
             "border-style:outset;border-width: 1px;border-color: " "red;font: bold 14px;min-width: 8em;padding:\
                 6px;border-radius: 10px;color: white")
        self.gameScore.setFixedSize(200*MOD, 200*MOD)
        self.chatBody.addWidget(self.btnStartGame, 2, 0)
        self.chatBody.addWidget(self.activePlayersLbl, 3, 0)
        self.chatBody.addWidget(self.gameScore, 5, 0)
        self.btnStartGame.clicked.connect(self.startGame)
        self.btnSend.clicked.connect(self.send)
        self.resize(900*MOD, 600*MOD)
        self.q = Queue() #потокобезапасная переменная для обмена между тредами
        self.conn = None
        self.conns = []
        self.nicks = []
        self.nicksDict = {}
        self.queue = 0 
        self.window.btnStartGame.setDisabled(1)
        self.scores = {} 
        self.gameScore.redoAvailable.connect(self.changeScore) #механизм сокет-слот для смены интерфейса из другого потока
        self.shipsLeft = 0                                                                       

    @Slot()                                                                  
    def changeScore(self):  #слот для изменения счета из другого треда                                          
        scores = ""
        for k,v in dict.items(self.scores):
            scores += k +": " + str(v) + "\n"
        self.gameScore.setText(scores)

    def makeBattleship(self): 
        if (self.sender().palette().button().color() == '#80c342'): #если цвет поля красный (стоит корабль) - меняем на белый и наоборот
            self.sender().setStyleSheet("QPushButton { background-color: white; }")
        else:
            self.sender().setStyleSheet("QPushButton { background-color: #80c342; }")

    def send(self, *args):
        text=self.chatTextField.text()
        if (len(args) == 2): #перегрузка для отправки команды на ход одному пользователю
            text = "!play:" + args[1]
        elif (len(args)>2): #перегрузка для отправки обновленной карты, счета и результата последнего выстрела
            text = "!map:"+str(args[0]) + ":" +str(args[1])+ ":" +str(args[2]) + ":" \
                 +str(args[3]) + "!" +str(args[4])+ "!" +str(self.shipsLeft)
        else:
            self.chat.append("/SERVER/: " + text) #иначе это просто сообщение от сервера
        message = text.encode(FORMAT)
        msg_length = len(message) #сначала посылаем разрмер сообщения, а только потом его тело
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        print(f'message ser = {message.decode(FORMAT)}, msg_len ser = {msg_length}, send_len ser = {send_length}')
        if (len(args) == 2): #посылка одному пользователю
            args[0].send(send_length)
            args[0].send(message)
        else:
            for c in self.conns: #широковещательная посылка
                c.send(send_length)
                c.send(message)
        self.chatTextField.setText("")

    def startGame(self):
        self.shipMap = [[0]*10 for i in range(10)] #перевод карты в матричный вид
        for i in range(1,11):
            for j in range(1,11):
                if self.buttons[i][j].palette().button().color() == '#80c342':
                    self.shipMap[i-1][j-1] = 1
                    self.shipsLeft+=1
        for i in range(0,10):
            print(" ".join(str(self.shipMap[i])))
        self.send(self.conns[self.queue], self.nicksDict[self.conns[self.queue]]) #отправка пользователю его нового никнейма, если он был изменен
        self.queue = (0, self.queue+1)[self.queue < len(self.conns)-1] #свдиг очереди на ход
        scores = ""
        for n in self.nicks: #инициализация счета пользователей
            self.scores[n] = 0
            scores += n +": 0\n"
        self.gameScore.setText(scores)
        

    def start_host(self):
        self.tcpServer.listen() #прослушивание новых поключений
        print("Multithreaded Python server : Waiting for connections from TCP clients...")
        while True:
            (conn, (ip,port)) = self.tcpServer.accept() #получение параметров нового поключения
            self.conn = conn
            self.conns.append(conn)
            newthread = ClientThread(conn, ip,port,self.window, self.q) #создание потока для получения сообщений от него
            newthread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

    def testHit(self, hit, nick): #проверка выстрела на попадание
        i = int(hit[1:])
        j = ord(hit[:1].lower())-97 #преобразование к числу
        if (self.shipMap[i][j]): #если было попадание
            self.shipMap[i][j] = 0
            self.buttons[i+1][j+1].setStyleSheet("QPushButton { background-color: red; }")
            self.buttons[i+1][j+1].setText("V")
            self.scores[nick] += 1
            self.gameScore.redoAvailable.emit(True) #пуск сигнала для изменения счета из другого треда
            scores = ""
            for k,v in dict.items(self.scores): #упаковка новой таблицы результатов для рассылки пользователям
                scores += k +": " + str(v) + "\n"
            self.shipsLeft-=1 
            self.send(i,j, 1, nick, scores)
            self.send(self.conns[self.queue], self.nicksDict[self.conns[self.queue]]) #передача хода новому пользователю
            self.queue = (0, self.queue+1)[self.queue < len(self.conns)-1] #ротация права хода
        else: #если не попал, все почти аналогично, только карта карсится другоими цветами и иное содержание посылки
            self.buttons[i+1][j+1].setStyleSheet("QPushButton { background-color: yellow; }")
            self.buttons[i+1][j+1].setText("X")
            scores = ""
            for k,v in dict.items(self.scores):
                scores += k +": " + str(v) + "\n"
            self.send(i,j, 0, nick, scores)
            self.send(self.conns[self.queue], self.nicksDict[self.conns[self.queue]])
            self.queue = (0, self.queue+1)[self.queue < len(self.conns)-1]
         

class ClientThread(Thread): 
    def __init__(self, conn, ip,port,window,q): 
        Thread.__init__(self) 
        self.window=window
        self.ip = ip 
        self.port = port 
        self.conn = conn
        self.q = q
        self.nick = None
        print("[+] New server socket thread started for " + ip + ":" + str(port))  
 
    def run(self): 
        print(f"[NEW CONNECTION] {self.ip}:{self.port} connected.")
        connected = True
        while connected:
            msg_length = self.conn.recv(HEADER).decode(FORMAT) #сначала получаем длину сообщения
            if msg_length:
                print(f'recv len ser = {msg_length}') 
                msg_length = int(msg_length)
                msg = self.conn.recv(msg_length).decode(FORMAT) #потом тело сообщения по размеру длины
                print(f'recv msg ser = {msg}')
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                elif str(msg).startswith("!hit"): #проверка попадания в отдельном треде
                    thread = threading.Thread(target=self.window.testHit, args=(msg[5:7],self.nick,))
                    thread.start()
                    self.window.chat.append("/"+self.nick+"/: "+"Hitted " + str(msg[5:7]).capitalize() + "!")
                elif str(msg).startswith("!nick"): #клиент посылает никнейм при первом соединении, 
                    self.nick = msg[6:]
                    while(self.nick in self.window.nicks): #во избежание одинаковых никнеймов принудительно меняем
                        self.nick += str(1)
                    self.window.nicks.append(self.nick)
                    self.window.nicksDict[self.conn] = self.nick #храним имена в словаре, ассоциировав с подключением
                    msg = "was connected by adress /" + self.ip + ":p" + str(self.port) +"/"
                    self.window.activePlayersLbl.setText("Players joined: " + str(len(self.window.conns)))
                    self.window.chat.append("/"+self.nick+"/: "+msg)
                    if (len(self.window.conns) > 1):
                        self.window.btnStartGame.setEnabled(1) #если более 1 подключения, можно начинать игру
                else:
                    self.window.chat.append("/"+self.nick+"/: "+msg)
        self.conn.close()
