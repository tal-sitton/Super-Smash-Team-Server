import socket
import threading
import time

import game
import networking
import pinger
from playerV2 import Player
from sql_handler import SQLHandler

SERVER_IP = "fe80:0:0:0:bc:5181:4c13:def8"
SERVER_TCP_PORT = 2212
LOST_CONNECTION_MSG = "LOST CONNECTION"
MAX_IN_GROUP = 2
BUFFER_SIZE = 1024

global server_udp
global server_tcp


class Server:
    def __init__(self):
        self.current_groups_players = []
        self.threads = []
        self.sqlhandler = SQLHandler()
        global server_tcp
        global server_udp
        server_tcp = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server_tcp.bind((SERVER_IP, SERVER_TCP_PORT))
        server_tcp.listen()
        print("LISTENING...")
        self.next_udp_port = 2221
        th = threading.Thread(target=self.check_pings)
        th.start()
        while True:
            self.new_client()

    def new_client(self):
        client_tcp, addr = server_tcp.accept()
        print("NEW PLAYER")

        try:
            networking.send_tcp_msg(client_tcp, str(self.next_udp_port))
            sprite_name, ip, client_udp_port = client_tcp.recv(BUFFER_SIZE).decode().split(',')
            right = False
            while not right:
                msg = client_tcp.recv(BUFFER_SIZE).decode()
                action, username = msg[:6], msg[6:]
                passhash = client_tcp.recv(BUFFER_SIZE)
                print("ACTION:", action)
                print("USERNAME:", username)
                print("passHash:", passhash)

                right, user_id = self.check_password(username, passhash)
                if action == "SignUp":
                    if not right:
                        user_id = self.sqlhandler.insert(username, passhash, 0, 0)
                        right = True

                networking.send_tcp_msg(client_tcp, str(right))
            new_player = Player(sprite_name, client_tcp, (ip, int(client_udp_port)), username,
                                295 + 200 * len(self.current_groups_players),
                                user_id)
        except Exception as e:
            print(e)
            return
        pinger.Pinger(client_tcp).start()
        self.matchmaking(new_player)

    def check_password(self, username, pass_hash):
        for user_id in self.sqlhandler.get_data("rowid", ("username", username)):
            user_id = user_id[0]
            if pass_hash == self.sqlhandler.get_data("password", ("rowid", user_id))[0][0]:
                return True, user_id
        return False, 0

    def matchmaking(self, new_player: Player):
        print(f"MATCHMAKING!!! with {new_player}")
        self.current_groups_players.append(new_player)
        print("IN THE MATCHMAKING: ", self.current_groups_players)
        if len(self.current_groups_players) == MAX_IN_GROUP:
            th = game.Game(self, self.current_groups_players, self.next_udp_port)
            th.start()
            self.threads.append(th)
            self.current_groups_players.clear()

            self.next_udp_port += 1
            while not networking.check_port(self.next_udp_port):
                self.next_udp_port += 1

    def check_pings(self):
        while True:
            if self.current_groups_players:
                print("check")
                players_sockets = [play.get_tcp_socket() for play in self.current_groups_players]
                for sock in players_sockets:
                    if pinger.is_ping_error(sock):
                        self.current_groups_players.remove(self.current_groups_players[players_sockets.index(sock)])
                        print("REMOVED PLAYER: ", sock)
                        print("current players: ", self.current_groups_players)
            time.sleep(1)

    def restart_match(self, match: game.Game):
        print("restarting match with:", match.get_players())
        for play in match.get_players():
            self.matchmaking(self.reset_player(play))
        self.kill_match(match)

    def reset_player(self, p: Player) -> Player:
        new_p = Player(p.get_character(), p.get_tcp_socket(), p.get_address(), p.get_name())
        del p
        return new_p

    def kill_match(self, match: game.Game):
        match.kill()
        self.threads.remove(match)
        print("KILLED MATCH")


if __name__ == '__main__':
    Server()
