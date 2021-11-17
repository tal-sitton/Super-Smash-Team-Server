import sys
import threading

from networking import *
from playerV2 import *
from utils import distance_between_point

HIT_DISTANCE = 100


class Game(threading.Thread):

    def __init__(self, server, players: [Player], udp_socket: socket.socket):
        threading.Thread.__init__(self)
        self._players = [p for p in players]
        self._threads = []
        self._udp_socket = udp_socket
        self._killed = False
        self._server = server

    def run(self) -> None:
        self.start_game()
        print("started Game with:", self._players)
        for i in range(len(self._players)):
            th = threading.Thread(target=self.recv_msgs, args=[self._udp_socket])
            th.start()
            self._threads.append(th)
        th = threading.Thread(target=self.pinger)
        th.start()
        self._threads.append(th)
        self.update()

    def recv_msgs(self, udp_socket: socket.socket):
        while not self._killed:
            msg, addr = recv_data(udp_socket)
            self.handle_data(addr, msg)

    def update(self):
        while not self._killed:
            [p.update() for p in self._players]
            msg = ""
            for play in self._players:
                if play.punched()[0]:
                    self.check_collider(play)
                msg += play.get_fpos() + "@" + play.get_sprite() + "%" + str(play.get_percentage()) + "&"
            msg = msg[0:len(msg) - 1:]
            self.send_to_all(msg)

            time.sleep(0.05)

    def handle_data(self, player_addr: (str, int), data: str):
        curr_player = [p for p in self._players if p.get_address() == player_addr][0]
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
            # curr_player.reset()
        else:
            print(f"who? {data}")

    def pinger(self):
        while not self._killed:
            for curr_player in self._players:
                try:
                    t = time.time()
                    curr_player.get_tcp_socket().send(b'T;')
                    curr_player.get_tcp_socket().recv(1)
                    ping = time.time() - t
                except Exception as e:
                    self._players.remove(curr_player)
                    # TODO - send all players a sad message
                    self._server.restart_match(self)
                time.sleep(0.3)

    def send_to_all(self, data: str):
        for p in self._players:
            send_msg(self._udp_socket, p.get_address(), data)

    def start_game(self):
        for i, curr_player in enumerate(self._players):
            msg = str(i) + ',' + str(len(self._players))
            send_tcp_msg(curr_player.get_tcp_socket(), msg)
            sprites = ""
            for p in self._players:
                if p is not curr_player:
                    sprites += p.get_character() + "&" + p.get_name() + ","
            sprites = sprites[0:len(sprites) - 1:]
            send_tcp_msg(curr_player.get_tcp_socket(), sprites)

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
