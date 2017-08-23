#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
 
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        print("Got POST")

        length = int(self.headers['Content-Length'])
        post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        for k, v in post_data.items():
            print(k, v)

        self.wfile.write("ok".encode("utf-8"))

    def do_GET(self):
        print("Got GET")

        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
 
        # Send message back to client
        message = "ok"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return
 
def run():
  print('starting server...')
 
  # Server settings
  server_address = ('127.0.0.1', 10080)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()
 
 
run()