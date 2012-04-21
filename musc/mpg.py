from subprocess import Popen, PIPE

class Mpg(object):
    command = 'mpg321'
    def __init__(self):
        self.__mpgProc = Popen([self.command, '-R', 'null'],
                stdin=PIPE,
                stdout=PIPE)

    def _send(self, message):
        self.__mpgProc.stdin.write(message + '\n')

    def __del__(self):
        print 'exiting'
        self.quit()

    def quit(self):
        self._send('Q')

if __name__ == '__main__':
    p = Mpg()
