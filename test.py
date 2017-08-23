import messages
from struct import *
import socket
import threading, os, sys
import time
import configurator

host = 'localhost'
port = 50000
size = 1024

def create_connection() -> socket.socket:
    #Start client
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    return s

def send_float_conf(name, value, socket):
    msg = messages.MsgSetFloatParam()
    msg.param_name = name
    msg.param_value = value
    socket.send(msg.serialize())

def configure_db(value, socket):
    msg = messages.MsgConfigure()
    msg.target_db = value
    socket.send(msg.serialize())

def read_messages(name, socket):

    # Send device list request
    get_devices_msg = messages.MsgGetDevices()
    socket.send(get_devices_msg.serialize())

    #var = input("Please enter something: ")
    #print ("you entered", var)

    device = 0
    channel = [0]
    gain = 1.0
    a_weighting = True

    reference = 1.0
    if len(sys.argv) >= 3:
        device = int(sys.argv[1])
        channel = int(sys.argv[2])
        gain = float(sys.argv[3])
        reference = float(sys.argv[4])
        duration = float(sys.argv[5])
        a_weighting = sys.argv[6] == "True"

    # Send gain setup
    send_float_conf("gain", gain, socket)

    # Send reference setup
    send_float_conf("reference", reference, socket)

    # Send A Weighting setup
    send_float_conf("a_weighting", a_weighting, socket)

    # Send start streaming RMS for device 0, channel 0
    start_rms_msg = messages.MsgStartStreamingRMS()
    start_rms_msg.devices = [device]
    start_rms_msg.channels = [channel]
    socket.send(start_rms_msg.serialize())
    i = 10

    start_time = int(round(time.time() * 1000))
    last_msg_sent = start_time
    last_package_type = 1
    do_twice = 2

    #while int(round(time.time() * 1000)) - start_time < duration*1000:
    while True:
        data = socket.recv(size)

        msg_length = unpack('<I', data[:calcsize('<I')])[0]
        msg_type = unpack('<I', data[calcsize('<I'):8])[0]


        if int(round(time.time() * 1000)) - last_msg_sent > 250:
            last_msg_sent = int(round(time.time() * 1000))
            do_twice = 2
        #elif do_twice == 0:
        #    continue

        do_twice -= 1

        #print("Thread ", name, " Got msg, length: ", msg_length)
        #print("Thread ", name, " Got msg, type: ", msg_type)

        if msg_type == messages.MSG_LIST_DEVICES:
            devices_msg = messages.MsgDeviceList.deserialize(data)
            print("Thread ", name, " Devices: ", devices_msg.devices)
        elif msg_type == messages.MSG_DB_PACKET:
            db_msg = messages.MsgdBPacket.deserialize(data)
            print("Thread ", name, " dB: ", db_msg.value)
            global last_db
            last_db = db_msg.value
            configurator.current_db.set('{:.1f}'.format(db_msg.value))
        elif msg_type == messages.MSG_SET_FLOAT_PARAM:
            param_msg = messages.MsgSetFloatParam.deserialize(data)
            print("Thread ", name, " Got param: ", param_msg.param_name, ", with value: ", param_msg.param_value)
        """elif msg_type == messages.MSG_RMS_PACKET:
            rms_msg = messages.MsgRMSPacket.deserialize(data)
            print("Thread ", name, " RMS: ", rms_msg.value)"""

        time.sleep(0.0001)

    socket.close()

def test():
    sounda_socket = create_connection()
    t1 = threading.Thread(target=read_messages, daemon=True, args=("Test 1",sounda_socket,))
    t1.start()

    configurator.start(sounda_socket)

if __name__ == "__main__":
    test()