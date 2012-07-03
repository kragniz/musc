import json
import socket
from mpg import Mpg

class Client(object):
    def __init_(self, port=7785, host='localhost'):
        self._sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
        self._port = port
        self._host = host

    def send(self, data):
        self._sock.connect(
                self._host,
                self._port
            )

class Server(object):
    def __init__(self, mpgInstance=Mpg()):
        self.mpg = mpgInstance

    def doAction(self, args):
        print 'doing action based on', args
