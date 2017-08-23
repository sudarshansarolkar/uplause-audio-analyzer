import socket
import struct
import requests
import time
import ntplib
import config

class BroadcasterHttpEcho(object):

    def __init__(self, address, port):
        self.address = config.broadcasters["http_echo"]["ip"]
        self.port = config.broadcasters["http_echo"]["port"]
        self.ntp_client = ntplib.NTPClient()

    def broadcast_db(self, db:float):
        #ntp_response = self.ntp_client.request('europe.pool.ntp.org', version=3)
        #print(ntp_response.tx_time)
        ntp_time = str(round(time.time() * 1000))
        data = {"dB":str(db), "ntp_time":ntp_time, "local_time":str(round(time.time() * 1000))}
        #data = {"dB":str(db)}

        try:
            requests.post(self.address + ":" + str(self.port) + "/db_data", data = data)
        except:
            pass
