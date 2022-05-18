import socket
import threading
import time
from typing import List


def is_ping_error(tcp_socket):
    return [ping for ping in pingers if ping.get_socket() == tcp_socket][0].get_is_error()


class Pinger(threading.Thread):

    def __init__(self, tcp_socket: socket.socket):
        print("INIT")
        threading.Thread.__init__(self)
        self.tcp = tcp_socket
        pingers.append(self)
        self.running = True
        self.error = False
        print("END INIT")

    def run(self) -> None:
        print("START RUNNING")
        self.tcp.settimeout(8)
        while self.running:
            try:
                # print("PING!")
                t = time.time()
                self.tcp.send(b'T;')
                # print("sent")
                self.tcp.recv(1)
                ping = (time.time() - t) * 1000
                # print(ping, "ms", self.tcp)
            except Exception as e:
                print("THE E:", e)
                self.error = True
                self.running = False
            time.sleep(0.3)

    def get_socket(self):
        return self.tcp

    def get_is_error(self):
        return self.error

    def stop(self):
        self.running = False


pingers: List[Pinger] = []
