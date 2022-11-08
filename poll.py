
# Import with __ at the start to denote internals
# threading for func_timeout and general typing
import threading as __threading
import typing as __typing
from .__init__ import timeit as __timeit
from .__init__ import xor as __xor

# A internal None of sorts to diffrentiat the result: None
# and the <no-result given state>
class __NoValSet: pass

# A Stoppable thread with a return val
class ThreadWithReturn(__threading.Thread):
    def __init__(self, target) -> None:
        super().__init__()
        # daemon just in case
        self.daemon: bool = True

        # need to use globals()["__NoValSet"] since it thinks
        # __NoValSet means _ThreadWithReturn__NoValSet due to private
        # variables
        self.target, self.result = target, globals()["__NoValSet"]

    def run(self) -> None:
        # self.return here is the part that
        # is accessable for both main thread
        # And Running thread
        self.result: __typing.Any = self.target()

    def raise_exception(self) -> None:
        # A very crude way to stop a thread form the outside
        # by raising a SystemExit Exception no matter where it is
        import ctypes
        if ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, ctypes.py_object(SystemExit)) > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, 0)

"""
    function: func_timeout(timeout: int | float, func: __typing.Callable, poll_time: float=0.5) -> __typing.Any:
        @brief: function to timout if a function takes more than given amount of time.

    description:
        A timeout function which checks if a function has finished executing every for every set
        Duration of time ,(by defult every 0.5 seconds) if the function has not finished by the set
        timeout period then the execution function will be terminated and it will raise an Exception
        
        otherwise the function will ruturn the result of the given function
"""
def func_timeout(timeout: int | float, func: __typing.Callable, poll_time: float=0.5) -> __typing.Any:
    import time

    waiter_inst: ThreadWithReturn = ThreadWithReturn(func)
    waiter_inst.start()
    
    for _ in range(round(timeout//poll_time)):
        if waiter_inst.result != __NoValSet:
            return waiter_inst.result
        time.sleep(poll_time)

    waiter_inst.raise_exception()
    raise Exception("Function(%s) Timed out" % func.__name__)

"""
    function: def poll(
                    timeout: int,
                    func: __typing.Callable,
                    expected_outcome: __typing.Type =__NoValSet,
                    per_func_poll_time: int | float = 0.5,
                    return_val: bool=False,
                    per_func_timeout: int | float | None = None,
                    poll:float | int = 0.5,
                    error_logging: bool = True,
                    error_logger: __typing.Callable = print,
                ) -> bool | __typing.Any:
        @brief overcomplex polling function that will run a given function every given amount of time

    description: 
        A polling function that will run a given function every given amount of time. The timeout
        argument can be either None and a number, if it is None then the poll function will keep
        running the given function until there are no errors. If the timeout argument is specified
        then it will try for timeout/poll number for times if poll is defined otherwise it will
        try for timeout number of times.

        If the expected_outcome is specified the the function will run the function until either the
        timeout runs out or until the function returns the expected_outcome, if the timeout is reached
        the poll function will return False.

        If the return_val argument is specified then the poll function will return the value of the given
        function. please note that the function will still return False if the timeout has run out. Only
        one, either return_val or expected_outcome must be defined if both are defined the poll function
        will return an error. It will also raise a Exception if neither are given.

        the function argument can either be a lambda or a function through the wrap_poll function which
        inputs the function argument as the decorated function. if the per_func_timeout argument is not
        None then the function will be run with func_timeout() with the specified amount of time given

        you can specify error logger by the error_logger argumment and if the error should be logged. can
        be specified by the error_logging argument.
"""
def poll(
        timeout, # TODO: type hinting
        func: __typing.Callable,
        expected_outcome: __typing.Type =__NoValSet,
        per_func_poll_time: int | float = 0.5,
        return_val: bool=False,
        per_func_timeout: int | float | None = None,
        poll= 0.5, #TODO: type hinting
        error_logging: bool = True,
        error_logger: __typing.Callable = print,
    ) -> bool | __typing.Any:

    # if the poll and timrout are specified check that the timeout is more than the poll
    # time otherwise it will wait for more than the timeout allows for
    if (poll != None) and (timeout != None) and (timeout < poll): raise Exception("Timout Must be higher than poll")

    # Check that only one of the expected_outcome or return_val is provided
    if (__xor((expected_outcome == __NoValSet), return_val)): raise Exception("Only Provide one return_val or expected_outcome")

    """
    if timeout is None run forever, else if poll is None then run for timeout, if both
    are given the run for timeout//poll
    """
    import time, itertools
    for _ in ((range(timeout//poll) if (poll != None) else range(timeout)) if (timeout != None) else (itertools.count(start=1))):
        try:
            # Run the function as specified
            res = (func_timeout(per_func_timeout, func, per_func_poll_time) if per_func_timeout != None else func())

            if (lambda: (not (res == expected_outcome)) if (not return_val) else False)():
                raise RuntimeError("Unexpected OutCome")
            else:
                return (res if (return_val) else True)
        except Exception as e:
            if error_logging:
                error_logger(f"Error: {type(e).__name__} was Triggered, Args: {e.args}")
            (time.sleep(poll) if poll != None else None)

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
