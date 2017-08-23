import socket
import struct
import requests
import time
import ntplib

class BroadcasterUplause(object):

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ntp_client = ntplib.NTPClient()

    def broadcast_db(self, db:float):
        ntp_response = self.ntp_client.request('europe.pool.ntp.org', version=3)
        print(ntp_response.tx_time)
        data = {"dB":str(db), "ntp_time":ntp_response.tx_time, "local_time":str(round(time.time() * 1000))}
        #data = {"dB":str(db)}

        requests.post(self.address + ":" + str(self.port) + "/db_data", data = data)
