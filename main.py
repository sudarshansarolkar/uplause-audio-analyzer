import threading, os, sys

import config

import audio
import server
import test
import broadcasting
import websocket_server

import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    with open(os.path.join(os.getcwd(), 'build_version_string'), 'r') as v_file:
        print (v_file.read())
except EnvironmentError:
    print("Couldn't open build_version_string. Perhaps it's missing?")

# python test.py 0 0 1.0 1.0 5 True
t = threading.Thread(target=server.start_server, daemon=True)
t.start()

t2 = threading.Thread(target=audio.listen, daemon=True)
t2.start()

t3 = threading.Thread(target=broadcasting.start, daemon=True)
t3.start()

#t4 = threading.Thread(target=test.test, daemon=True)
#t4.start()

t5 = threading.Thread(target=websocket_server.start, daemon=True)
t5.start()

while True:
    choice = input("Enter Q to quit, or press return to continue")
    if choice.lower() == "q":
        server.QUIT = True
        break
