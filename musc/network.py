import json
import socket
import mpg
import re
import musc
from mutagen import File
import threading
import time
from scrobble import Scrobbler
import sys

class Server(object):

    def doAction(self, args):
        '''Perform a server action based on the arguments given.'''
        if len(args) > 1:
            #we have a single command.
            command = args[1]
            if self._match('^p$|^pause$', command):
                self._mpg.pause()

            elif self._match('^r$|^random$|^rand$', command):
                self._mpg.shuffle()
                return 'playing songs in a random order'

            elif command == 'quit':
                print 'quitting'
                sys.exit()
        else:
            #we have no arguments, so skip to the next song if a song is
            #playing
            self.nextTrack()
        return 'OK'


    class ManageQueue(threading.Thread):
        '''Handle playing a song after the current one has finished'''
        def __init__(self, mpg, timeToQuit):
            super(Server.ManageQueue, self).__init__()
            self._mpg = mpg
            self._scrobbler = Scrobbler()
            self.scrobbled = False
            self._timeToQuit = timeToQuit
            self._skippedTrack = False

        def skippedTrack(self):
            self._skippedTrack = True

        def markAsPlaying(self):
            metadata = Server.Metadata(self._mpg.filename)
            self._scrobbler.nowPlaying(metadata.artist,
                                       metadata.title,
                                       metadata.album)
            self._skippedTrack = False

        def run(self):
            while not self._timeToQuit.isTime:
                if self._mpg.timeToScrobble and not self.scrobbled:
                    print 'scrobbling this track!'
                    metadata = Server.Metadata(self._mpg.filename)
                    self._scrobbler.scrobble(metadata.artist,
                                             metadata.title,
                                             metadata.album)
                    self.scrobbled = True

                if not self._mpg.playing:
                    self._mpg.next()
                    print '....next'
                    self.markAsPlaying()
                    self.scrobbled = False

                if self._skippedTrack:
                    self.markAsPlaying()

                time.sleep(0.1)

    class Metadata(object):
        '''Get the metadata for a file.
        Data you probably need:
            artist
            title
            album
            tracknumber
            date'''
        def __init__(self, filename):
            self._audio = File(filename, easy=True)
            for k, v in self._audio.iteritems():
                # drop any unicode character we can't decode into ascii so md5
                # works (because md5 uses bytes, not characters)
                self._audio[k] = v[0].encode('ascii', 'ignore')

        def __getattr__(self, name):
            return self._audio[name][0]

    def __init__(self):
        self._mpg = mpg.Mpg()
        self.loadPlaylist('/home/louis/playlist')
        self._mpg.shuffle()
        
        self.timeToQuit = TimeToQuit()

        self._queueThread = self.ManageQueue(self._mpg, self.timeToQuit)
        self._queueThread.start()

    def nextTrack(self):
        '''Skip to the next track on the current playlist'''
        self._mpg.next()
        self._queueThread.skippedTrack()
        
    def quit(self):
        '''Kill everything in a nice way'''
        self.timeToQuit.isTime = True
        self._mpg.quit()

    def loadPlaylist(self, filename):
        '''Add a bunch of songs into the queue from a single file'''
        self._mpg.queue = open(filename).readlines()

    def _match(self, pattern, arg):
        '''Return True if the pattern can be matched in arg'''
        return re.findall(pattern, arg, flags=re.IGNORECASE) > 1

class Client(object):
    def __init__(self):
        self._sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
        self._port = musc.config.PORT
        self._host = musc.config.HOST

    def send(self, data):
        '''Send a command to the server. Returns the message given by the
        server'''
        self._sock.connect(
                (self._host,
                 self._port)
            )

        self._sock.sendall(json.dumps({'args':data}))
        returnValue = self._sock.recv(1024)
        self._sock.close()
        return returnValue

class TimeToQuit(object):
    isTime = False
