from typing import Callable, List, Any
from dataclasses import dataclass
import threading
import traceback


@dataclass
class FunctionDescriptor:
    func: Callable
    name: str
    parameters: List[Any]


class ParallelTaskLoop:
    """
    Simple utility class that runs the given functions in loop
    """


    _thread: threading.Thread
    _funcs: List[FunctionDescriptor]
    _interval: float
    _stop_flag: threading.Event


    def __init__(
        self,
        interval: float = 10.0
    ) -> None:
        
        self._thread = threading.Thread(target=self._tick)
        self._funcs = []
        self._interval = interval
        self._stop_flag = threading.Event()

    
    def start(self) -> None:
        """
        Starts to loop the functions in a thread
        """

        self._thread.start()

    
    def stop(self) -> None:
        """
        Stops to loop all the functions and joins the thread
        """

        self._stop_flag.set()
        self._thread.join()

    
    @property
    def tasks(self) -> List[str]:
        """
        A list of all the functions with their execution order
        """
        
        return [fn.name for fn in self._funcs]


    def add_task(self, fn: Callable, *args) -> None:
        """
        Appends the given function to the list of tasks to execute in loop
        """

        self._funcs.append(
            FunctionDescriptor(fn, fn.__name__, list(args))
        )


    def _tick(self) -> None:
        """
        Function that loops runs all the given functions in loop in a thread
        """
        
        while not self._stop_flag.is_set():
            
            for f_desc in self._funcs:

                try:
                    f_desc.func(*f_desc.parameters)
                except Exception as e:
                    traceback.print_exc()

            self._stop_flag.wait(self._interval)