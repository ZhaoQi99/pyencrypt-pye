import random


def random_list(length, start=1, end=100):
    return random.sample(range(start, end), length)
