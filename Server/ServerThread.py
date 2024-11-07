# needs to do the following:
# 
# listen for connections
# recieve connections (prob 1 at a time)
# send messages to other threads (like download ep _ from season ___ or download season _____)
import socket, json, threading, time
import ThreadCommBus

color = "\033[36m"
colorReset = "\033[00m"

class CommandServer:
    def __init__(self, bus=ThreadCommBus.BUS, vb=False):
        self.enabled = True
        self._bus = bus
        self.header = "(SERVER): "
        self.verboose = vb # vb is short for verboose (you'd think I'd use the shorthand if I have to type it a lot, but nooooo)

    def startThread(self, id, port):
        self.thread = threading.Thread(target=self.main, args=(port,1))
        self.threadID = id
        self.header = f"Thread({id}) {self.header}"
        self.thread.start()
        return self.thread

    def Print(self, msg, verb = False):
        if verb and self.verboose:
            self._bus.PrintBus.put(f"(Verboose) {color}{self.header}{msg}{colorReset}")
        else:
            self._bus.PrintBus.put(f"{color}{self.header}{msg}{colorReset}")

    def main(self, port, connCount=1):
        self.port = port
        listener = socket.socket()
        listener.bind((socket.gethostname(), port))
        self.Print(F"Server opened at {socket.gethostname()} on port {port}")
        while self.enabled:
            listener.listen(connCount)
            if not self._bus.killBus.empty():
                self.Print("Kill code recieved", True)
                break
            conn, addr = listener.accept()
            with conn:
                connData = []
                self.Print(f"connected to by : {addr}")
                while True:
                    data = conn.recv(1024) # recieve information from the client
                    if not data: break  # if there isnt data, then break
                    connData.append(data)
                    self.Print("recieved a packet!", True)
                msgData = json.loads(str(b"".join(connData), "utf-8"))
                self.Print(f"Recieved :\n{json.dumps(msgData, indent=4)}", True)
                self._bus.servChannel.put(msgData)
                # print(f"{self.header}Recieved : \n{json.dumps(json.loads(b"".join(connData)), indent=4)}")
    
    def shutdownServ(self):
        if self._bus.killBus.empty():
            self._bus.killBus.put(1)
        self.Print("Server shutting down")
        self.enabled = False

        self.Print("Shutting down socket server", True)
        killSocket = socket.socket() # get a socket obj
        self.Print("Sending kill code", True)

        # connect to the socket server (this breaks the loop, and exits the listener.listen())
        killSocket.connect((socket.gethostname(), self.port)) 
        # needs a dictionary to actually close without crashing, womp womp
        msg={"0" : "0"} 
        
        # send the kill message
        killSocket.sendall(bytes(json.dumps(msg), "utf-8"))
        self.Print("Kill code sent", True)
        # close the socket
        killSocket.close()
        
        # flush the Queue, (hopefully before the CMD Proc thread gets to it)
        self._bus.servChannel.get()
        self.Print("Socket server shutdown, waiting on thread", True)
        self.thread.join()
        self.Print("Server shutdown")


            
def testing():
    print("Starting")
    _BUS = ThreadCommBus.BUS()
    serv = CommandServer(_BUS)
    thread = serv.startThread(1, 7777)
    print("Thread online!")
    time.sleep(20)
    while not _BUS.servChannel.empty():
        print(f"Recieved : {_BUS.servChannel.get()}")
    # print("Kill code sent")
    # _BUS.killBus.put(1)
    serv.shutdownServ()
    