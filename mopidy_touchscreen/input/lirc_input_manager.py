import socket

class LIRCManager():
    def __init__(self, fname = '/var/run/lirc/lircd'):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.connect(fname)
        self.sock.setblocking(0)

    def get(self):
        try:
            s = self.sock.recv(4096)
        except:
            return []
        res = []
        for l in s.splitlines():
            ldata = l.split(' ')
            # Ignore repeats
            if int(ldata[1]) == 0:
                res.append(ldata[2])
        return res
