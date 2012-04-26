import json

class Client(object):
    def __init_(self, port=7785, host='localhost'):
        pass

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
