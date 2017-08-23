#!/usr/bin/python

# open a microphone in pyAudio and listen for taps

import pyaudio
import struct
import math
import time
import server
import websocket_server
import analysis
import config
from messages import *
import numpy as np
from numpy import pi, polymul
from scipy.signal import bilinear
from scipy.signal import lfilter
from threading import Lock

py_audio = pyaudio.PyAudio()

FORMAT = pyaudio.paFloat32 
RATE = 44100
INPUT_BLOCK_TIME = 0.1
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)

streams = {}
stream_channels = {}

dbs_lock = Lock()
dbs = {}

def get_rms(block, gain, channels = [0, 1], channel_count = 2, a_weighting = True):

    block_as_np = analysis.decode(block, channel_count)

    b, a = analysis.A_weighting(RATE)
    block_weighted = lfilter(b, a, block_as_np)

    rms_sum = 0.0

    if a_weighting == True and config.audio["never_a_weight"] != True:
        data = block_weighted
        print("Weighting")
    else:
        data = block_as_np

    for channel in channels:
        rms_sum += (analysis.rms_flat(block_as_np[:, channel])) * gain

    if (len(channels) < 1):
        return 0.0

    return rms_sum/float(len(channels))

def get_db_from_rms(rms, reference_value) -> float:
    return 20.0 * math.log10(rms/(0.000002 * reference_value))

def configure_db(rms, target_db) -> float:
    reference = target_db/20.0
    reference = math.pow(10, reference)
    reference = rms/reference
    reference = reference/0.000002
    print("new reference value: " + str(reference))
    return reference

def __init__():
    #self.stream = self.open_mic_stream()
    pass

def stop():
    pass
    #self.stream.close()

# Finds a random mic channel to listen to. Testing purposes only.
def find_input_device():
    device_index = None

    for i in range( py_audio.get_device_count() ):     
        devinfo = py_audio.get_device_info_by_index(i)   
        print( "Device %d: %s"%(i,devinfo["name"]) )

        if py_audio.get_device_info_by_index(i).get('maxInputChannels')>0:
            print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
            device_index = i
            return device_index

    if device_index == None:
        print( "No preferred input found; using default input device." )

    return device_index

def get_device_dict() -> dict:
    # Key: device ID. Value: Device name
    devices = {}

    print("PortAudio version text: ", pyaudio.get_portaudio_version_text())
    print("Host API count: ", py_audio.get_host_api_count())

    print("Default host API info: ", py_audio.get_default_host_api_info())

    default_index = py_audio.get_default_host_api_info()["index"]

    for i in range(py_audio.get_default_host_api_info()["deviceCount"]):
        devinfo = py_audio.get_device_info_by_host_api_device_index(default_index, i)
        if py_audio.get_device_info_by_host_api_device_index(default_index, i).get('maxInputChannels')>0:
            print("Device with audio, index: ", i, " name: ", devinfo["name"], " channels: ", py_audio.get_device_info_by_host_api_device_index(default_index, i).get('maxInputChannels'))
            devices[i] = (devinfo["name"], py_audio.get_device_info_by_host_api_device_index(default_index, i).get('maxInputChannels'))

    return devices

def open_stream(device_id):
    default_api_index = py_audio.get_default_host_api_info()["index"]

    stream = py_audio.open(format = FORMAT,
                            channels = py_audio.get_device_info_by_index(device_id).get('maxInputChannels'),
                            rate = RATE,
                            input = True,
                            input_device_index = device_id,
                            frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

    global streams
    global stream_channels
    streams[str(device_id)] = stream
    stream_channels[str(device_id)] = py_audio.get_device_info_by_index(device_id).get('maxInputChannels')

def listen():
    print_db_count = 3

    while 1:
        stream_data = {}

        for device_id, stream in streams.items():
            try:
                stream_data[str(device_id)] = stream.read(INPUT_FRAMES_PER_BLOCK)
            except IOError as e:
                print("Error recording, ", str(e))
                return

        if len(stream_data) < 1:     
            time.sleep(0.001)

        sent_websocket_db = False

        server.connections_lock.acquire()
        for address, connection in sorted(server.connections.items()):
            for i in range(0, len(connection.devices_to_listen_to)):
                device_id = connection.devices_to_listen_to[i]

                if str(device_id) not in stream_data:
                    open_stream(device_id)
                else:

                    rms_packet = MsgRMSPacket()
                    amplitude = get_rms(block = stream_data[str(device_id)],
                        gain = connection.get_param("gain"),
                        channels = connection.channels_to_listen_to[i],
                        channel_count = stream_channels[str(device_id)],
                        a_weighting = connection.get_param("a_weighting"))
                    
                    if connection.configure_for_db != None:
                        new_reference = configure_db(amplitude, connection.configure_for_db)
                        connection.configure_for_db = None
                        connection.set_param("reference", new_reference)

                        ref_config_msg = MsgSetFloatParam()
                        ref_config_msg.param_name = "reference"
                        ref_config_msg.param_value = new_reference
                        connection.send_msg(ref_config_msg)

                    rms_packet.value = amplitude
                    connection.send_msg(rms_packet)

                    db_packet = MsgdBPacket()
                    db_packet.value = get_db_from_rms(amplitude, connection.get_param("reference"))
                    connection.send_msg(db_packet)

                    #print("ID for msg: " + str(db_packet.id))
                    if print_db_count == 3:
                        print("DB value: " + str(db_packet.value))
                        print_db_count = 0
                    else:
                        print_db_count += 1
                    #print("As bits! " + ''.join(bin(ord(chr(c))).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', db_packet.value)))

                    if not sent_websocket_db:
                        websocket_server.SimpleEcho.sendAll(db_packet.value)
                        sent_websocket_db = True

                    dbs_lock.acquire()
                    dbs[address] = db_packet.value
                    dbs_lock.release()

        server.connections_lock.release()
