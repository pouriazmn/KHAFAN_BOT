
def add(dic, key, value):
    dic[key] = value


class Node(object):
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0

    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

    def __str__(self):
        return f"({self.x}, {self.y})"

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

    def calc_h(self, position):
        if self.position is not None:
            dx = abs(position[0] - self.position[0])
            dy = abs(position[1] - self.position[1])

            self.h = dx + dy

    def calc_g(self):
        if self.parent is None:
            self.g = 0
        else:
            self.g = 1 + self.parent.g


def A_Star_Search(maze, start, end, dont_visit):
    # print(maze)
    start_node = Node(None, start)
    end_node = Node(None, end)

    if start == end:
        return start

    start_node.calc_h(end_node.position)
    start_node.calc_g()

    move = [[-1, 0],
            [0, -1],
            [1, 0],
            [0, 1]]

    to_visit = list()
    visited = list()
    to_visit.append(start_node)

    while len(to_visit) > 0:
        next_node = to_visit[0]
        next_node_index = 0
        f_next_node = next_node.h + next_node.g
        for ind, each in enumerate(to_visit[1:], start=1):
            if each.h + each.g < f_next_node:
                next_node_index = ind
                next_node = each
                f_next_node = next_node.h + next_node.g

        # print("F is => {} , Min value index: {}".format(dic, min(dic.keys(), key=(lambda k: dic[k]))))

        current_node = to_visit.pop(next_node_index)
        visited.append(current_node)
        # print('current node pos ====> {}'.format(current_node.position))
        if end_node == current_node:
            path = []
            while current_node.parent:
                path.append(current_node)
                current_node = current_node.parent
            return path[::-1]

        for m in move:
            next_pos = (current_node.x + m[0],
                        current_node.y + m[1])
            if next_pos[0] < 0 or next_pos[0] >= len(maze) \
                    or next_pos[1] < 0 or next_pos[1] >= len(maze):
                continue
            if maze[next_pos[0]][next_pos[1]] not in dont_visit:
                node = Node(current_node, next_pos)
                if node in visited or node in to_visit:
                    # print(f"duplicate: {node.position}")
                    continue
                # print(f"adding to A* queue: {node.position}")
                node.calc_h(end_node.position)
                node.calc_g()
                to_visit.append(node)
