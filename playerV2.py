import socket
import time

from Physics import *


class Constants:
    JUMP = "Jump"
    FALL = "Fall"
    IDLE = "Idle"
    MOVE_RIGHT = "mr"
    MOVE_LEFT = "ml"
    MOVE_SPRITE = "Walk"
    RELEASED = "rel"
    BEEN_HIT = "Hurt"
    A_PUNCH = "A_PUN"
    A = "A_"
    A_AIR = "AAir"
    MOVING_DISTANCE = 7
    GROUND_UNMOVABLE = [A_PUNCH]
    FULL_UNMOVABLE = [BEEN_HIT]
    JUMP_PUNCH_RATE = 0.050  # in seconds


class PhysicsConstants:
    d = 100  # distance between start height and maximum target height in pixels
    vf = 0  # final velocity
    t = 1.5  # time to top
    vi = get_vi(vf=0, d=d, t=t)  # initial jump velocity
    ag = -get_a(vi=vi, vf=vf, d=d, t=t)  # gravity
    hit_vi = 50  # initial hit velocity
    hit_a = get_a(vi=-20, vf=0, t=0.5)  # the acceleration of the player when hit


class Player:

    def __init__(self, character: str, _client_tcp_socket: socket.socket, _client_address: (str, int), name: str):
        """

        :param name: the name of the player
        :type name: str
        :param character: the name of the character the player is playing
        :type character: str
        :param _client_address: the player's client's address (IP,port)
        :type _client_address: (str,int)
        """
        # self.name = name
        self._character = character
        self.START_HEIGHT = 300  # the height the player starts in
        self.MAX_JUMP_HEIGHT = self.START_HEIGHT - 200  # the max height of the player when jump, 30 units above the

        self._client_address = _client_address
        self._client_tcp_socket = _client_tcp_socket

        self._name = name
        self._actions = [(Constants.IDLE, time.time())]
        self._pos = (495, self.START_HEIGHT)
        self._direction = "right"
        self._sprite = Constants.IDLE
        self._percentage = 1
        self._punched = (False, 0)
        self._next_time_to_jump = 0
        self._next_time_to_punch = 0
        self._hit_side_multiplier = 1
        self._temp_vi = PhysicsConstants.vi
        self._temp_t = -1

    def reset(self):
        self._pos = (495, self.START_HEIGHT)
        self._sprite = Constants.IDLE
        self._actions = [(Constants.IDLE, time.time())]

    def get_character(self) -> str:
        return self._character

    def get_percentage(self) -> int:
        return self._percentage

    def get_address(self) -> (str, int):
        return self._client_address

    def get_tcp_socket(self) -> socket.socket:
        return self._client_tcp_socket

    def get_name(self) -> str:
        return self._name

    def get_actions(self) -> [str]:
        return self._actions

    def get_sprite(self) -> str:
        return self._sprite

    def get_pos(self) -> (int, int):
        return self._pos

    def punched(self):
        return self._punched

    def reset_punch(self):
        self._punched = (False, 0)

    def hit(self, damage: int, is_from_left: bool):
        print(damage)
        print(self._percentage)
        self._percentage += damage
        print(self._percentage)
        self._sprite = Constants.BEEN_HIT
        self._hit_side_multiplier = 1 if is_from_left else -1
        self._actions = [(Constants.BEEN_HIT, time.time())]
        self._temp_t = -1
        self._temp_vi = PhysicsConstants.vi
        self._temp_hit_vi = PhysicsConstants.hit_vi

    def get_fpos(self) -> str:
        """
        returns a the formatted position
        """
        return str(self._pos[0]) + "," + str(self._pos[1]) + "," + str(self._direction)

    def remove_action_by_name(self, given_action: str):
        action = [action for action in self._actions if action[0] == given_action]
        if action:
            self._actions.remove(action[0])
        if self._actions and self._sprite == given_action:
            self._sprite = self._actions[0][0]

    def get_action_by_name(self, given_action: str) -> (Constants, float):
        action = [action for action in self._actions if action[0] == given_action]
        if action:
            return action[0]

    def is_action_active(self, given_action):
        if isinstance(given_action, str):
            return bool([action for action in self._actions if action[0] == given_action])
        elif isinstance(given_action, list):
            for act in given_action:
                if self.is_action_active(act):
                    return True
            return False

    def get_factions(self) -> str:
        """
        returns a the formatted factions
        """
        return ','.join([action[0] for action in self._actions])

    def set_action(self, action: str):
        if action == Constants.JUMP and self._actions[0][0] == Constants.IDLE and time.time() > self._next_time_to_jump:
            self._actions.insert(0, (action, time.time()))
            self.remove_action_by_name(Constants.IDLE)
            self._sprite = action
        elif action == Constants.A_PUNCH and time.time() > self._next_time_to_punch and not self.is_action_active(
                Constants.A_PUNCH):
            self.remove_action_by_name(Constants.IDLE)
            self._actions.insert(0, (action, time.time()))
            print(f"inserted {action} to self._actions ", self._actions)
            if self.is_action_active([Constants.JUMP]) or (
                    self.is_action_active([Constants.FALL]) and self._pos[1] < self.START_HEIGHT - 10):
                self._sprite = Constants.A_AIR
                self._punched = (True, 5)
                print("air")
            else:
                self._sprite = Constants.A
                self._punched = (True, 2)
                print("A", self._sprite)

    def can_move(self, to_left: bool):
        if to_left:
            # return self._pos[0] - 2 > 0 and\
            return not self.is_action_active(Constants.FULL_UNMOVABLE) and \
                   ((self.is_action_active(Constants.GROUND_UNMOVABLE) and
                     self.is_action_active([Constants.JUMP, Constants.FALL]))
                    or not self.is_action_active(Constants.GROUND_UNMOVABLE))
        else:
            # return self._pos[0] + 2 < 1280 - 120 and\
            return not self.is_action_active(Constants.FULL_UNMOVABLE) and \
                   ((self.is_action_active(Constants.GROUND_UNMOVABLE) and
                     self.is_action_active([Constants.JUMP, Constants.FALL]))
                    or not self.is_action_active(Constants.GROUND_UNMOVABLE))

    def move(self, to_left: bool):
        if to_left:
            self._direction = "left"
            if self.can_move(to_left):
                self._pos = (self._pos[0] - Constants.MOVING_DISTANCE, self._pos[1])
                if self._actions[0][0] == Constants.IDLE:
                    self._sprite = Constants.MOVE_SPRITE

        else:
            self._direction = "right"
            if self.can_move(to_left):
                self._pos = (self._pos[0] + Constants.MOVING_DISTANCE, self._pos[1])
                if self._actions[0][0] == Constants.IDLE:
                    self._sprite = Constants.MOVE_SPRITE

    def stopped_moving(self):
        if self._sprite == Constants.MOVE_SPRITE:
            self._sprite = Constants.IDLE
            self._actions = [(Constants.IDLE, time.time())]

    def update(self):
        stopped_falling = True
        if self.is_action_active(Constants.JUMP):
            if self._temp_t == -1:
                self._temp_t = self.get_action_by_name(Constants.JUMP)[1]
            deltaT = time.time() - self._temp_t
            d = get_d(vi=self._temp_vi, t=deltaT, a=PhysicsConstants.ag)
            self._temp_vi = get_vf(vi=self._temp_vi, t=deltaT, a=PhysicsConstants.ag)
            if self._temp_vi >= 0:
                # print("VI", self._temp_vi)
                # print("D", d)
                print("T", deltaT)
                # self._pos = (self._pos[0], int(self.START_HEIGHT - d))
                self._pos = (self._pos[0], int(self._pos[1] - d))
                self._temp_t = time.time()
            else:
                print("AG", PhysicsConstants.ag)
                # self._temp_vi = PhysicsConstants.vi
                self._temp_t = -1
                self._temp_vi = 0
                self.remove_action_by_name(Constants.JUMP)
                self._actions.append((Constants.FALL, time.time()))
                self._sprite = Constants.FALL

        if self.is_action_active(Constants.FALL):
            if self._temp_t == -1:
                self._temp_t = self.get_action_by_name(Constants.FALL)[1]
            deltaT = time.time() - self._temp_t
            d = get_d(vi=self._temp_vi, t=deltaT, a=PhysicsConstants.ag * 2)
            self._temp_vi = get_vf(vi=self._temp_vi, t=deltaT, a=PhysicsConstants.ag * 2)
            if abs(self._pos[1] - d) < self.START_HEIGHT:
                self._pos = (self._pos[0], int(self._pos[1] - d))
                self._temp_t = time.time()
                stopped_falling = False
            else:
                self._temp_vi = PhysicsConstants.vi
                self.remove_action_by_name(Constants.FALL)
                self._temp_t = -1
                if not self._actions:
                    self._actions = [(Constants.IDLE, time.time())]
                    self._sprite = Constants.IDLE
                    self._next_time_to_jump = time.time() + Constants.JUMP_PUNCH_RATE

        if self.is_action_active(Constants.A_PUNCH):
            if time.time() > [action for action in self._actions if action[0] == Constants.A_PUNCH][0][1] + 0.55:
                print(self._actions)
                self.remove_action_by_name(Constants.A_PUNCH)
                if not self._actions:
                    self._actions = [(Constants.IDLE, time.time())]
                    self._sprite = Constants.IDLE
                    self._next_time_to_punch = time.time() + Constants.JUMP_PUNCH_RATE
                else:
                    print(self._actions)
                    print(self._sprite)

        if self.is_action_active(Constants.BEEN_HIT):
            if self._temp_t == -1:
                self._temp_t = self.get_action_by_name(Constants.BEEN_HIT)[1]
            deltaT = time.time() - self._temp_t
            Xd = get_d(vi=self._temp_hit_vi + self._percentage, t=deltaT, a=PhysicsConstants.hit_a)
            self._temp_hit_vi = get_vf(vi=self._temp_hit_vi + self._percentage / 2, t=deltaT, a=PhysicsConstants.hit_a)

            Yd = get_d(vi=self._temp_vi * (self._percentage / 50), t=deltaT, a=PhysicsConstants.ag)
            self._temp_vi = get_vf(vi=self._temp_vi + (self._percentage / 50), t=deltaT, a=PhysicsConstants.ag)
            Yd = int(self._pos[1] - Yd) if Yd > 0 else int(self._pos[1] - abs(Yd) / 100)
            if Xd > 0:
                Xd *= self._hit_side_multiplier
                # self._pos = (int(self._pos[0] + d), self._pos[1])
                self._pos = (int(self._pos[0] + Xd), Yd)
            else:
                self._temp_t = -1
                self._temp_vi = 0
                self.remove_action_by_name(Constants.BEEN_HIT)
                self._actions.append((Constants.FALL, time.time()))
                self._sprite = Constants.FALL
                print("oh ive been hit")

        if not self.is_action_active([Constants.FALL, Constants.JUMP]) and self._pos[1] < self.START_HEIGHT:
            if stopped_falling:
                self.set_action(Constants.FALL)
            else:
                self._pos = (self._pos[0], self.START_HEIGHT)
        if not self.is_action_active([Constants.FALL, Constants.JUMP]) and self._pos[1] > self.START_HEIGHT:
            self._pos = (self._pos[0], self.START_HEIGHT)
