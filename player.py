import socket


class Constants:
    JUMP = "Jump"
    FALL = "Fall"
    IDLE = "Idle"
    MOVE_RIGHT = "mr"
    MOVE_LEFT = "ml"
    MOVE_SPRITE = "Walk"
    RELEASED = "rel"


class Player:

    def __init__(self, character: str, client_socket: socket.socket, group: int):
        """

        :param name: the name of the player
        :type name: str
        :param character: the name of the character the player is playing
        :type character: str
        :param client_socket: the player's client's socket
        :type client_socket: socket.socket
        :param group: the group the player is part of
        :type group: int
        """
        # self.name = name
        self.character = character
        self.START_HEIGHT = 235  # the height the player starts in
        self.MAX_JUMP_HEIGHT = self.START_HEIGHT - 100  # the max height of the player when jump, 30 units above the
        self._client_socket = client_socket
        self._group = group
        self._action = Constants.IDLE
        self._pos = (495, 235)
        self._sprite = self._action
        self._started = False

    # def get_name(self) -> str:
    #     return self.name

    def get_character(self) -> str:
        return self.character

    def get_socket(self) -> socket.socket:
        return self._client_socket

    def get_group(self) -> int:
        return self._group

    def get_action(self) -> str:
        return self._action

    def get_sprite(self) -> str:
        return self._sprite

    def get_pos(self) -> (int, int):
        return self._pos

    def get_fpos(self) -> str:
        """
        returns a the formatted position
        """
        return str(self._pos[0]) + "," + str(self._pos[1])

    def started(self):
        return self._started

    def start(self, start: bool):
        self._started = start

    def set_action(self, action: str):
        if (action == Constants.JUMP and self._action == Constants.IDLE) or action != Constants.JUMP:
            self._action = action
            self._sprite = action

    def move(self, to_left: bool):
        if to_left and self._pos[0] - 2 > -106:
            self._pos = (self._pos[0] - 20, self._pos[1])
            if self._action == Constants.IDLE:
                self._sprite = Constants.MOVE_SPRITE

        elif not to_left and self._pos[0] + 2 < 1056:
            self._pos = (self._pos[0] + 20, self._pos[1])
            if self._action == Constants.IDLE:
                self._sprite = Constants.MOVE_SPRITE

    def stopped_moving(self):
        if self._sprite == Constants.MOVE_SPRITE:
            self._sprite = Constants.IDLE
            self._action = Constants.IDLE

    def update(self):
        if self._action == Constants.JUMP:
            if self._pos[1] > self.MAX_JUMP_HEIGHT:
                self._pos = (self._pos[0], self._pos[1] - 2)
            else:
                self._action = Constants.FALL
                self._sprite = Constants.FALL

        if self._action == Constants.FALL:
            if self._pos[1] < self.START_HEIGHT:
                self._pos = (self._pos[0], self._pos[1] + 2)
            else:
                self._action = Constants.IDLE
                self._sprite = Constants.IDLE
