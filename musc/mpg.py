#!/usr/bin/env python

from subprocess import Popen, PIPE

class Mpg(object):
    command = 'mpg321'
    def __init__(self):
        self.__mpgProc = Popen([self.command, '-R', 'null'],
                stdin=PIPE,
                stdout=PIPE)

        self._state = {
                'playStatus' : 0,
                'currentFrame' : 0,
                'framesRemaining' : 0,
                'currentTime' : 0,
                'timeRemaining' : 0
                }

    def _send(self, message):
        self.__mpgProc.stdin.write(message + '\n')

    def _read(self):
        return self.__mpgProc.stdout.readline()

    def __del__(self):
        print 'exiting'
        self.quit()

    def quit(self):
        self._send('QUIT')

    def load(self, filename):
        self.playing = True
        self._send('LOAD %s' % filename)

    def pause(self):
        self._send('PAUSE')

    def _update_from_output(self):
        output = self._read()
        if output[0] == '@':
            outputType = output[1]
            lines = output[3:].split()

            if outputType == 'F':
                self._state['currentFrame']    = float(lines[0])
                self._state['framesRemaining'] = float(lines[1])
                self._state['currentTime']     = float(lines[2])
                self._state['timeRemaining']   = float(lines[3])

            elif outputType == 'P':
                self._state['playStatus'] = int(lines[0])


if __name__ == '__main__':
    p = Mpg()
    p.load("/media/CAMERA/Squaredance/14 Everybody Rush.mp3")
    while 1:
        p._update_from_output(), p._read()
        print p._state
