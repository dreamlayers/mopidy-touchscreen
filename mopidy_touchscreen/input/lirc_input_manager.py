import socket
from datetime import datetime

class lircsource(object):
    def __init__(self, fname = '/var/run/lirc/lircd'):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.connect(fname)
        self.sock.setblocking(0)
        self.lastkey = None

    def getraw(self):
        try:
            s = self.sock.recv(4096)
        except:
            return []
        res = []
        for l in s.splitlines():
            res.append(l.split(' ')[2])
        return res

    def get(self):
        res = []
        keys = self.getraw()
        now = datetime.now()
        mayrepeat = self.lastkey is not None and \
                    (now-self.lktime).total_seconds() < 0.5
        if len(keys) > 0:
            self.lktime = now
        for k in keys:
            if mayrepeat:
                if k == self.lastkey:
                    continue
            else:
                mayrepeat = True
            res.append(k)
            self.lastkey = k
        return res

class LIRCManager():
    def __init__(self):
        self.lirc = lircsource()

    def get(self):
        return self.lirc.get()
