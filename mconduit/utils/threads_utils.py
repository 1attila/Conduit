from typing import Callable, Optional, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from mconduit.plugins import Plugin


T = TypeVar("T")


def new_process(
        fn: Optional[Callable[..., T]],
        *,
        force_to_stop_after_secs: Optional[float]=None
        ) -> Callable[..., None]:
    """
    Executes the function in a new process every time it's gets called.

    Usage:

    ```
    @new_process
    def parallel_work():
        ...
    
    @new_process(force_to_stop_after_secs=10)
    def parallel_work():
        ...
    ```
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., None]:

        def _wrapped_function(*args, **kwargs) -> None:

            plugin_inst: Plugin = args[0]
            plugin_inst.run_process(
                fn,
                args=args,
                kwargs=kwargs,
                force_stop_after_secs=force_to_stop_after_secs
            )

        _wrapped_function.__name__ = fn.__name__

        return _wrapped_function
    
    if fn is None:
        return decorator

    return decorator(fn)