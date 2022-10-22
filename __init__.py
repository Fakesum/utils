from .poll import *
from .gui import *
from .automation import *

def timeit(f):
    def wrapper(*args, **kwargs):
        import time
        st = time.time()
        return [f(*args, **kwargs), time.time() - st]
    return wrapper
