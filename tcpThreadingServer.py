import socket

import game
import networking
from playerV2 import Player

SERVER_IP = "0.0.0.0"
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
        global server_tcp
        global server_udp
        server_tcp = socket.socket()
        server_tcp.bind((SERVER_IP, SERVER_TCP_PORT))
        server_tcp.listen()
        self.next_udp_port = 2221
        while True:
            self.new_client()

    def new_client(self):
        client_tcp, addr = server_tcp.accept()
        networking.send_tcp_msg(client_tcp, str(self.next_udp_port))
        sprite_name, player_name, client_ip, client_udp_port = client_tcp.recv(BUFFER_SIZE).decode().split(',')

        new_player = Player(sprite_name, client_tcp, (client_ip, int(client_udp_port)), player_name)
        self.matchmaking(new_player)

    def reset_player(self, p: Player) -> Player:
        new_p = Player(p.get_character(), p.get_tcp_socket(), p.get_address(), p.get_name())
        del p
        return new_p

    def restart_match(self, match: game.Game):
        print("restarting match with:", match.get_players())
        for play in match.get_players():
            self.matchmaking(self.reset_player(play))
        match.kill()
        self.threads.remove(match)

    def matchmaking(self, new_player: Player):
        print(f"MATCHMAKING!!! with {new_player}")
        self.current_groups_players.append(new_player)
        print("IN THE MATCHMAKING: ", self.current_groups_players)
        if len(self.current_groups_players) == MAX_IN_GROUP:
            th = game.Game(self, self.current_groups_players, self.next_udp_port)
            self.next_udp_port += 1
            while not networking.check_port(self.next_udp_port):
                self.next_udp_port += 1
            th.start()
            self.threads.append(th)
            self.current_groups_players.clear()


if __name__ == '__main__':
    Server()
