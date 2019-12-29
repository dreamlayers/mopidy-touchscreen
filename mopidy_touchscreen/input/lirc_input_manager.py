import socket

class LIRCManager():
    def __init__(self, fname = 'none', remote = 'none', repeat = 0):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.connect('/var/run/lirc/lircd' if fname == 'none' else fname)
        self.sock.setblocking(0)
        self.remote = None if remote == 'none' else remote
        self.repeat = repeat

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
                res.append(ldata[2])
        return res
