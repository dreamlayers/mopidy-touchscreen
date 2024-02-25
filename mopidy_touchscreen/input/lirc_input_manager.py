import socket
from . import InputManager

class LIRCManager():
    lircmap = {
        ('pageup', InputManager.swipe, InputManager.up),
        ('up', InputManager.key, InputManager.up),
        ('down', InputManager.key,  InputManager.down),
        ('pagedown', InputManager.swipe, InputManager.down),
        ('left', InputManager.key, InputManager.left),
        ('right', InputManager.key, InputManager.right),
        ('enter', InputManager.key, InputManager.enter),
        ('enqueue', InputManager.key, InputManager.enqueue),
        ('back', InputManager.key, InputManager.back),
    }

    def _makedict(self, config):
        self.lircdict = {}
        for key in self.lircmap:
            lirckey = config['lirc_' + key[0]]
            if lirckey != 'none':
                self.lircdict[lirckey] = key[1:]

    def __init__(self, config):
        fname = config['lirc_socket']
        remote = config['lirc_remote']
        self.repeat = config['lirc_repeat']

        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.connect('/var/run/lirc/lircd' if fname == 'none' else fname)
        self.sock.setblocking(0)
        self.remote = None if remote == 'none' else remote
        self._makedict(config)

    def get(self):
        try:
            s = self.sock.recv(4096)
        except:
            return []
        res = []
        for l in s.splitlines():
            ldata = l.decode().split(' ')
            repeat = int(ldata[1], 16)
            if (self.remote is None or ldata[3] == self.remote) and \
               (repeat == 0 or
                (self.repeat != 0 and repeat % self.repeat == 0)):
                mappedkey = self.lircdict.get(ldata[2])
                if mappedkey is not None:
                    res.append(mappedkey)

        return res
