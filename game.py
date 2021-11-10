import threading

from networking import *
from playerV2 import *
from utils import distance_between_point

HIT_DISTANCE = 100


class Game(threading.Thread):

    def __init__(self, players: [Player]):
        threading.Thread.__init__(self)
        self._players = [p for p in players]
        self._threads = []

    def run(self) -> None:
        self.start_game()
        print("started Game with:", self._players)
        for i, player in enumerate(self._players):
            th = threading.Thread(target=self.recv_msgs, args=[player.get_socket()])
            th.start()
            self._threads.append(th)
        self.update()

    def update(self):
        while True:
            [p.update() for p in self._players]
            # curr_player = self._players[curr_player_index]
            # msg = curr_player.get_fpos() + "@" + curr_player.get_sprite()
            msg = ""
            for play in self._players:
                if play.punched()[0]:
                    self.check_collider(play)
                msg += play.get_fpos() + "@" + play.get_sprite() + "%" + str(play.get_percentage()) + "&"
            msg = msg[0:len(msg) - 1:]
            self.send_to_all(msg)

            time.sleep(0.05)

    def recv_msgs(self, player_socket: socket.socket):
        while True:
            msg = recv_data(player_socket)
            self.handle_data(msg, player_socket)

    def handle_data(self, data: str, player_socket: socket.socket):
        need_to_continue, curr_player = self.check_disconnection(player_socket, data)
        if need_to_continue:
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

            elif data == "*":  # TODO - remove!
                print(curr_player.get_fpos())
                curr_player.reset()
            else:
                print(f"who? {data}")

    def check_disconnection(self, client_socket: socket.socket, data: str) -> (bool, Player):
        curr_player = [p for p in self._players if p.get_socket() == client_socket][0]
        if data == '':
            print("connection Disconnected")
            self._players.remove(curr_player)
            client_socket.close()
            return False, curr_player

        else:
            if data == LOST_CONNECTION_MSG:
                self.send_to_all(data)
                print(data)
                # print("connection Disconnected")
                self._players.remove(curr_player)
                client_socket.close()
                return False, curr_player

        return True, curr_player

    def send_to_all(self, data: str):
        for p in self._players:
            send_msg(p.get_socket(), data, p.get_name())

    def start_game(self):
        for i, curr_player in enumerate(self._players):
            msg = str(i) + ',' + str(len(self._players))
            send_msg(curr_player.get_socket(), msg, curr_player.get_name())
            sprites = ""
            for p in self._players:
                if p is not curr_player:
                    sprites += p.get_character() + "&" + p.get_name() + ","
            sprites = sprites[0:len(sprites) - 1:]
            send_msg(curr_player.get_socket(), sprites, curr_player.get_name())

    def check_collider(self, play: Player):
        for curr_player in self._players:
            if curr_player == play:
                continue
            Xdistance = curr_player.get_pos()[0] - play.get_pos()[0]
            distance = distance_between_point(curr_player.get_pos(), play.get_pos())
            if abs(distance) < HIT_DISTANCE and abs(distance) < 100:
                curr_player.hit(play.punched()[1], bool(Xdistance > 0))
        play.reset_punch()
