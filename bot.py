import itertools
import socket
import struct
from enum import Enum
import a_star


class Directions(Enum):
    UP, DOWN, LEFT, RIGHT = 'UP', 'DOWN', 'LEFT', 'RIGHT'


class Fruits(Enum):
    Orange, Banana, Cherry, WaterMelon, Apple = 'O', 'B', 'C', 'W', 'A'


class AI:

    def __init__(self, bot_id, bot_count, board_size):
        self.__bot_id, self.__bot_count, self.__board_size = bot_id, bot_count, board_size
        self.bot_fruits, self.board, self.fruits, = None, None, None
        self.eaten = dict()
        self.must_eat = dict()
        self.init_eaten()
        self.fruit_positions = dict()
        self.x, self.y = 0, 0

    def init_eaten(self):
        for each in list(Fruits):
            self.eaten[each] = 0

        self.must_eat[Fruits.Orange] = 2
        self.must_eat[Fruits.Apple] = 2
        self.must_eat[Fruits.WaterMelon] = 1
        self.must_eat[Fruits.Banana] = 1
        self.must_eat[Fruits.Cherry] = 1

    def do_turn(self, board, bot_fruits):
        # write your bot's logic here
        self.board = board
        self.bot_fruits = [None for _ in range(self.__bot_count)]
        for each in bot_fruits:
            self.bot_fruits.insert(int(each[0]), each[1:] if len(each) > 1 else [])
        self.fruits = self.bot_fruits[self.__bot_id]
        self.find_fruits()
        self.set_eaten()
        #print(f"Eaten list --> {self.eaten}")
        self.get_position()
        return self.best_action()

    def best_action(self):
        f_order = self.fruit_order()
        print(f"Fruit order --> {f_order}")
        min_path = None
        min_path_len = float('+inf')
        check, district = "", '*'
        for f, w in f_order:
            if w > 0:
                check += f
            else:
                district += f
        print(f"district: {district}")
        print(f"check: {check}")
        for f in check:
            min_path_f = None
            min_path_len_f = float('+inf')
            for pos in self.fruit_positions[f]:
                path = a_star.A_Star_Search(self.board, (self.x, self.y), pos, district)
                if path is not None and len(path) < min_path_len_f:
                    min_path_f = path
                    min_path_len_f = len(path)
            if min_path_len_f < min_path_len:
                min_path_len = min_path_len_f
                min_path = min_path_f

        print(f'({self.x}, {self.y}) -> {min_path[0]}')
        ac = self.get_action(min_path[0])
        print(ac)
        return ac

    def get_action(self, pos):
        if pos.x - self.x == 1:
            return Directions.DOWN
        elif pos.x - self.x == -1:
            return Directions.UP
        elif pos.y - self.y == 1:
            return Directions.RIGHT
        elif pos.y - self.y == -1:
            return Directions.LEFT
        else:
            print(f'Not suportet pos --> {pos} for current {self.x, self.y}')

    def find_fruits(self):
        for f in 'OABCW':
            self.fruit_positions[f] = list()
        for x, y in itertools.product(range(self.__board_size), range(self.__board_size)):
            if self.board[x][y] in 'OABCW':
                self.fruit_positions[self.board[x][y]].append((x, y))

        """for key, value in self.fruit_positions.items():
            print(key, ', '.join(map(str, value)), sep=':\t')"""

    def get_position(self):
        for x, row in enumerate(self.board):
            y = row.find(str(self.__bot_id))
            if y >= 0:
                self.x, self.y = x, y

    def set_eaten(self):
        print("this bot fruits: ", self.fruits)
        for each in list(Fruits):
            self.eaten[each] = 0
        for each in self.fruits:
            if each == Fruits.Orange.value:
                self.eaten[Fruits.Orange] += 1
            elif each == Fruits.Apple.value:
                self.eaten[Fruits.Apple] += 1
            elif each == Fruits.Banana.value:
                self.eaten[Fruits.Banana] += 1
            elif each == Fruits.Cherry.value:
                self.eaten[Fruits.Cherry] += 1
            elif each == Fruits.WaterMelon.value:
                self.eaten[Fruits.WaterMelon] += 1
            else:
                print(each)
                raise Exception

    def set_must_eat(self):
        self.must_eat[Fruits.Orange] = max(self.must_eat[Fruits.Orange] - self.eaten[Fruits.Orange],
                                           self.eaten[Fruits.Banana] * 2 - self.eaten[Fruits.Orange])
        self.must_eat[Fruits.Apple] = max(self.must_eat[Fruits.Apple] - self.eaten[Fruits.Apple],
                                          self.eaten[Fruits.Cherry] + self.eaten[Fruits.WaterMelon] - self.eaten[
                                              Fruits.Apple])
        self.must_eat[Fruits.WaterMelon] = self.must_eat[Fruits.WaterMelon] - self.eaten[Fruits.WaterMelon]
        self.must_eat[Fruits.Cherry] = self.must_eat[Fruits.Cherry] - self.eaten[Fruits.Cherry]
        self.must_eat[Fruits.Banana] = self.must_eat[Fruits.Banana] - self.eaten[Fruits.Banana]

    def fruit_order(self):
        self.set_must_eat()
        return list(map(lambda x: (getattr(x, 'value'), self.must_eat[x]),
                        sorted(list(Fruits), key=lambda x: self.must_eat[x])))


def read_utf(sock: socket.socket):
    length = struct.unpack('>H', s.recv(2))[0]
    return sock.recv(length).decode('utf-8')


def write_utf(sock: socket.socket, msg: str):
    sock.send(struct.pack('>H', len(msg)))
    sock.send(msg.encode('utf-8'))


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 9898))
    init_data = read_utf(s)
    bot_id, bot_count, board_size, max_turns = map(int, init_data.split(','))
    print(bot_id, bot_count, board_size)
    ai = AI(bot_id, bot_count, board_size)
    while True:
        board_str = read_utf(s)
        if board_str.startswith("WINNER"):
            print(board_str)
            break
        board = [board_str[i * board_size:(i + 1) * board_size] for i in range(board_size)]
        #print('\n'.join(board), end='\n-------------------------\n')
        fruits = [read_utf(s) for _ in range(bot_count)]
        write_utf(s, ai.do_turn(board, fruits).value)
