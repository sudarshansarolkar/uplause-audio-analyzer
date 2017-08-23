import socket
import struct
import config

class BroadcasterTCPClient(object):

    def __init__(self, address, port):
        self.address = config.broadcasters["tcp_client"]["ip"]
        self.port = config.broadcasters["tcp_client"]["port"]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def broadcast_db(self, db:float):
        message = ""

        db_string = "{0:.2f}".format(db)

        if config.broadcasters["tcp_client"]["fixed_length_mode"] == True:
            if int(db) < 10:
                db_string = "0" + db_string
            if int(db) < 100:
                db_string = "0" + db_string

        message = db_string

        if config.broadcasters["tcp_client"]["single_value_mode"] != True:
            message = "A:" + db_string

        if "delimiter" in config.broadcasters["tcp_client"]:
            message = message + str(config.broadcasters["tcp_client"]["delimiter"])

        try:
            self.socket.sendall(bytes(message, config.broadcasters["tcp_client"]["encoding"]))
        except:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.address, self.port))
            except:
                pass