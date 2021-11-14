import socket

import game
from playerV2 import Player

SERVER_IP = "0.0.0.0"
SERVER_TCP_PORT = 2212
LOST_CONNECTION_MSG = "LOST CONNECTION"
MAX_IN_GROUP = 1

current_groups_players = []
threads = []
BUFFER_SIZE = 1024

global server_udp
global server_tcp


def main():
    global server_tcp
    global server_udp
    server_tcp = socket.socket()
    server_tcp.bind((SERVER_IP, SERVER_TCP_PORT))
    server_tcp.listen()
    server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_udp.bind(("0.0.0.0", 2213))
    while True:
        new_client()


def new_client():
    client_tcp, addr = server_tcp.accept()
    sprite_name, player_name, client_udp_port = client_tcp.recv(BUFFER_SIZE).decode().split(',')

    new_player = Player(sprite_name, client_tcp, (client_tcp.getsockname()[0], int(client_udp_port)), player_name)
    matchmaking(new_player)


def reset_player(p: Player) -> Player:
    new_p = Player(p.get_character(), p.get_tcp_socket(), p.get_address(), p.get_name())
    del p
    return new_p


def restart_match(match: game.Game):
    print("restarting match with:", match.get_players())
    for play in match.get_players():
        matchmaking(reset_player(play))
    match.kill()
    threads.remove(match)


def matchmaking(new_player: Player):
    current_groups_players.append(new_player)
    if len(current_groups_players) == MAX_IN_GROUP:
        th = game.Game(current_groups_players, server_udp)
        th.start()
        threads.append(th)
        current_groups_players.clear()


if __name__ == '__main__':
    main()
