#!/usr/bin/env python

from subprocess import Popen, PIPE
import threading

class Mpg(object):
    command = 'mpg321'

    class States(object):
        threadRunning = True
        playing = {
                    'playStatus' : 0,
                    'currentFrame' : 0,
                    'framesRemaining' : 0,
                    'currentTime' : 0,
                    'timeRemaining' : 0,
                    'playing' : False
                  }
        inputLock = threading.Lock()
        outputLock = threading.Lock()

    class InputGetter(threading.Thread):
        def __init__(self, reader, states):
            threading.Thread.__init__(self)
            self._reader = reader
            self._states = states
            
        def run(self):
            while self._states.threadRunning:
                output = self._reader()
                if output[0] == '@':
                    outputType = output[1]
                    lines = output[3:].split()

                    if outputType == 'F':
                        self._states.playing['currentFrame']    = float(lines[0])
                        self._states.playing['framesRemaining'] = float(lines[1])
                        self._states.playing['currentTime']     = float(lines[2])
                        self._states.playing['timeRemaining']   = float(lines[3])

                    elif outputType == 'P':
                        self._states.playing['playStatus'] = int(lines[0])

                    if self._states.playing['framesRemaining'] <= 4:
                        self._states.playing['playing'] = False

    def __init__(self):
        self.__mpgProc = Popen([self.command, '-R', 'null'],
                stdin=PIPE,
                stdout=PIPE)

        self._states = self.States()

        self._playQueue = []
        inputThread = self.InputGetter(self._read,
                                       self._states)
        inputThread.start()

    def _send(self, message):
        '''Send a command to mpg'''
        with self._states.outputLock:
            self.__mpgProc.stdin.write(message + '\n')

    def _read(self):
        '''Read the output of the mpg process'''
        with self._states.inputLock:
            return self.__mpgProc.stdout.readline()

    def __del__(self):
        '''Close the mpg process when this class is destroyed'''
        print 'exiting'
        self._states.running = False
        self.quit()

    def quit(self):
        '''Quit the mpg process'''
        self._send('QUIT')

    def load(self, filename):
        '''Load a new file to play'''
        self._states.playing['playing'] = True
        self._send('LOAD %s' % filename)

    def pause(self):
        '''Pause the music'''
        self._send('PAUSE')

    def _update_from_output(self):
        '''Update status from the current output'''

    def playNext(self):
        '''Load the next item in the queue and remove it from the queue'''
        print 'loading next file...'
        self._states.playing['playing'] = True
        self.load(self._playQueue.pop(0))

    @property
    def hasItemsInQueue(self):
        '''Return True if the queue contains items'''
        return len(self._playQueue) > 0

    @property
    def playing(self):
        '''Return True if music is currently playing'''
        return self._states.playing['playing']

    @property
    def queue(self):
        return self._playQueue

    @queue.setter
    def queue(self, item):
        self._playQueue = item


if __name__ == '__main__':
    p = Mpg()
    p.queue = ["/media/CAMERA/Squaredance/14 Everybody Rush.mp3",
               "/media/CAMERA/Squaredance/30 Deep Beep (feat. Jackal Queenston.mp3"]
    i = 0
    while 1:
        i += 1
        p._update_from_output()
        if not p.playing:
            print 'playing next'
            p.playNext()
        if not i%100: print i, p._states.playing, p.playing
