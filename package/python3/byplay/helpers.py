import os


def join(*args):
    return os.path.join(*args).replace("\\", "/")
