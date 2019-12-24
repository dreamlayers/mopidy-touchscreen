import socket

class LIRCManager():
    def __init__(self, fname = 'none', remote = 'none'):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.connect('/var/run/lirc/lircd' if fname == 'none' else fname)
        self.sock.setblocking(0)
        self.remote = None if remote == 'none' else remote

    def get(self):
        try:
            s = self.sock.recv(4096)
        except:
            return []
        res = []
        for l in s.splitlines():
            ldata = l.split(' ')
            # Ignore repeats
            if int(ldata[1]) == 0 and \
               (self.remote is None or ldata[3] == self.remote):
                res.append(ldata[2])
        return res
