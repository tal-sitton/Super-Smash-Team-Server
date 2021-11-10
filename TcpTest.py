import select
import socket
import threading
import time

from player import Player, Constants

SERVER_IP = "0.0.0.0"
SERVER_PORT = 2212
LOST_CONNECTION_MSG = "LOST CONNECTION"

# MAX_IN_GROUP = 3
MAX_IN_GROUP = 2
currentGroup = (1, 0)  # the current group information - (number_of_group, number_of_people_in_group)
last_msg_of_group = []  # the last msg of each group, by index=group_num-1

server = socket.socket()
server.bind((SERVER_IP, SERVER_PORT))
server.listen()

players = []  # the connected players and their info

printed_sent = False


def main():
    th = threading.Thread(target=update)
    th.start()
    while True:
        clients_sockets = [p.get_socket() for p in players]
        rlist, wlist, xlist = select.select([server] + clients_sockets, clients_sockets, [])  # sets up a select server
        for current_socket in rlist:
            if current_socket is server:
                new_client()  # receives a new client
            else:
                handle_data(current_socket)  # receive data from an existing client


def update():
    while True:
        active_players = [curr_player for curr_player in players if
                          curr_player.started()]  # player that has started their match

        [p.update() for p in active_players]

        curr_player_index = 0
        while curr_player_index < len(active_players) - 1:
            curr_player = active_players[curr_player_index]
            msg = curr_player.get_fpos() + "@" + curr_player.get_sprite()
            for i in range(MAX_IN_GROUP - 1):
                msg += "&" + active_players[curr_player_index + i + 1].get_fpos() + "@" + active_players[
                    curr_player_index + i + 1].get_sprite()
            send_msg_to_group(curr_player.get_group(), msg)
            curr_player_index += 3

        time.sleep(0.001)
        # time.sleep(1)


def handle_data(client_socket: socket.socket):
    data = recv_data(client_socket)
    need_to_continue, curr_player = check_disconnection(client_socket, data)
    if need_to_continue:
        if data == Constants.JUMP:
            curr_player.set_action(Constants.JUMP)
        elif data == Constants.MOVE_RIGHT:
            curr_player.move(False)
        elif data == Constants.MOVE_LEFT:
            curr_player.move(True)
        elif data == Constants.RELEASED:
            curr_player.stopped_moving()

        elif data == "?":
            print(curr_player.get_fpos())
        else:
            print(f"ho? {data}")


def send_msg(client_socket: socket.socket, msg: str):
    """
    formats a the message the server wants to send and sends it.
    :param client_socket: the socket the server needs to send to
    :param msg: the message that needs to be formatted and sent
    """

    if client_socket in [p.get_socket() for p in players]:
        try:
            client_socket.send((str(len(msg)).zfill(2) + msg).encode())
        except Exception as e:
            print(e)


def recv_data(client_socket: socket.socket):
    """
    receives data from a client.
    :param client_socket: the socket of the client that we want to receive from
    """
    try:
        data = client_socket.recv(int.from_bytes(client_socket.recv(2), byteorder='big')).decode()
    except ConnectionResetError as e:
        data = LOST_CONNECTION_MSG
    return data


def check_disconnection(client_socket: socket.socket, data: str) -> (bool, Player):
    curr_client = [p for p in players if p.get_socket() == client_socket][0]
    if data == '':
        print("connection Disconnected")
        players.remove(curr_client)
        client_socket.close()
        return False, curr_client

    else:
        if data == LOST_CONNECTION_MSG:
            send_msg_to_group(curr_client.get_group(), data)
            print(data)
            # print("connection Disconnected")
            players.remove(curr_client)
            client_socket.close()
            return False, curr_client

    return True, curr_client


def new_client():
    """
    handle the new client when it connects - give him a player name (X or O), tells him to start, and adds him to the
    list.
    """
    global currentGroup

    client_socket, addr = server.accept()
    if currentGroup[1] < MAX_IN_GROUP:
        sprite_name = recv_data(client_socket)
        print(sprite_name)
        players.append(Player(sprite_name, client_socket, currentGroup[0]))
        currentGroup = (currentGroup[0], currentGroup[1] + 1)
        if currentGroup[1] == MAX_IN_GROUP:
            start_group(currentGroup[0])
            currentGroup = (currentGroup[0] + 1, 0)
        print("connected to a new client")


def cords_from_msg(client_socket: socket.socket) -> (int, int):
    """
    cords should be formatted like "X,Y"
    :param client_socket: the socket of the clients to retrieve the cords from
    :type client_socket: socket.socket
    :return: the cords of the player from a message
    :rtype: tuple
    """
    data = recv_data(client_socket)
    return int(data.split(",")[0]), int(data.split(",")[1])


def start_group(group: int):
    index = 0
    print(f"started group {group}")
    for curr_player in players:
        if curr_player.get_group() == group:
            send_msg(curr_player.get_socket(), str(index) + ',' + str(MAX_IN_GROUP))
            sprites = ""
            for p in players:
                if p.get_group() == group and p is not curr_player:
                    sprites += p.get_character() + ","
            sprites = sprites[0:len(sprites) - 1:]
            print(sprites)
            send_msg(curr_player.get_socket(), sprites)
            print("startG: " + str(index) + ',' + str(MAX_IN_GROUP))
            curr_player.start(True)
            index += 1
    last_msg_of_group.append("")


def send_msg_to_group(group: int, data: str):
    if last_msg_of_group[group - 1] == data:
        last_msg_of_group[group - 1] = ""
        return

    for curr_player in players:
        if curr_player.get_group() == group:
            send_msg(curr_player.get_socket(), data)
            # messages_to_send.append((curr_player, curr_player.get_socket(), data.encode()))
        last_msg_of_group[group - 1] = data


if __name__ == '__main__':
    main()
