#!/usr/bin/python3
'''
This is a test file to receive post requests and send responses for testing the job_manager script

It is largely taken from https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7 with a bunch
of modifications

'''


#import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = ""
hostPort = 24998

class MyServer(BaseHTTPRequestHandler):
    #This defines how the server responds to HEAD requests
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.wfile.write(bytes("worker", "utf-8"))

    # predefined responses to GET requests
    def do_GET(self):

        if self.path == "/status":
            self._set_response()
            self.wfile.write(bytes("OK", "utf-8"))
        else:
            self.wfile.write(bytes("Unrecognized request: %s" % self.path, "utf-8"))
            self.send_response(201)
#POST is for submitting data.
    def do_POST(self):
        if self.path == "/start":
            print( "incomming http: ", self.path )
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            print(post_data)
            self._set_response()
        else:
            self.send_response(201)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            print("Bad Post Request")
        #client.close()


myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
