import socket
import os
from select import select

class SocketServer:
    def __init__(self, socket_path = '/tmp/mopidy_display',
                 bufsize = 320*240*4):
        # remove the socket file if it already exists
        try:
            os.unlink(socket_path)
        except OSError:
            if os.path.exists(socket_path):
                raise
        self.socket_path = socket_path

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(socket_path)
        os.chmod(socket_path, 0o660)
        self.server.listen(1)
        self.server_list = [ self.server ]
        self.read_list = None

        self.buf = bytearray(bufsize)
        self.bufview = memoryview(self.buf)
        self.bufidx = 0

    def _close_client(self):
        self.read_list[0].close()
        self.read_list = None
        self.bufidx = 0

    def poll(self):
        if not self.read_list:
            # Wait for a client
            readable, writable, errored = select(self.server_list, [], [], 0)
            if readable:
                connection, client_address = self.server.accept()
                self.read_list = [ connection ]
        else:
            # Receive data from the client
            readable, writable, errored = select(self.read_list, [], [], 0)
            if readable:
                got = readable[0].recv_into(self.bufview[self.bufidx:])
                if got <= 0:
                    self._close_client()
                else:
                    self.bufidx += got
                    if self.bufidx == len(self.buf):
                        self._close_client()
                        return self.buf
            return None

    def __del__(self):
        os.unlink(self.socket_path)
