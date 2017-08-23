import audio, threading, time
from time import sleep
from broadcaster_viz import BroadcasterViz
from broadcaster_uplause import BroadcasterUplause
from broadcaster_http_echo import BroadcasterHttpEcho
from broadcaster_tcp_client import BroadcasterTCPClient

BROADCAST_TARGET_TYPE_VIZ = 0
BROADCAST_TARGET_TYPE_UPLAUSE = 1
BROADCAST_TARGET_TYPE_HTTP_ECHO = 2
BROADCAST_TARGET_TYPE_TCP_CLIENT = 3

targets = []

def add_target(target_type, address = "", port = ""):
    global targets

    if target_type == BROADCAST_TARGET_TYPE_VIZ:
        targets.append(BroadcasterViz(BroadcasterViz.COMM_TYPE_UDP, address, port))
    elif target_type == BROADCAST_TARGET_TYPE_UPLAUSE:
        targets.append(BroadcasterUplause(address, port))
    elif target_type == BROADCAST_TARGET_TYPE_HTTP_ECHO:
        targets.append(BroadcasterHttpEcho(address, port))
    elif target_type == BROADCAST_TARGET_TYPE_TCP_CLIENT:
        targets.append(BroadcasterTCPClient(address, port))

def broadcast_dbs():
    dbs = {}

    audio.dbs_lock.acquire()
    dbs = audio.dbs.copy()
    audio.dbs_lock.release()

    for target in targets:
        for key,value in dbs.items():
            threading.Thread(target=target.broadcast_db, daemon=True, args=(value,)).start()
            #target.broadcast_db(value)

def broadcast_loop():
    start_time = int(round(time.time() * 1000))
    last_msg_sent = start_time

    while 1:
        if int(round(time.time() * 1000)) - last_msg_sent > 100:
            last_msg_sent = int(round(time.time() * 1000))
        else:
            sleep(0.05)
            continue

        broadcast_dbs()

def start():
    #add_target(BROADCAST_TARGET_TYPE_VIZ, "localhost", 6666)
    #add_target(BROADCAST_TARGET_TYPE_UPLAUSE, "http://188.165.141.154", 1337)
    add_target(BROADCAST_TARGET_TYPE_HTTP_ECHO)
    add_target(BROADCAST_TARGET_TYPE_TCP_CLIENT)
    broadcast_loop()