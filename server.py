import socketserver 
import messages
from struct import *
import audio
from threading import Lock
import logging


# The only lock the whole thing needs.
connections_lock = Lock()
connections = {}

def composed_address(address_tuple):
    return address_tuple[0] + str(address_tuple)

class UplauseClientInstance(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.devices_to_listen_to = []
        self.channels_to_listen_to = [[]]
        self.params = {}
        self.params["reference"] = 1.0
        self.params["gain"] = 1.0
        self.params["a_weighting"] = True
        self.params["update_frequency"] = 5.0
        self.params["block_time"] = 0.1

        self.last_updated_to_client = 0.0

        self.configure_for_db = None

        self.close = False

        print("Connection from client: ", client_address)
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def handle(self):
        connections_lock.acquire()
        connections[composed_address(self.client_address)] = self
        connections_lock.release()
        self.data = bytes()

        data_remaining = False

        while self.close == False:
            if data_remaining == False:
                try:
                    self.data = self.request.recv(1024)
                except:
                    print("Error in connection. Likely it was terminated.")
                    self.close = True
                    break

            data_remaining = False

            if not self.data:
                print("Connection closed..")
                break

            msg_length = unpack('<I', self.data[:calcsize('<I')])[0]

            print (str(self.client_address[0]) + " wrote: ")
            print ("Message length: ", msg_length)
            print ("Data length: ", len(self.data))

            if len(self.data) >= msg_length:
                self.handle_msg(self.data)
                self.data = self.data[msg_length:]
                if len(self.data) > 4:
                    msg_length = unpack('<I', self.data[:calcsize('<I')])[0]
                    print("Msg length 2: ", msg_length)
                    if msg_length <= len(self.data):
                        data_remaining = True
            else:
                continue

    def finish(self):
        print ("Client closed connection.")
        connections_lock.acquire()
        del connections[composed_address(self.client_address)]
        connections_lock.release()
        self.close = True

    def get_param(self, name, default_value = 1.0):
        if name in self.params:
            return self.params[name]
        else:
            return default_value

    def set_param(self, name, value):
        if name in self.params:
            self.params[name] = value
        else:
            return

    def handle_msg(self, data):
        msg_length = unpack('<I', data[:calcsize('<I')])[0]
        msg_type = unpack('<I', data[calcsize('<I'):8])[0]

        print("Handling msg..")

        if msg_type == messages.MSG_GET_RMS:
            self.handle_get_rms(data)
        elif msg_type == messages.MSG_GET_DEVICES:
            self.handle_get_devices_list()
        elif msg_type == messages.MSG_SET_FLOAT_PARAM:
            self.handle_set_float_param(data)
        elif msg_type == messages.MSG_SET_BOOLEAN_PARAM:
            self.handle_set_boolean_param(data)
        elif msg_type == messages.MSG_CONFIGUREDB:
            self.handle_configure(data)

    def handle_get_rms(self, data):
        print("Handling get RMS message..")
        msg = messages.MsgStartStreamingRMS.deserialize(data)
        self.devices_to_listen_to = list(msg.devices)
        self.channels_to_listen_to = list(msg.channels)
        print("Devices to listen to: ", self.devices_to_listen_to)
        print("Channels to listen to: ", self.channels_to_listen_to)

    def handle_get_devices_list(self):
        print("Handling get devices message..")
        devices = audio.get_device_dict()
        devices_msg = messages.MsgDeviceList()
        devices_msg.devices = devices
        self.send_msg(devices_msg)

    def handle_set_float_param(self, data):
        print("Handling set float param message..")
        msg = messages.MsgSetFloatParam.deserialize(data)
        self.params[msg.param_name] = msg.param_value
        print("Param: ", msg.param_name, " value: ", msg.param_value)

    def handle_set_boolean_param(self, data):
        print("Handling set boolean param message..")
        msg = messages.MsgSetBooleanParam.deserialize(data)
        self.params[msg.param_name] = msg.param_value
        print("Param: ", msg.param_name, " value: ", msg.param_value)

    def handle_configure(self, data):
        print("Handling configuration command..")
        msg = messages.MsgConfiguredB.deserialize(data)
        self.configure_for_db = msg.target_db

    def send_msg(self, msg):
        try:
            self.request.send(msg.serialize())
        except:
            self.close = True
            print("Error in sending message. Likely connection was terminated.")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def start_server():
    HOST, PORT = "localhost", 50000

    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), UplauseClientInstance)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
