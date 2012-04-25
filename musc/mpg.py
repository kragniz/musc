#!/usr/bin/env python

from subprocess import Popen, PIPE
import threading
import time

class Mpg(object):
    command = 'mpg123' #the command used to play mp3 files

    class States(object):
        '''Class used to hold bunch of states'''
        def __init__(self):
            self.threadRunning = True

            self.playStatus = 0
            self.currentFrame = None
            self.framesRemaining = 0
            self.currentTime = 0
            self.timeRemaining = 0
            self.playing = False
            self.volume = 100

            self.inputLock = threading.Lock()
            self.outputLock = threading.Lock()

    class InputGetter(threading.Thread):
        '''Thread used to collect status from mpg's stdout'''
        def __init__(self, reader, states):
            super(Mpg.InputGetter, self).__init__()
            self._reader = reader
            self._states = states
            
        def run(self):
            while self._states.threadRunning:
                output = self._reader()
                if output[0] == '@':
                    outputType = output[1]
                    lines = output[3:].split()

                    if outputType == 'F':
                        self._states.currentFrame    = float(lines[0])
                        self._states.framesRemaining = float(lines[1])
                        self._states.currentTime     = float(lines[2])
                        self._states.timeRemaining   = float(lines[3])

                    elif outputType == 'P':
                        self._states.playStatus = int(lines[0])

                frames = self._states.framesRemaining
                if frames <= 4:# and frames is not None:
                    self._states.playing = False
                else:
                    self._states.playing = True

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
        self._send('LOAD %s' % filename)

    def pause(self):
        '''Pause the music'''
        self._send('PAUSE')

    @property
    def volume(self):
        '''volume of the player'''
        return self._states.volume

    @volume.setter
    def volume(self, v):
        self._states.volume = v
        self._send('VOLUME %s' % v)

    def playNext(self):
        '''Load the next item in the queue and remove it from the queue'''
        print 'loading next file...'
        if self.hasItemsInQueue:
            musicFile = self._playQueue.pop(0)
            print 'loading', musicFile
            self.load(musicFile)
        else:
            print 'no more items in queue.'

    @property
    def hasItemsInQueue(self):
        '''Return True if the queue contains items'''
        return len(self._playQueue) > 0

    @property
    def playing(self):
        '''Return True if music is currently playing'''
        return self._states.playing is True

    @playing.setter
    def playing(self, b):
        self._states.playing = b

    @property
    def queue(self):
        '''List holding queue of files to play'''
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
        if not p.playing:
            print 'playing next'
            p.playNext()
            time.sleep(2)
        if not i % 100000: print i, p.playing
