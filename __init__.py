from .poll import *

def timeit(f):
    def wrapper(*args, **kwargs):
        import time
        st = time.time()
        return [f(*args, **kwargs), time.time() - st]
    return wrapper

def exec(cmd):
    import subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)

def nand (a, b):
    return (False if (a == 1 and b == 1) else True)

class Dummy:
    def __init__(self, _key) -> None:
        self.key = _key

    def __eq__(self, other):
        return self.key == other.key

