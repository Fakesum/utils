from .poll import *
from .gui import *
from .datatypes import *

import typing as __typing

# Time the executing of a function
# And return a tuple with the Return
# value and the time taken to execute
def timeit(f: __typing.Callable) -> __typing.Callable:
    """Get the time taken by a function to execute

    Args:
        f (__typing.Callable): decorator Function

    Returns:
        __typing.Callable: decorated function
    """
    def wrapper(*args, **kwargs) -> tuple[__typing.Any, float]:
        import time
        st: float = time.time()
        return (f(*args, **kwargs), round(time.time() - st, 2))
    return wrapper

# Get the commandline output of the given command
def exec_cmd(cmd: str) -> tuple[str, str]:
    """Run a Command and Get the command line output

    Args:
        cmd (str): command given

    Returns:
        tuple[str, str]: command line output of the command
    """
    import subprocess
    proc: subprocess.Popen[bytes] = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    out, err = str(out), str(err)
    return (out, err)

def ignore_error(f: __typing.Callable) -> __typing.Any:
    """Don't do anything in case of error

    Args:
        f (__typing.Callable): _description_
    """
    try:
        return f()
    except:
        pass

# XOR Gate:
def xor(*orands) -> bool:
    """XOR Gate with truth table(for two imputs):
        # 1 1 -> 0
        # 0 1 -> 1
        # 1 0 -> 1
        # 0 0 -> 0
    
    Args: <Any Number of bools>

    Returns:
        bool: Output
    """
    return sum(bool(x) for x in orands) == 1

# NAND Gate:
def nand (a: bool, b: bool) -> bool:
    """A Nand Gate with 
        # 1 1 -> 0
        # 0 1 -> 1
        # 1 0 -> 1
        # 0 0 -> 1
    Truth Table

    Args:
        a (bool): First Input
        b (bool): Second Input

    Returns:
        bool: Output
    """
    return (False if (a == 1 and b == 1) else True)

# Symantic Sugar cotting for filter function in
# python, allows for @wrap_filter, where now
# all the args must be given as lists
def wrap_filter(f: __typing.Callable) -> __typing.Callable:
    """decorator for a function allowing automatic
    filtering of a list given as a single argument
    (Can be a string or list or dict) and a common
    variable which is also given to the function.

    Args:
        f (__typing.Callable): The Function the decorator
        is acting on

    Returns:
        __typing.Callable: The decorated function
    """
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
def wrap_assert(val: __typing.Any) -> __typing.Callable:
    """decorator for asserting the return val of a function

    Args:
        val (__typing.Any): The expected value of function asserted
    """
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
def hearsay(logger: __typing.Callable, value: __typing.Any, fmt: str= "") -> __typing.Any:
    """This function takes any value, formats and logs it
    using the given function before returning the val back

    Args:
        logger (__typing.Callable): the logging function given to the function
        value (__typing.Any): the value given to and will be returned by the function
        fmt (str, optional): the formating that the value has to undergo before logging
        . Defaults to "".

    Returns:
        __typing.Any: _description_
    """
    logger(fmt.format(value))
    return value

def compare(a: str,b: str) -> float:
    """This function takes two strings and returns the
    percentage they are similar to each other

    Args:
        a (str): one string
        b (str): another string

    Returns:
        float: the percentage of similarity between them
    """
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
    """Find a Free Port on the device

    Returns:
        int: A free port
    """
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