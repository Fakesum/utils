
# Import with __ at the start to denote internals
# threading for func_timeout and general typing
import threading as __threading
import multiprocessing as __mp
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
        self.e = None

    def run(self) -> None:
        # self.return here is the part that
        # is accessable for both main thread
        # And Running thread
        try:
            self.result: __typing.Any = self.target()
        except Exception as e:
            self.result = None
            self.e = e

    def is_finished(self) -> None:
        # Check if result is defiend
        return self.result != globals()["__NoValSet"]

    def raise_exception(self) -> None:
        # A very crude way to stop a thread form the outside
        # by raising a SystemExit Exception no matter where it is
        import ctypes
        if ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, ctypes.py_object(SystemExit)) > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, 0)

class ProcessWithReturn(__mp.Process):
    def __init__(self, target):
        self.target, self.result = target, globals()["__NoValSet"]
        self.done = False

    def run(self) -> None:
        self.result = self.target()
        self.done = True

    def raise_exception(self) -> None:
        import ctypes
        if ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, ctypes.py_object(SystemExit)) > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, 0)


class FuncTimeout(Exception): pass

def func_timeout(timeout: int | float, func: __typing.Callable, poll_time: float=0.5) -> __typing.Any:
    """
        function: func_timeout(timeout: int | float, func: __typing.Callable, poll_time: float=0.5) -> __typing.Any:
            @brief: function to timout if a function takes more than given amount of time.

        description:
            A timeout function which checks if a function has finished executing every for every set
            Duration of time ,(by defult every 0.5 seconds) if the function has not finished by the set
            timeout period then the execution function will be terminated and it will raise an Exception
            
            otherwise the function will ruturn the result of the given function
    """
    import time

    waiter_inst: ThreadWithReturn = ThreadWithReturn(func)
    waiter_inst.start()
    
    for _ in range(round(timeout//poll_time)):
        if waiter_inst.result != __NoValSet:
            if waiter_inst.e != None:
                raise waiter_inst.e
            return waiter_inst.result
        time.sleep(poll_time)

    waiter_inst.raise_exception()
    raise FuncTimeout("Function(%s) Timed out" % func.__name__)

def poll(
        timeout: int | float | None, 
        func: __typing.Callable,
        expected_outcome: __typing.Type | __typing.Any=__NoValSet,
        validity_determiner: __typing.Type | __typing.Callable = __NoValSet,
        per_func_poll_time: int | float = 0.5,
        return_val: bool=False,
        per_func_timeout: int | float | None = None,
        poll: int | float | None= 0.5,
        error_logging: bool = True,
        error_logger: __typing.Callable = print,
        true_timing: bool=False,
        fast: bool = False,
        generator: bool = False,
        on_failer: __typing.Callable | __typing.Type = __NoValSet
    ) -> bool | __typing.Any:
    """This function does too many things to explain, Just understand that this is
        By far the best method of adding reliability and speed to the code. specially
        for selenium for which this was created. use @wrap_poll decorator if you want
        something much netter.

    Args:
        timeout (int | float | None): The Timeout of the function
        func (__typing.Callable): The function that is to be repeated
        expected_outcome (__typing.Type | __typing.Any, optional): the expected outcome if there is one. Defaults to __NoValSet.

        validity_determiner(__typing.Type | __typing.Callable, optional): funciton, if specified the output of the given function will be run 
        throw the validity function specified in order to verify that the result was valid. The validity function must return either True or False 
        for  valid and invalid result respectivly.

        per_func_poll_time (int | float, optional): if per_func_timeout is set then this will check on if the function has
                                                    completed every this many seconds. Defaults to 0.5.
        return_val (bool, optional): if this is set then the function will return the result of the function. Defaults to 
                                     False.
        per_func_timeout (int | float | None, optional): this will run the function in a func_timeout in order to not allow
                                                         Each individual function call to not exceed the given amount of time
                                                         . Defaults to None.
        poll (int | float | None, optional): The amount of time between each attempt. Defaults to 0.5.
        error_logging (bool, optional): this will print the error if the passed function has raised one. Defaults to True.
        error_logger (__typing.Callable, optional): The function which is to be run to log the error. Defaults to print.
        true_timing (bool, optional): by defualt it does not take the time taken by the function into a account when
                                      calculating timeout, this uses func_timeout in order to more accurately measure
                                      that. Defaults to False.
        fast (bool, optional): the poll function works in O(1) time with a constant overhead, this will reduce that from
                               ~8 * 10^-5 seconds to ~4 * 10^-7. this is such a small difference that it only matters when
                               dealing with tiny passed functions. **the poll function will Not check for any mistakes if this
                               is True**. Defaults to False.
        generator (bool, optional): if the passed function yields then it might be a good idea to pass this argument as True
                                    since it pre-gens the function and checks for Exceptions before returning the returned val
                                    Defaults to False.
        on_failer (__typing.Callbale): If defined, it runs when the function incounters a problem. Defaults to (lambda: __NoValSet)

    Raises:
        SyntaxError: Timout Must be higher than poll
        SyntaxError: Only Provide one return_val or expected_outcome
        SyntaxError: The Timeout cannot be None when true_timing is specified
        SyntaxError: The per_func_timeout cannot be specified with the true_timing argument.

    Returns:
        bool | __typing.Any: either return False if failed, True if expected outcome or the return value if the return_val argument.
    """

    if not fast:
        # if the poll and timrout are specified check that the timeout is more than the poll
        # time otherwise it will wait for more than the timeout allows for
        if (poll != None) and (timeout != None) and (timeout < poll): raise SyntaxError("Timout Must be higher than poll")

        # Check that only one of the expected_outcome or return_val is provided
        if not (__xor((expected_outcome != __NoValSet), return_val, (validity_determiner != __NoValSet))): raise SyntaxError("Only Provide one return_val or expected_outcome or validity_determiner")
        
        # The True timing and pre_func_timeout cannot be given at once
        if (true_timing and (timeout == None)): raise SyntaxError("The Timeout cannot be None when true_timing is specified")
        if (true_timing and per_func_timeout != None): raise SyntaxError("The per_func_timeout cannot be specified with the true_timing argument.")

    """
    if timeout is None run forever, else if poll is None then run for timeout, if both
    are given the run for timeout//poll
    """
    import time, itertools
    for _ in ((range(int(timeout//poll)) if (poll != None) else range(timeout)) if (timeout != None) else (itertools.count(start=1))):
        try:
            if (generator):
                res = [i for i in ((func_timeout(per_func_timeout, func, per_func_poll_time) if per_func_timeout != None else func()) if not true_timing else __timeit(lambda: (func_timeout(timeout, func, per_func_poll_time)))())]
            else:
                res = ((func_timeout(per_func_timeout, func, per_func_poll_time) if per_func_timeout != None else func()) if not true_timing else __timeit(lambda: (func_timeout(timeout, func, per_func_poll_time)))())
            
            timeout = (timeout if not true_timing else timeout - res[1])

            if ((((res[0] if true_timing else res) != expected_outcome)) if (validity_determiner == __NoValSet) else (validity_determiner(res[0] if true_timing else res) != True)) if (not return_val) else False:
                raise RuntimeError("Unexpected OutCome")
            else:
                return ((res[0] if true_timing else res) if (return_val or validity_determiner != __NoValSet) else True)
        except FuncTimeout as e:
            if error_logging:
                error_logger(f"Error: {type(e).__name__} was Triggered, Args: {e.args}")
            
            if true_timing:
                return False
            else:
                on_failer()
                (time.sleep(poll) if poll != None else None)
        except Exception as e:
            if error_logging:
                error_logger(f"Error: {type(e).__name__} was Triggered, Args: {e.args}")
            on_failer()
            (time.sleep(poll) if poll != None else None)
    return False

def wrap_func_timeout(timeout) -> __typing.Callable:
    def decorator(f) -> __typing.Callable:
        def wrapper(*args, **kwargs):
            return func_timeout(timeout, (lambda: f(*args, **kwargs)))
        return wrapper
    return decorator

def wrap_poll(
        timeout: int | float | None, 
        expected_outcome: __typing.Type | __typing.Any=__NoValSet,
        validity_determiner: __typing.Type | __typing.Callable = __NoValSet,
        per_func_poll_time: int | float = 0.5,
        return_val: bool=False,
        per_func_timeout: int | float | None = None,
        _poll: int | float | None= 0.5,
        error_logging: bool = True,
        error_logger: __typing.Callable = print,
        true_timing: bool=False,
        fast: bool = False,
        generator: bool = False,
        on_failer: __typing.Callable | __typing.Type = __NoValSet
    ) -> __typing.Callable: 
    """This function does too many things to explain, Just understand that this is
        By far the best method of adding reliability and speed to the code. specially
        for selenium for which this was created. use @wrap_poll decorator if you want
        something much netter.

    Args:
        timeout (int | float | None): The Timeout of the function
        func (__typing.Callable): The function that is to be repeated
        expected_outcome (__typing.Type | __typing.Any, optional): the expected outcome if there is one. Defaults to __NoValSet.

        validity_determiner(__typing.Type | __typing.Callable, optional): funciton, if specified the output of the given function will be run 
        throw the validity function specified in order to verify that the result was valid. The validity function must return either True or False 
        for  valid and invalid result respectivly.

        per_func_poll_time (int | float, optional): if per_func_timeout is set then this will check on if the function has
                                                    completed every this many seconds. Defaults to 0.5.
        return_val (bool, optional): if this is set then the function will return the result of the function. Defaults to 
                                     False.
        per_func_timeout (int | float | None, optional): this will run the function in a func_timeout in order to not allow
                                                         Each individual function call to not exceed the given amount of time
                                                         . Defaults to None.
        poll (int | float | None, optional): The amount of time between each attempt. Defaults to 0.5.
        error_logging (bool, optional): this will print the error if the passed function has raised one. Defaults to True.
        error_logger (__typing.Callable, optional): The function which is to be run to log the error. Defaults to print.
        true_timing (bool, optional): by defualt it does not take the time taken by the function into a account when
                                      calculating timeout, this uses func_timeout in order to more accurately measure
                                      that. Defaults to False.
        fast (bool, optional): the poll function works in O(1) time with a constant overhead, this will reduce that from
                               ~8 * 10^-5 seconds to ~4 * 10^-7. this is such a small difference that it only matters when
                               dealing with tiny passed functions. **the poll function will Not check for any mistakes if this
                               is True**. Defaults to False.
        generator (bool, optional): if the passed function yields then it might be a good idea to pass this argument as True
                                    since it pre-gens the function and checks for Exceptions before returning the returned val
                                    Defaults to False.
        on_failer (__typing.Callbale): If defined, it runs when the function incounters a problem. Defaults to (lambda: __NoValSet)

    Raises:
        SyntaxError: Timout Must be higher than poll
        SyntaxError: Only Provide one return_val or expected_outcome
        SyntaxError: The Timeout cannot be None when true_timing is specified
        SyntaxError: The per_func_timeout cannot be specified with the true_timing argument.

    Returns:
        bool | __typing.Any: either return False if failed, True if expected outcome or the return value if the return_val argument.
    """
    def decorator(f) -> __typing.Callable:
        def wrapper(*args, **kwargs) -> (bool | __typing.Any):
            return poll(
                timeout,
                (lambda: f(*args, **kwargs)),
                expected_outcome,
                validity_determiner,
                per_func_poll_time,
                return_val,
                per_func_timeout,
                _poll,
                error_logging,
                error_logger,
                true_timing,
                fast, 
                generator, 
                on_failer
            ) # Manully funling arguments.
        return wrapper
    return decorator

def bulk_polling(timeout, obj, *args, **kwargs) -> None:
    for func in obj:
        assert poll(timeout, func, *args, **kwargs)
