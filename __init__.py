from .poll import *
import typing as __typing

# Time the executing of a function
# And return a tuple with the Return
# value and the time taken to execute
def timeit(f) -> __typing.Callable:
    def wrapper(*args, **kwargs) -> tuple[__typing.Any, float]:
        import time
        st: float = time.time()
        return (f(*args, **kwargs), time.time() - st)
    return wrapper

# Get the commandline output of the given command
def exec(cmd) -> tuple[bytes, bytes]:
    import subprocess
    proc: subprocess.Popen[bytes] = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)

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
def nand (a, b) -> bool:
    return (False if (a == 1 and b == 1) else True)
