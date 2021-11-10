import Physics
import game
import playerV2
from networking import *
from playerV2 import PhysicsConstants
from playerV2 import Player

SERVER_IP = "0.0.0.0"
SERVER_PORT = 2212
LOST_CONNECTION_MSG = "LOST CONNECTION"
MAX_IN_GROUP = 2

current_groups_players = []
threads = []
global server


def main():
    global server
    server = socket.socket()
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    while True:
        new_client()


def new_client():
    client_socket, addr = server.accept()
    sprite_name, player_name = recv_data(client_socket).split(',')
    print(sprite_name)
    print(player_name)
    current_groups_players.append(Player(sprite_name, client_socket, player_name))
    if len(current_groups_players) == MAX_IN_GROUP:
        th = game.Game(current_groups_players)
        th.start()
        threads.append(th)
        current_groups_players.clear()



if __name__ == '__main__':
    main()
