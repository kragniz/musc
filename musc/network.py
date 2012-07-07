import json
import socket
import mpg
import re
import musc

class Server(object):
    def __init__(self):
        self._mpg = mpg.Mpg()
        self.loadPlaylist('/home/louis/playlist')

        self._playmode = 'r'

    def doAction(self, args):
        '''Perform a server action based on the arguments given.'''
        if len(args) > 1:
            #we have a single command.
            command = args[1]
            if self._match('^p$|^pause$', command):
                self._mpg.pause()

            elif self._match('^r$|^random$|^rand$', command):
                self._playmode = 'r'
                return 'playing songs in a random order'

        else:
            #we have no arguments, so skip to the next song if a song is
            #playing
            self._mpg.next()

        return 'OK'

    def loadPlaylist(self, filename):
        '''Add a bunch of songs into the queue from a single file'''
        self._mpg.queue = open(filename).readlines()

    def _match(self, pattern, arg):
        '''Return True if the pattern can be matched in arg'''
        return re.findall(pattern, arg, flags=re.IGNORECASE) > 1

    def mode(self):
        return self._playmode

class Client(object):
    def __init__(self):
        self._sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
        self._port = musc.config.PORT
        self._host = musc.config.HOST

    def send(self, data):
        self._sock.connect(
                (self._host,
                 self._port)
            )

        self._sock.sendall(json.dumps({'args':data}))
        returnValue = self._sock.recv(1024)
        self._sock.close()
        return returnValue
