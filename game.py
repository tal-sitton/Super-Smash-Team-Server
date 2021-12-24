import ipaddress
import sys
import threading

import pinger
from networking import *
from playerV2 import *
from utils import distance_between_point

HIT_DISTANCE = 100

SERVER_IP = "fe80:0:0:0:bc:5181:4c13:def8"


class Game(threading.Thread):

    def __init__(self, server, players: [Player], port: int):
        threading.Thread.__init__(self)
        self._players = [p for p in players]
        self._threads = []
        self._udp_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self._udp_socket.bind((SERVER_IP, port))
        self._killed = False
        self._server = server

    def run(self) -> None:
        self.start_game()
        print("started Game with:", self._players)
        for i in range(len(self._players)):
            th = threading.Thread(target=self.recv_msgs, args=[self._udp_socket])
            th.start()
            self._threads.append(th)
        # th = threading.Thread(target=self.pinger)
        # th.start()
        # self._threads.append(th)
        self.update()

    def recv_msgs(self, udp_socket: socket.socket):
        while not self._killed:
            msg, addr = recv_data(udp_socket)
            if not self._killed:
                self.handle_data((addr[0], addr[1]), msg)

    def update(self):
        while not self._killed:
            [p.update() for p in self._players]
            msg = ""
            alive = []
            for play in self._players:
                if not play.is_alive() and play.has_sent_message_of_death():
                    msg += "&"
                    continue

                if pinger.is_ping_error(play.get_tcp_socket()):
                    print("PING ERROR: ", )
                    self._players.remove(play)
                    self.sent_to_all_tcp("F")
                    print("KICK EVERYONE")
                    self._server.kill_match(self)
                    break

                if play.punched()[0]:
                    self.check_collider(play)
                msg += play.get_fpos() + "@" + play.get_sprite() + "%" + str(play.get_percentage()) + "&"
                if not play.is_alive() and not play.has_sent_message_of_death():
                    msg = msg[0:len(msg) - 1:1] + "@" + str(play.is_alive()) + "&"
                    play.death_message_has_been_sent()
                if play.is_alive():
                    alive.append(play)
            if len(alive) == 1:
                self.sent_to_all_tcp("W" + str(self._players.index(alive[0])))
                # todo add things to DB
                print("DEAD")
                self._server.kill_match(self)
            else:
                msg = msg[0:len(msg) - 1:]
                self.send_to_all(msg)

            time.sleep(0.05)

    def handle_data(self, player_addr: (str, int), data: str):
        # print([(p.get_address()[0].split("%")[0], p.get_address()[1]) for p in self._players])
        # print(player_addr)
        curr_player = \
            [p for p in self._players if
             (ipaddress.ip_address(p.get_address()[0].split("%")[0]).compressed, p.get_address()[1]) ==
             (ipaddress.ip_address(player_addr[0]).compressed, player_addr[1])][0]
        if data == Constants.JUMP:
            curr_player.set_action(Constants.JUMP)
        elif data == Constants.MOVE_RIGHT:
            curr_player.move(False)
        elif data == Constants.MOVE_LEFT:
            curr_player.move(True)
        elif data == Constants.RELEASED:
            curr_player.stopped_moving()
        elif data == Constants.A:
            curr_player.set_action(Constants.A_PUNCH)
        elif data == Constants.MOVE_DOWN:
            curr_player.set_action(Constants.MOVE_DOWN)

        elif data == "*" or data == '?':  # TODO - remove!
            print(curr_player.get_fpos())
        else:
            print(f"who? {data}")

    # def pinger(self):
    #     while not self._killed:
    #         for curr_player in self._players:
    #             try:
    #                 t = time.time()
    #                 curr_player.get_tcp_socket().send(b'T;')
    #                 curr_player.get_tcp_socket().recv(1)
    #                 ping = time.time() - t
    #             except Exception as e:
    #                 self._players.remove(curr_player)
    #                 self.sent_to_all_tcp("F")
    #                 # self._server.restart_match(self)
    #             time.sleep(0.3)

    def send_to_all(self, data: str):
        for p in self._players:
            send_msg(self._udp_socket, p.get_address(), data)

    def sent_to_all_tcp(self, data):
        for p in self._players:
            send_tcp_msg(p.get_tcp_socket(), data)

    def start_game(self):
        for i, curr_player in enumerate(self._players):
            msg = str(i) + ',' + str(len(self._players))
            send_tcp_msg(curr_player.get_tcp_socket(), "I" + msg)
            sprites = ""
            for p in self._players:
                if p is not curr_player:
                    sprites += p.get_character() + "&&&" + p.get_name() + ",,,"
            sprites = sprites[0:len(sprites) - 3:]
            send_tcp_msg(curr_player.get_tcp_socket(), "S" + sprites)

    def check_collider(self, play: Player):
        for curr_player in self._players:
            if curr_player == play:
                continue
            Xdistance = curr_player.get_pos()[0] - play.get_pos()[0]
            distance = distance_between_point(curr_player.get_pos(), play.get_pos())
            if abs(distance) < HIT_DISTANCE and abs(distance) < 100:
                curr_player.hit(play.punched()[1], bool(Xdistance > 0))
        play.reset_punch()

    def get_players(self):
        return self._players

    def kill(self):
        self._killed = True
        sys.exit()
