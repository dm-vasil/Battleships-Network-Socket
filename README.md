# Battleships-Network-Socket
**Distributed application of "Battleship" game type for local network in "client-server" architecture based on socket mechanism**

Description:

This program solves the problem of client communication through the server using the socket mechanism. The server waits for more than one user to connect to it, builds a map of ships and starts the game.
Users take turns writing coordinates of cells, those are checked by the server for hits and the results are sent broadcasting back to all clients. 
The battle map is dynamically rendered.
Live ships are counted. When their number is 0, the game ends and users are sent the game result and final score, after which they can disconnect from the server.

Choosing role:

![](images/Рисунок1.png)

Server configuration:

![](images/Рисунок2.png)

Server interface:

![](images/Рисунок3.png)

Player configuration:

![](images/Рисунок4.png)

Players connected to the game:

![](images/Рисунок5.png)

Dispaying messages in general chat:

![](images/Рисунок6.png)

The server puts ships on the battlefield:

![](images/Рисунок7.png)

Player made a miss:

![](images/Рисунок8.png)

Displaying players activity on the server side:

![](images/Рисунок9.png)

Player made a hit:

![](images/Рисунок10.png)

Game over as a winner:

![](images/Рисунок11.png)

Game over as a loser:

![](images/Рисунок12.png)
