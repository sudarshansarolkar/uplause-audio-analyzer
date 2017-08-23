import socket
import struct

class BroadcasterViz(object):
    COMM_TYPE_UDP = 0

    def __init__(self, comm_type, address, port):
        self.comm_type = comm_type
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def broadcast_db(self, db:float):
        message = "SharedMemoryMap_SetValue|uplause_db|" + str(db) + "\0"

        self.socket.sendto(message.encode('utf-8'), (self.address, self.port))