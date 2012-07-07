import urllib
import httplib
import re
import config

class Scrobbler(object):
    def __init__(self):
        self.token = self.getToken

    def request(self, args):
        params = urllib.urlencode(args)
        header = {'user-agent' : 'musc/0.1',
                  'Content-type': 'application/x-www-form-urlencoded'}

        lastfm = httplib.HTTPConnection('ws.audioscrobbler.com')
        lastfm.request('POST','/2.0/?',params,header)
        response = lastfm.getresponse()
        return response.read()

    def getToken(self):
        token = self.request({'method' : 'auth.getToken',
                              'api_sig' : config.apiSig,
                              'api_key' : config.apiKey})
        return re.search('<token.+token>', token).group()[7:-8]

if __name__ == '__main__':
    s = Scrobbler()
    print s.getToken()
