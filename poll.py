def xor(*orands):
    return sum(bool(x) for x in orands) == 1

import threading as __threading
import typing as __typing

class NoValSet: pass

class ThreadWithReturn(__threading.Thread):
    def __init__(self, target) -> None:
        super().__init__()
        self.daemon: bool = True
        self.target, self.result = target, NoValSet

    def run(self) -> None:
        self.result: __typing.Any = self.target()

    def raise_exception(self) -> None:
        import ctypes
        if ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, ctypes.py_object(SystemExit)) > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, 0)


def func_timeout(timeout, func, poll_time=0.5) -> __typing.Any:
    import time

    waiter_inst: ThreadWithReturn = ThreadWithReturn(func)
    waiter_inst.start()
    
    for _ in range(round(timeout//poll_time)):
        if waiter_inst.result != NoValSet:
            return waiter_inst.result
        time.sleep(poll_time)

    waiter_inst.raise_exception()
    raise Exception("Function(%s) Timed out" % func.__name__)

class __NoExcpectedOutcome: pass

def poll(
        timeout: int,
        func,
        expected_outcome: __typing.Type =__NoExcpectedOutcome,
        per_func_poll_time: float = 0.5,
        return_val=False,
        per_func_timeout = None,
        poll:float = 0.5,
        error_logging = True,
        error_logger = print,
    ) -> bool | __typing.Any:

    if (xor((expected_outcome == __NoExcpectedOutcome), return_val)): raise Exception("Only Provide one return_val or expected_outcome")

    itr: int = 0
    import time
    while True:
        try:
            res = (lambda: func_timeout(per_func_timeout, func, per_func_poll_time) if per_func_timeout != None else func() )()

            if (lambda: (not (res == expected_outcome)) if (not return_val) else False)():
                raise RuntimeError("Unexpected OutCome")
            else:
                return (lambda: res if (return_val) else True)()
        except Exception as e:
            if (timeout != None) and (itr == (timeout/poll)):
                return False
            if error_logging:
                error_logger(f"Error: {type(e).__name__} was Triggered, Args: {e.args}")
            itr+=1
            time.sleep(poll)

def wrap_func_timeout(timeout) -> __typing.Callable:
    def decorator(f) -> __typing.Callable:
        def wrapper(*args, **kwargs):
            return func_timeout(timeout, (lambda: f(*args, **kwargs)))
        return wrapper
    return decorator

def wrap_poll(timeout, *pargs, **pkwargs) -> __typing.Callable: 
    def decorator(f) -> __typing.Callable:
        def wrapper(*args, **kwargs) -> (bool | __typing.Any):
            return poll(timeout, (lambda: f(*args, **kwargs)), *pargs, **pkwargs)
        return wrapper

    return decorator

def bulk_polling(timeout, obj, *args, **kwargs) -> None:
    for func in obj:
        assert poll(timeout, func, *args, **kwargs)
