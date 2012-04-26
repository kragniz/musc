import json
import socket

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

class Protocol(object):
    '''Generates and returns some protocol strings'''
    def __init__(self):
        pass

    def skipSong(self):
        return json.dumps({
            'C': 'skip'
            })

    def getPlaylist(self):
        return json.dumps({
            'C': 'get',
            'content': 'playlist'
            })

    def addSong(self, name):
        return json.dumps({
            'C': 'play',
            'name': name
            })

    def newPlaylist(self, songType):
        return json.dumps({
            'C': 'new_playlist',
            'type': songType
            })

    def togglePause(self):
        return json.dumps({
            'C': 'toggle_pause'
            })
