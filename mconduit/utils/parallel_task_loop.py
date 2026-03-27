from typing import Callable, List, Any
from dataclasses import dataclass
import threading
import traceback
import time


@dataclass
class FunctionDescriptor:
    func: Callable
    name: str
    parameters: List[Any]


class ParallelTaskLoop:
    """
    Simple utility class that runs the given functions in loop
    """


    __thread: threading.Thread
    __funcs: List[FunctionDescriptor]
    __interval: int
    __stop_flag: bool


    def __init__(
        self,
        interval: int = 10
    ) -> None:
        
        self.__thread = threading.Thread(target=self.__tick)
        self.__funcs = []
        self.__interval = interval
        self.__stop_flag = False

    
    def start(self) -> None:
        """
        Starts to loop the functions in a thread
        """

        self.__thread.start()

    
    def stop(self) -> None:
        """
        Stops to loop all the functions and joins the thread
        """

        self.__stop_flag = True
        self.__thread.join()

    
    @property
    def tasks(self) -> List[str]:
        """
        A list of all the functions with their execution order
        """
        
        return [fn.name for fn in self.__funcs]


    def add_task(self, fn: Callable, *args) -> None:
        """
        Appends the given function to the list of tasks to execute in loop
        """

        if len(args) > 1:
            args = list(args)

        self.__funcs.append(
            FunctionDescriptor(fn, fn.__name__, args)
        )


    def __tick(self) -> None:
        """
        Function that loops runs all the given functions in loop in a thread
        """
        
        while not self.__stop_flag:
            
            for f_desc in self.__funcs:

                try:
                    f_desc.func(*f_desc.parameters)
                except Exception as e:
                    traceback.print_exc()

            time.sleep(self.__interval)