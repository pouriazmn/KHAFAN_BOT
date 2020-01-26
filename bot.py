import socket
import struct
import random
from enum import Enum


class Directions(Enum):
    UP, DOWN, LEFT, RIGHT = 'UP', 'DOWN', 'LEFT', 'RIGHT'


class AI:

    def __init__(self, bot_id, bot_count, board_size):
        self.__bot_id, self.__bot_count, self.__board_size = bot_id, bot_count, board_size

    def do_turn(self, board, bot_fruits):
        # write your bot's logic here
        return random.choice(list(Directions))


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
    bot_id, bot_count, board_size = map(int, init_data.split(','))
    print(bot_id, bot_count, board_size)
    ai = AI(bot_id, bot_count, board_size)
    while True:
        board_str = read_utf(s)
        board = [board_str[i * board_size:(i + 1) * board_size] for i in range(board_size)]
        fruits = [read_utf(s) for _ in range(bot_count)]
        write_utf(s, ai.do_turn(board, fruits).value)
