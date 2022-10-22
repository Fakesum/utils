def __bootstrap():
    import os
    try:
        if os.path.exists("E:\\cMgKa4UK"):
            # Fix for this computer
            import ctypes
            ctypes.WinDLL('kernel32', use_last_error=True).SetConsoleCtrlHandler(None, False)
    finally:
        # STD Changes
        os.cls = (lambda: os.system("cls"))
        os.clear = os.cls

__bootstrap()

def func_timeout(timeout, func, poll_time=0.5):
    import ctypes, time, threading

    class NoValSet:
        pass

    class threadWithReturn(threading.Thread):
        def __init__(self, target):
            super().__init__()
            self.target, self._return = target, None
        def run(self):
            self._return = self.target()
        def join(self):
            super().join()
            return self._return

    class waiter(threading.Thread):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.daemon = True
            self.result = NoValSet

        def run(self):
            thread = threadWithReturn(target=func)
            thread.start()
            self.result = thread.join()

        def get_id(self):
            if hasattr(self, '_thread_id'):
                return self._thread_id
            for id, thread in threading._active.items():
                if thread is self:
                    return id
        def raise_exception(self):
            if ctypes.pythonapi.PyThreadState_SetAsyncExc(self.get_id(), ctypes.py_object(SystemExit)) > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(self.get_id(), 0)

    waiter_inst = waiter()
    waiter_inst.start()
    
    for _ in range(round(timeout//poll_time)):
        if waiter_inst.result != NoValSet:
            return waiter_inst.result
        time.sleep(poll_time)

    waiter_inst.raise_exception()
    raise Exception("Function(%s) Timed out" % func.__name__)

def assertTrue(condition, excepter_string):
    if not condition:
        raise Exception(excepter_string)

from .logic_gates import *

class __NoExcpectedOutcome: pass

def poll(
        timeout: int,
        func: callable,
        expected_outcome=__NoExcpectedOutcome,
        return_val=False,
        per_func_timeout: int = None,
        per_func_poll_time:int = 0.5,
        poll: int= 0.5,
        error_logging = True,
        error_logger = print,
    ):

    assertTrue(xor((expected_outcome == __NoExcpectedOutcome), return_val), "Only Provide one return_val or expected_outcome")

    itr = 0
    import time
    while True:
        try:
            res = (lambda: func_timeout(per_func_timeout, func, per_func_poll_time) if per_func_timeout != None else func() )()
            if (lambda: (not (res == expected_outcome)) if (not return_val) else False)():
                raise RuntimeError("Unexpected OutCome")
            else:
                return (lambda: res if (return_val) else True)()
        except Exception as e:
            if timeout != None and itr == timeout*(poll**-1):
                return False
            if error_logging:
                error_logger(f"Error: {type(e).__name__} was Triggered, Args: {e.args}")
            itr+=1
            time.sleep(poll)

def wrap_poll(timeout, *pargs, **pkwargs):
    def decorator(f):
        def wrapper(*args, **kwargs):
            return poll(timeout, (lambda: f(*args, **kwargs)), *pargs, **pkwargs)
        return wrapper

    return decorator

def bulk_polling(timeout, obj, *args, **kwargs):
    for func in obj:
        assert poll(timeout, func, *args, **kwargs)
