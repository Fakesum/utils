from .poll import *
from .gui import *
from .datatypes import *

import typing as __typing

# Time the executing of a function
# And return a tuple with the Return
# value and the time taken to execute
def timeit(f) -> __typing.Callable:
    def wrapper(*args, **kwargs) -> tuple[__typing.Any, float]:
        import time
        st: float = time.time()
        return (f(*args, **kwargs), round(time.time() - st, 2))
    return wrapper

# Get the commandline output of the given command
def exec_cmd(cmd) -> tuple[str, str]:
    import subprocess
    proc: subprocess.Popen[bytes] = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    out, err = str(out), str(err)
    return (out, err)

def ignore_error(f):
    try:
        f()
    except:
        pass

# XOR Gate:
# 1 1 -> 0
# 0 1 -> 1
# 1 0 -> 1
# 0 0 -> 0
def xor(*orands):
    return sum(bool(x) for x in orands) == 1

# NAND Gate:
# 1 1 -> 0
# 0 1 -> 1
# 1 0 -> 1
# 0 0 -> 1
def nand (a: bool, b: bool) -> bool:
    return (False if (a == 1 and b == 1) else True)

# make the dict printing look pretty
def pretty_print(a: dict)->None:
    import json
    print(json.dumps(a, indent=4))

# Symantic Sugar cotting for filter function in
# python, allows for @wrap_filter, where now
# all the args must be given as lists
def wrap_filter(f):
    class NoValSet: pass
    def wrapper(args, common: __typing.Any=NoValSet):
        res = []
        for arg in args:
            _res = (f(arg) if common == NoValSet else f(arg, common))
            if _res != None: res.append(_res)
        return res
    return wrapper

# wraping asserting with function, checks the
# results of a function with assert before
# either returing or throwing a error
def wrap_assert(val):
    def decorator(f):
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            assert res == val
            return res
        return wrapper
    return decorator

# Hear(log) and then say(return) 
# the same value, useful for in
# -line logging
def hearsay(logger, fmt, value) -> __typing.Any:
    logger(fmt.format(value))
    return value

def compare(a: str,b: str) -> float:
    a = a.strip().lower().split(" ")[0]
    b = b.strip().lower().split(" ")[0]

    res = 0.0
    for lchr in max([a, b]):
        for schr in min([a, b]):
            if lchr == schr:
                res += (1/len(max([a,b])))
    return res

# find a free port
def find_free_port() -> int:
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

# Get a SPeaker Function that just logs out the next
# Line from where it is called
def get_speaker(logger, _format):
    import inspect
    def speak():
        logger(_format.format(open(str(inspect.stack()[1][0]).split(",")[1].split("'")[1], "r").readlines()[inspect.stack()[1][0].f_lineno].split("\t")[-1]).split("\n")[0].split("  ")[-1])
    return speak