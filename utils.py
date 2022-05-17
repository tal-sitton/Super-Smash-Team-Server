from math import sqrt


def distance_between_point(xy1: [int, int], xy2: [int, int]):
    x1, y1 = xy1
    x2, y2 = xy2
    return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def clamp(min_num, num, max_num):
    return min(max(num, min_num), max_num)


