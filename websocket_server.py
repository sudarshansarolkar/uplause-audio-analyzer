from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

server = None
connections = {}

def composed_address(address_tuple):
    return address_tuple[0] + str(address_tuple)

class SimpleEcho(WebSocket):

    def handleMessage(self):
        # echo message back to client

        print("Got a message: " + self.data)
        #self.sendMessage(str(value))

    def handleConnected(self):
        print("");
        print (self.address, 'connected')
        global connections
        connections[composed_address(self.address)] = self

    def handleClose(self):
        print (self.address, 'closed')
        print("");

    def sendAll(value):
        for address, connection in connections.items():
            connection.sendMessage(str(value))

def start():
    global server
    server = SimpleWebSocketServer('', 8123, SimpleEcho)
    server.serveforever()